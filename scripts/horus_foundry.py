#!/usr/bin/env python3
"""
Horus Foundry — Linear-Orchestrated Parallel Background OpenCode Agents (v0.4.2).

Inspired by @leixusam/foundry (MIT), upgraded for OpenCode & Horus Super Agent:
  - Zero external dependencies (Python 3.8+ stdlib + direct Linear GraphQL API).
  - Deterministic 0-token Linear Reader/Claimer & Writer (saves 2 LLM calls/loop).
  - True parallel workers via isolated `git worktree` per ticket (--workers N).
  - Native OpenCode CLI runner (`opencode run`) inheriting Horus AGENTS.md,
    Graphify, Horus Context Mode, and plan.py evidence gates.
  - Full Linear state machine (∞ Needs Research -> Spec -> Plan -> Implement ->
    Validate -> Awaiting Merge -> Done | ∞ Blocked) + `oneshot` mode.

Environment (or .horus/foundry.env):
  LINEAR_API_KEY         Linear personal API key (required for live calls)
  LINEAR_TEAM_KEY        Linear team key, e.g. "ENG" (auto-detected if single team)
  HORUS_FOUNDRY_AGENT    OpenCode agent name (default: horus)
  HORUS_FOUNDRY_MODEL    Optional provider/model override (default: OpenCode default)
  HORUS_FOUNDRY_WORKERS  Parallel worktree workers (default: 1)
  HORUS_FOUNDRY_MODE     Workflow mode: staged | oneshot (default: staged)
  HORUS_FOUNDRY_MERGE    Merge mode: pr | merge | auto (default: pr)

Usage:
  python scripts/horus_foundry.py init-linear
  python scripts/horus_foundry.py status
  python scripts/horus_foundry.py run --workers 2 --mode staged --merge pr
  python scripts/horus_foundry.py run --once --dry-run
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# argparse prints help via stdout; on Windows cp1252 consoles a non-ASCII
# character in a help string raises UnicodeEncodeError before parsing.
# Force UTF-8 so --help works regardless of the active code page.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

LINEAR_GRAPHQL_URL = os.environ.get("LINEAR_API_URL", "https://api.linear.app/graphql")
PREFIX = "∞"

FOUNDRY_STATES = [
    {"name": f"{PREFIX} Backlog", "type": "backlog", "color": "#95a2b3"},
    {"name": f"{PREFIX} Needs Research", "type": "unstarted", "color": "#e2e2e2"},
    {"name": f"{PREFIX} Needs Specification", "type": "unstarted", "color": "#e2e2e2"},
    {"name": f"{PREFIX} Needs Plan", "type": "unstarted", "color": "#e2e2e2"},
    {"name": f"{PREFIX} Needs Implement", "type": "unstarted", "color": "#e2e2e2"},
    {"name": f"{PREFIX} Needs Validate", "type": "unstarted", "color": "#e2e2e2"},
    {"name": f"{PREFIX} Research In Progress", "type": "started", "color": "#f2c94c"},
    {"name": f"{PREFIX} Specification In Progress", "type": "started", "color": "#f2c94c"},
    {"name": f"{PREFIX} Plan In Progress", "type": "started", "color": "#f2c94c"},
    {"name": f"{PREFIX} Implement In Progress", "type": "started", "color": "#f2c94c"},
    {"name": f"{PREFIX} Validate In Progress", "type": "started", "color": "#f2c94c"},
    {"name": f"{PREFIX} Oneshot In Progress", "type": "started", "color": "#f2c94c"},
    {"name": f"{PREFIX} Blocked", "type": "started", "color": "#eb5757"},
    {"name": f"{PREFIX} Awaiting Merge", "type": "started", "color": "#5e6ad2"},
    {"name": f"{PREFIX} Done", "type": "completed", "color": "#22c55e"},
    {"name": f"{PREFIX} Canceled", "type": "canceled", "color": "#95a2b3"},
]

# Staged transitions: source_state -> (stage_key, in_progress_state, next_state_on_pass)
STAGE_TRANSITIONS = {
    f"{PREFIX} Needs Research": ("research", f"{PREFIX} Research In Progress", f"{PREFIX} Needs Plan"),
    f"{PREFIX} Needs Specification": ("spec", f"{PREFIX} Specification In Progress", f"{PREFIX} Needs Plan"),
    f"{PREFIX} Needs Plan": ("plan", f"{PREFIX} Plan In Progress", f"{PREFIX} Needs Implement"),
    f"{PREFIX} Needs Implement": ("implement", f"{PREFIX} Implement In Progress", f"{PREFIX} Needs Validate"),
    f"{PREFIX} Needs Validate": ("validate", f"{PREFIX} Validate In Progress", f"{PREFIX} Done"),
}

STAGE_INSTRUCTIONS = {
    "research": (
        "STAGE: RESEARCH. Map the affected codebase using `graphify query` (if graphify-out/graph.json exists) "
        "or targeted reads. Write a concise evidence-backed research brief to `foundry-docs/research/{key}.md` "
        "citing exact `file:line` references. Do NOT modify production code."
    ),
    "spec": (
        "STAGE: SPECIFICATION. Write a concrete PRD/UX specification with acceptance criteria and edge cases "
        "to `foundry-docs/specs/{key}.md`. Do NOT modify production code."
    ),
    "plan": (
        "STAGE: PLAN. Convert the ticket + research brief into an executable phased plan in "
        "`foundry-docs/plans/{key}.md` with exact target files, invariants, and verification commands."
    ),
    "implement": (
        "STAGE: IMPLEMENT. Implement the ticket cleanly following `AGENTS.md` (zero noisy code, TDD where applicable). "
        "Run the project's build/test suite and commit your verified changes to this branch."
    ),
    "validate": (
        "STAGE: VALIDATE. Run the full test suite, linter, and adversarial read-only review against the ticket's "
        "acceptance criteria. Write a terse proof report to `foundry-docs/validation/{key}.md`."
    ),
    "oneshot": (
        "STAGE: ONESHOT. Research, implement, verify with tests/build, and commit clean changes for this ticket "
        "in one focused pass following `AGENTS.md`."
    ),
}


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_env_file(repo_root: Path) -> None:
    """Load key=value pairs from .horus/foundry.env (or legacy .foundry/env) without overriding existing env."""
    for rel in (".horus/foundry.env", ".foundry/env"):
        env_path = repo_root / rel
        if not env_path.is_file():
            continue
        for raw in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v


class LinearAPI:
    """Minimal zero-dependency Linear GraphQL client."""

    def __init__(self, api_key: str, endpoint: str | None = None) -> None:
        self.api_key = api_key
        self.endpoint = endpoint or LINEAR_GRAPHQL_URL

    def query(self, gql: str, variables: dict | None = None) -> dict:
        payload = json.dumps({"query": gql, "variables": variables or {}}).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": self.api_key,
                "User-Agent": "horus-foundry/0.4.2",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:300]
            raise RuntimeError(f"Linear HTTP {exc.code}: {detail}") from exc
        if body.get("errors"):
            raise RuntimeError(f"Linear GraphQL error: {body['errors']}")
        return body.get("data", {})

    def resolve_team(self, team_key: str | None = None) -> dict:
        data = self.query("query { teams { nodes { id key name } } }")
        teams = data.get("teams", {}).get("nodes", [])
        if not teams:
            raise RuntimeError("No Linear teams accessible with this LINEAR_API_KEY.")
        if team_key:
            for t in teams:
                if t["key"].lower() == team_key.lower():
                    return t
            known = ", ".join(t["key"] for t in teams)
            raise RuntimeError(f"Linear team {team_key!r} not found. Available: {known}")
        if len(teams) == 1:
            return teams[0]
        known = ", ".join(t["key"] for t in teams)
        raise RuntimeError(f"Multiple Linear teams found ({known}); set LINEAR_TEAM_KEY or --team.")

    def list_states(self, team_id: str) -> dict[str, dict]:
        data = self.query(
            """
            query($teamId: String!) {
              team(id: $teamId) {
                states { nodes { id name type position } }
              }
            }
            """,
            {"teamId": team_id},
        )
        nodes = data.get("team", {}).get("states", {}).get("nodes", [])
        return {s["name"]: s for s in nodes}

    def ensure_states(self, team_id: str) -> tuple[list[str], list[str]]:
        existing = self.list_states(team_id)
        created, kept = [], []
        for st in FOUNDRY_STATES:
            if st["name"] in existing:
                kept.append(st["name"])
                continue
            self.query(
                """
                mutation($input: WorkflowStateCreateInput!) {
                  workflowStateCreate(input: $input) {
                    success
                    workflowState { id name }
                  }
                }
                """,
                {"input": {"teamId": team_id, "name": st["name"], "type": st["type"], "color": st["color"]}},
            )
            created.append(st["name"])
        return created, kept

    def list_candidate_issues(self, team_id: str, mode: str) -> list[dict]:
        """Fetch issues ready for Horus Foundry, sorted by Linear priority (1=Urgent .. 4=Low, 0=None last)."""
        data = self.query(
            """
            query($teamId: ID!) {
              issues(
                filter: { team: { id: { eq: $teamId } }, state: { type: { nin: ["completed", "canceled"] } } }
                first: 50
              ) {
                nodes {
                  id identifier title description priority url
                  state { id name type }
                  labels { nodes { name } }
                }
              }
            }
            """,
            {"teamId": team_id},
        )
        nodes = data.get("issues", {}).get("nodes", [])
        if mode == "oneshot":
            allowed = set(STAGE_TRANSITIONS.keys()) | {"Todo", f"{PREFIX} Backlog"}
        else:
            allowed = set(STAGE_TRANSITIONS.keys())
        ready = [iss for iss in nodes if iss.get("state", {}).get("name") in allowed]
        # Priority 1 (Urgent) first, 0 (No priority) last
        ready.sort(key=lambda i: (i.get("priority") or 99, i.get("identifier", "")))
        return ready

    def update_issue_state(self, issue_id: str, state_id: str) -> None:
        self.query(
            """
            mutation($id: String!, $stateId: String!) {
              issueUpdate(id: $id, input: { stateId: $stateId }) { success }
            }
            """,
            {"id": issue_id, "stateId": state_id},
        )

    def add_comment(self, issue_id: str, body: str) -> None:
        self.query(
            """
            mutation($issueId: String!, $body: String!) {
              commentCreate(input: { issueId: $issueId, body: $body }) { success }
            }
            """,
            {"issueId": issue_id, "body": body},
        )


def slugify(text: str, max_len: int = 36) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return (s[:max_len].rstrip("-")) or "task"


def find_runner_cli(runner: str = "opencode") -> str:
    env_map = {
        "opencode": ("OPENCODE_BIN", ("opencode", "opencode.exe", "opencode.cmd")),
        "antigravity": ("ANTIGRAVITY_BIN", ("agy", "agy.exe", "agy.cmd")),
        "dsh": ("DSH_BIN", ("dsh", "dsh.exe", "dsh.cmd")),
    }
    if runner not in env_map:
        raise RuntimeError(f"Unsupported runner {runner!r} (expected: opencode, antigravity, dsh)")
    env_var, names = env_map[runner]
    override = os.environ.get(env_var)
    if override and os.path.exists(override):
        return override
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    raise RuntimeError(f"`{names[0]}` CLI not found on PATH. Install {runner} or set {env_var}.")


def ensure_worktree(repo_root: Path, branch: str, wt_path: Path) -> Path:
    wt_path.parent.mkdir(parents=True, exist_ok=True)
    if wt_path.exists():
        return wt_path
    # Check if branch exists locally
    chk = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
        cwd=str(repo_root),
    )
    if chk.returncode == 0:
        cmd = ["git", "worktree", "add", str(wt_path), branch]
    else:
        cmd = ["git", "worktree", "add", "-b", branch, str(wt_path)]
    r = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git worktree add failed: {r.stderr.strip()}")
    return wt_path


def build_worker_prompt(issue: dict, stage: str, branch: str, merge_mode: str) -> str:
    key = issue["identifier"]
    title = issue.get("title", "")
    desc = (issue.get("description") or "(no description)").strip()
    url = issue.get("url", "")
    stage_note = STAGE_INSTRUCTIONS[stage].format(key=key)
    return (
        f"You are a Horus Foundry background OpenCode worker on isolated git worktree branch `{branch}`.\n"
        f"Linear Ticket: **{key}** — {title}\n"
        f"URL: {url}\n"
        f"Merge Mode: `{merge_mode}`\n\n"
        f"## Ticket Description\n{desc}\n\n"
        f"## Stage Directive\n{stage_note}\n\n"
        f"## Output Contract\n"
        f"Follow `AGENTS.md`. Do NOT call interactive `question` polls (you are running unattended in background mode). "
        f"If blocked by missing credentials or ambiguous requirements, output a line starting with `FOUNDRY_BLOCKED: <reason>` and exit non-zero. "
        f"Otherwise finish cleanly and summarize exact changed files and verification command exit codes."
    )


def run_worker(
    wt_path: Path,
    prompt: str,
    agent: str,
    model: str | None,
    timeout: int,
    log_path: Path,
    runner: str = "opencode",
    variant: str | None = None,
) -> tuple[int, str]:
    cli = find_runner_cli(runner)
    if runner == "opencode":
        cmd = [cli, "run", "--agent", agent]
        if model:
            cmd += ["--model", model]
        if variant:
            cmd += ["--variant", variant]
        cmd.append(prompt)
    elif runner == "antigravity":
        cmd = [cli, "run"]
        if model:
            cmd += ["--model", model]
        cmd.append(prompt)
    else:
        cmd = [cli, "run", prompt]
    try:
        r = subprocess.run(
            cmd,
            cwd=str(wt_path),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        combined = (r.stdout or "") + ("\n--- STDERR ---\n" + r.stderr if r.stderr else "")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(combined, encoding="utf-8", errors="replace")
        return r.returncode, combined
    except subprocess.TimeoutExpired:
        msg = f"FOUNDRY_BLOCKED: OpenCode worker timed out after {timeout}s"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(msg, encoding="utf-8")
        return 124, msg


def process_ticket(
    api: LinearAPI,
    states: dict[str, dict],
    repo_root: Path,
    issue: dict,
    mode: str,
    merge_mode: str,
    agent: str,
    model: str | None,
    timeout: int,
    dry_run: bool,
    runner: str = "opencode",
    variant: str | None = None,
) -> dict:
    key = issue["identifier"]
    cur_state = issue["state"]["name"]
    if mode == "oneshot":
        stage = "oneshot"
        in_prog = f"{PREFIX} Oneshot In Progress"
        next_state = f"{PREFIX} Awaiting Merge" if merge_mode == "pr" else f"{PREFIX} Done"
    else:
        stage, in_prog, next_state = STAGE_TRANSITIONS[cur_state]
        if stage == "validate" and merge_mode == "pr":
            next_state = f"{PREFIX} Awaiting Merge"

    branch = f"horus/{key.lower()}-{slugify(issue.get('title', ''))}"
    wt_path = repo_root / ".horus" / "foundry" / "worktrees" / key
    log_path = repo_root / ".horus" / "foundry" / "logs" / f"{key}-{stage}-{int(time.time())}.log"

    if dry_run:
        return {
            "issue": key,
            "stage": stage,
            "from": cur_state,
            "claim": in_prog,
            "next": next_state,
            "branch": branch,
            "worktree": str(wt_path),
            "status": "DRY_RUN",
        }

    # 1. Atomically claim ticket in Linear (0 LLM tokens)
    if in_prog in states:
        api.update_issue_state(issue["id"], states[in_prog]["id"])
    api.add_comment(
        issue["id"],
        f"**Horus Foundry** claimed `{key}` for stage **`{stage}`** on branch `{branch}` ({now_iso()}).",
    )

    # 2. Prepare isolated git worktree
    ensure_worktree(repo_root, branch, wt_path)

    # 3. Run OpenCode worker
    prompt = build_worker_prompt(issue, stage, branch, merge_mode)
    code, out = run_worker(wt_path, prompt, agent, model, timeout, log_path, runner=runner, variant=variant)

    # 4. Advance or block ticket in Linear (0 LLM tokens)
    blocked_match = re.search(r"FOUNDRY_BLOCKED:\s*(.+)", out)
    if code != 0 or blocked_match:
        reason = blocked_match.group(1).strip() if blocked_match else f"worker exited {code}"
        tail = "\n".join(out.splitlines()[-12:])
        if f"{PREFIX} Blocked" in states:
            api.update_issue_state(issue["id"], states[f"{PREFIX} Blocked"]["id"])
        api.add_comment(
            issue["id"],
            f"**Horus Foundry BLOCKED** on stage `{stage}`: {reason}\n\n```\n{tail}\n```\nLog: `{log_path.name}`",
        )
        return {"issue": key, "stage": stage, "status": "BLOCKED", "reason": reason, "log": str(log_path)}

    if next_state in states:
        api.update_issue_state(issue["id"], states[next_state]["id"])
    summary_tail = "\n".join(out.splitlines()[-15:])
    api.add_comment(
        issue["id"],
        f"**Horus Foundry** completed stage **`{stage}`** → `{next_state}` on branch `{branch}`.\n\n{summary_tail}",
    )
    return {"issue": key, "stage": stage, "status": "DONE", "next": next_state, "branch": branch, "log": str(log_path)}



LOOP_PRESETS: dict[str, str] = {
    "default": (
        "Complete ONE ready task from task_plan.md (`plan.py next`) or .taskmaster/tasks/tasks.json. "
        "Follow the 4-Line Pre-Edit Contract, run deterministic tests, record proof via `plan.py done <id> --run`, "
        "append a 1-line summary to {progress_file}, and stop. Emit <loop-complete>ALL_DONE</loop-complete> if no pending tasks remain, "
        "or <loop-blocked>REASON</loop-blocked> if blocked."
    ),
    "test-coverage": (
        "Find ONE critical untested user-facing or unhappy-path behavior, write a non-tautological test (verify it fails if logic is stubbed), "
        "run the suite, append coverage/test notes to {progress_file}, and emit <loop-complete>TARGET_MET</loop-complete> when done."
    ),
    "linting": (
        "Run the project linter and typechecker, fix ONE high-priority type/security/lint error with minimal diff, re-verify green, "
        "and log remaining error count to {progress_file}. Emit <loop-complete>ZERO_ERRORS</loop-complete> when clean."
    ),
    "duplication": (
        "Identify ONE high-impact duplicated code block, extract a clean shared utility preserving all callers (`graphify query`), "
        "re-run tests, and log the refactor to {progress_file}. Emit <loop-complete>CLEAN</loop-complete> when no major clones remain."
    ),
    "entropy": (
        "Find ONE high-risk code smell (>60-line function, >3-level nesting, magic numbers, or god module), refactor minimally with passing tests, "
        "and log the cleanup to {progress_file}. Emit <loop-complete>CLEAN</loop-complete> when done."
    ),
}


def run_local_loop(
    repo_root: Path,
    preset: str,
    prompt_file: str | None,
    iterations: int,
    sleep_seconds: int,
    progress_file: str,
    runner: str,
    agent: str,
    model: str | None,
    variant: str | None,
    timeout: int,
    dry_run: bool,
) -> int:
    """Fresh-context autonomous loop (TaskMasterProMax Ralph pattern, upgraded for OpenCode/Antigravity/DSH)."""
    prog_path = (repo_root / progress_file).resolve()
    if prompt_file:
        pf = Path(prompt_file)
        if not pf.is_file():
            print(f"ERROR: --prompt-file not found: {pf}", file=sys.stderr)
            return 1
        base_prompt = pf.read_text(encoding="utf-8")
    else:
        base_prompt = LOOP_PRESETS[preset].format(progress_file=progress_file)

    if dry_run:
        print(json.dumps({
            "mode": "loop",
            "preset": preset,
            "iterations": iterations,
            "runner": runner,
            "agent": agent,
            "variant": variant,
            "progress_file": str(prog_path),
            "dry_run": True,
        }))
        return 0

    prog_path.parent.mkdir(parents=True, exist_ok=True)
    if not prog_path.exists():
        prog_path.write_text(f"# Horus Loop Progress\n# Preset: {preset} | Runner: {runner}\n\n", encoding="utf-8")

    logs_dir = repo_root / ".horus" / "foundry" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    for i in range(1, iterations + 1):
        prompt = (
            f"Iteration {i}/{iterations} (fresh context). Progress log: {progress_file}.\n"
            f"Read the tail of {progress_file} before acting so you never repeat completed work.\n\n"
            f"{base_prompt}"
        )
        log_path = logs_dir / f"loop-{preset}-iter{i}.log"
        code, out = run_worker(repo_root, prompt, agent, model, timeout, log_path, runner=runner, variant=variant)
        print(json.dumps({"iteration": i, "exit_code": code, "log": str(log_path)}))
        if "<loop-complete>" in out:
            print(f"Loop completed early at iteration {i}.")
            return 0
        if "<loop-blocked>" in out:
            print(f"Loop blocked at iteration {i}; see {log_path}.", file=sys.stderr)
            return 2
        if i < iterations and sleep_seconds > 0:
            time.sleep(sleep_seconds)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Horus Foundry — Linear-orchestrated parallel OpenCode background agents.")
    ap.add_argument("--dir", default=".", help="Project repository directory (default: current)")
    ap.add_argument("--team", default=None, help="Linear team key (default: LINEAR_TEAM_KEY or auto-detect)")
    sp = ap.add_subparsers(dest="cmd", required=True)

    sp.add_parser("init-linear", help="Create missing ∞ Foundry workflow states in Linear")
    sp.add_parser("status", help="List ready/in-progress Linear tickets and local worktrees")

    p_run = sp.add_parser("run", help="Run parallel background OpenCode workers against Linear")
    p_run.add_argument("--workers", type=int, default=None, help="Parallel git worktree workers (default: 1)")
    p_run.add_argument("--mode", choices=("staged", "oneshot"), default=None)
    p_run.add_argument("--merge", choices=("pr", "merge", "auto"), default=None)
    p_run.add_argument("--runner", choices=("opencode", "antigravity", "dsh"), default=None, help="CLI harness runner (default: opencode)")
    p_run.add_argument("--agent", default=None, help="Agent name (default: horus)")
    p_run.add_argument("--model", default=None, help="Optional provider/model override")
    p_run.add_argument("--variant", default=None, help="Optional reasoning effort variant (e.g. high, xhigh, max)")
    p_run.add_argument("--poll-seconds", type=int, default=60, help="Sleep interval when no tickets ready")
    p_run.add_argument("--timeout", type=int, default=1800, help="Per-ticket worker timeout in seconds")
    p_run.add_argument("--once", action="store_true", help="Process one wave and exit")
    p_run.add_argument("--dry-run", action="store_true", help="Plan claims without mutating Linear or running OpenCode")


    p_loop = sp.add_parser("loop", help="Run fresh-context autonomous loop locally (no Linear key required)")
    p_loop.add_argument("--preset", choices=tuple(LOOP_PRESETS.keys()), default="default", help="Loop preset (default, test-coverage, linting, duplication, entropy)")
    p_loop.add_argument("--prompt-file", default=None, help="Optional custom prompt file overriding --preset")
    p_loop.add_argument("-n", "--iterations", type=int, default=5, help="Max fresh-context iterations (default: 5)")
    p_loop.add_argument("--sleep", type=int, default=2, help="Seconds between iterations (default: 2)")
    p_loop.add_argument("--progress-file", default=".horus/loop-progress.txt", help="Progress log path")
    p_loop.add_argument("--runner", choices=("opencode", "antigravity", "dsh"), default=None, help="CLI harness runner (default: opencode)")
    p_loop.add_argument("--agent", default=None, help="Agent name (default: horus)")
    p_loop.add_argument("--model", default=None, help="Optional provider/model override")
    p_loop.add_argument("--variant", default=None, help="Optional reasoning effort variant (e.g. high)")
    p_loop.add_argument("--timeout", type=int, default=1800, help="Per-iteration timeout in seconds")
    p_loop.add_argument("--dry-run", action="store_true", help="Print resolved loop configuration without executing")

    args = ap.parse_args(argv)
    repo_root = Path(args.dir).resolve()
    load_env_file(repo_root)

    if args.cmd == "loop":
        return run_local_loop(
            repo_root=repo_root,
            preset=args.preset,
            prompt_file=args.prompt_file,
            iterations=max(1, args.iterations),
            sleep_seconds=max(0, args.sleep),
            progress_file=args.progress_file,
            runner=args.runner or os.environ.get("HORUS_FOUNDRY_RUNNER", "opencode"),
            agent=args.agent or os.environ.get("HORUS_FOUNDRY_AGENT", "horus"),
            model=args.model or os.environ.get("HORUS_FOUNDRY_MODEL") or None,
            variant=args.variant or os.environ.get("HORUS_FOUNDRY_VARIANT") or None,
            timeout=args.timeout,
            dry_run=args.dry_run,
        )

    api_key = os.environ.get("LINEAR_API_KEY", "").strip()
    if not api_key:
        print("ERROR: LINEAR_API_KEY not set. Export it or add it to .horus/foundry.env.", file=sys.stderr)
        return 1

    api = LinearAPI(api_key)
    team = api.resolve_team(args.team or os.environ.get("LINEAR_TEAM_KEY"))

    if args.cmd == "init-linear":
        created, kept = api.ensure_states(team["id"])
        print(f"Team {team['key']} ({team['name']}): {len(created)} created, {len(kept)} already existed.")
        for name in created:
            print(f"  + {name}")
        return 0

    states = api.list_states(team["id"])
    mode = getattr(args, "mode", None) or os.environ.get("HORUS_FOUNDRY_MODE", "staged")

    if args.cmd == "status":
        issues = api.list_candidate_issues(team["id"], mode)
        print(f"Horus Foundry Status — Team {team['key']} ({mode} mode): {len(issues)} ready ticket(s)")
        for iss in issues:
            print(f"  [{iss['identifier']}] P{iss.get('priority', 0)} | {iss['state']['name']} | {iss['title']}")
        wt_root = repo_root / ".horus" / "foundry" / "worktrees"
        if wt_root.is_dir():
            wts = sorted(p.name for p in wt_root.iterdir() if p.is_dir())
            print(f"Active worktrees ({len(wts)}): {', '.join(wts) or 'none'}")
        return 0

    workers = max(1, args.workers or int(os.environ.get("HORUS_FOUNDRY_WORKERS", "1")))
    merge_mode = args.merge or os.environ.get("HORUS_FOUNDRY_MERGE", "pr")
    runner = args.runner or os.environ.get("HORUS_FOUNDRY_RUNNER", "opencode")
    agent = args.agent or os.environ.get("HORUS_FOUNDRY_AGENT", "horus")
    model = args.model or os.environ.get("HORUS_FOUNDRY_MODEL") or None
    variant = args.variant or os.environ.get("HORUS_FOUNDRY_VARIANT") or None

    while True:
        issues = api.list_candidate_issues(team["id"], mode)
        batch = issues[:workers]
        if not batch:
            print(f"[{now_iso()}] No ready tickets in team {team['key']}.")
            if args.once:
                return 0
            time.sleep(args.poll_seconds)
            continue

        print(f"[{now_iso()}] Dispatching {len(batch)} ticket(s) across {workers} worker(s) ({mode} / {merge_mode})...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            futs = [
                pool.submit(
                    process_ticket,
                    api,
                    states,
                    repo_root,
                    iss,
                    mode,
                    merge_mode,
                    agent,
                    model,
                    args.timeout,
                    args.dry_run,
                    runner,
                    variant,
                )
                for iss in batch
            ]
            for fut in concurrent.futures.as_completed(futs):
                res = fut.result()
                print(json.dumps(res))

        if args.once:
            return 0
        time.sleep(5)


if __name__ == "__main__":
    sys.exit(main())
