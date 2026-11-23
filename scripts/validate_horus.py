#!/usr/bin/env python3
"""
Integrity & configuration validator for Horus Super Agent (OpenCode v0.5.0+).

Checks:
1. opencode.jsonc (V2) / opencode.json (global or V1) and opencode.v1.json parse cleanly and allow `question`.
2. Primary agent `horus.md` explicitly allows `question`; all subagents explicitly deny `question` and `subagent`.
3. Read-only subagents (`edit: deny`) explicitly deny `shell: "*"` before narrow command allowlists.
4. Zero hardcoded `model:` fields in clean repo templates (auto-relaxed when `.horus/STATE.md` exists or `--allow-session-models` is passed).
5. Every skill under .opencode/skills/*/SKILL.md has valid YAML frontmatter matching its directory name.
6. Every slash command under .opencode/commands/*.md has valid frontmatter and non-empty body.
7. All merged Vibe Engineering Playbook templates (4) and bilingual EN/AR reference handbooks (8) exist.
8. Bundled Python scripts (plan.py, with_server.py, sync_upstream.py, validate_horus.py, migrate-opencode-db.py) parse cleanly in memory (no __pycache__ pollution).
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Support both layouts:
#   project install: <root>/.opencode/{agents,skills,commands} + <root>/opencode.jsonc
#   global install:  <config>/{agents,skills,commands}        + <config>/opencode.json
NESTED = ROOT / ".opencode"
BASE = NESTED if NESTED.is_dir() else ROOT
LAYOUT = "project" if NESTED.is_dir() else "global"


def find_config() -> Path | None:
    for name in ("opencode.jsonc", "opencode.json"):
        p = ROOT / name
        if p.exists():
            return p
    return None


def v2_permissions(cfg: dict) -> list[dict]:
    """V2 uses a `permissions` array; V1 uses a `permission` map."""
    perms = cfg.get("permissions")
    if isinstance(perms, list):
        return [p for p in perms if isinstance(p, dict)]
    legacy = cfg.get("permission")
    if isinstance(legacy, dict):
        return [
            {"action": k, "resource": "*", "effect": v}
            for k, v in legacy.items()
            if isinstance(v, str)
        ]
    return []


REQUIRED_VIBE_TEMPLATES = [
    "AGENTS.template.md",
    "AGENTS.template.ar.md",
    "PRD.template.md",
    "IMPLEMENTATION_PLAN.template.md",
]

REQUIRED_VIBE_REFS = [
    "workflow-7-stages.en.md",
    "workflow-7-stages.ar.md",
    "checklists.en.md",
    "checklists.ar.md",
    "anti-patterns.en.md",
    "anti-patterns.ar.md",
    "prompt-blueprints.en.md",
    "prompt-blueprints.ar.md",
]

REQUIRED_COMMANDS = [
    "vibe.md",
    "graphify.md",
    "design.md",
    "craft.md",
    "security.md",
    "horus-context.md",
    "horus-foundry.md",
    "horus-todo.md",
    "horus-init.md",
    "horus-status.md",
    "horus-resume.md",
    "horus-review.md",
]

REQUIRED_CONTEXT_MODE_FILES = [
    "package.json",
    "server.js",
    "lib/store.js",
    "lib/chunker.js",
    "lib/executor.js",
    "lib/tools.js",
    "dashboard/server.mjs",
    "dashboard/index.html",
]

REQUIRED_GRAPHIFY_REFS = [
    "add-watch.md",
    "exports.md",
    "extraction-spec.md",
    "github-and-merge.md",
    "hooks.md",
    "query.md",
    "transcribe.md",
    "update.md",
]


def strip_jsonc_comments(text: str) -> str:
    # Remove full-line // comments and trailing commas for strict stdlib json parsing
    lines = [ln for ln in text.splitlines() if not ln.lstrip().startswith("//")]
    cleaned = "\n".join(lines)
    cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)
    return cleaned


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        raise ValueError("Missing opening YAML frontmatter delimiter '---'")
    parts = re.split(r"\r?\n---\r?\n", text[4:], maxsplit=1)
    if len(parts) != 2:
        raise ValueError("Missing closing YAML frontmatter delimiter '---'")
    return parts[0], parts[1].strip()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate Horus Super Agent installation and integrity.")
    ap.add_argument(
        "--allow-session-models",
        action="store_true",
        help="Allow local `model:` overrides in agent frontmatter (also auto-enabled when .horus/STATE.md exists).",
    )
    args = ap.parse_args(argv)
    allow_models = args.allow_session_models or (ROOT / ".horus" / "STATE.md").exists()

    errors: list[str] = []

    def fail(msg: str) -> None:
        errors.append(msg)

    # 1. Validate the active config (V2 `permissions` array or V1 `permission` map)
    jsonc_path = find_config()
    if jsonc_path is None:
        fail(f"Missing opencode.jsonc or opencode.json in {ROOT}")
    else:
        try:
            raw = jsonc_path.read_text(encoding="utf-8-sig")
            # Strict JSON check when file extension is .json (no // comments allowed)
            if jsonc_path.suffix == ".json":
                cfg = json.loads(raw)
            else:
                cfg = json.loads(strip_jsonc_comments(raw))
            perms = v2_permissions(cfg)
            has_q = any(
                p.get("action") == "question" and p.get("effect") == "allow"
                for p in perms
            )
            if not has_q:
                fail(f"{jsonc_path.name} missing question -> allow permission")
            if cfg.get("default_agent") != "horus":
                fail(f"{jsonc_path.name} default_agent expected 'horus', got {cfg.get('default_agent')!r}")
        except Exception as exc:
            fail(f"{jsonc_path.name} parse error: {exc}")

    # 2. Validate opencode.v1.json (V1 reference config), if shipped
    v1_path = ROOT / "opencode.v1.json"
    if v1_path.exists():
        try:
            v1 = json.loads(v1_path.read_text(encoding="utf-8-sig"))
            if v1.get("permission", {}).get("question") != "allow":
                fail("opencode.v1.json missing permission.question = 'allow'")
        except Exception as exc:
            fail(f"opencode.v1.json parse error: {exc}")

    # 3. Validate agents
    agents_dir = BASE / "agents"
    agent_files = sorted(agents_dir.glob("*.md"))
    if not agent_files:
        fail("No agent files found in agents/")
    for af in agent_files:
        try:
            fm, body = split_frontmatter(af.read_text(encoding="utf-8"))
        except Exception as exc:
            fail(f"{af.name}: {exc}")
            continue
        if not body:
            fail(f"{af.name}: empty prompt body")
        if not allow_models and re.search(r"^model:\s*\S+", fm, re.M):
            fail(f"{af.name}: hardcoded model: found in frontmatter (must be selected in session)")
        if af.name == "horus.md":
            if not re.search(r"action:\s*question\s*\n\s*resource:\s*\"?\*\"?\s*\n\s*effect:\s*allow", fm):
                fail("horus.md must explicitly allow the `question` tool")
        else:
            if not re.search(r"action:\s*question\s*\n\s*resource:\s*\"?\*\"?\s*\n\s*effect:\s*deny", fm):
                fail(f"{af.name}: subagent must explicitly deny `question` tool")
            if not re.search(r"action:\s*subagent\s*\n\s*resource:\s*\"?\*\"?\s*\n\s*effect:\s*deny", fm):
                fail(f"{af.name}: subagent must explicitly deny `subagent` tool")
            # Read-only subagents (edit: deny) must also explicitly deny shell: "*"
            if re.search(r"action:\s*edit\s*\n\s*resource:\s*\"?\*\"?\s*\n\s*effect:\s*deny", fm):
                if not re.search(r"action:\s*shell\s*\n\s*resource:\s*\"?\*\"?\s*\n\s*effect:\s*deny", fm):
                    fail(f"{af.name}: read-only subagent must explicitly deny `shell: \"*\"` baseline")

    # 4. Validate skills
    skills_dir = BASE / "skills"
    skill_dirs = sorted(p for p in skills_dir.iterdir() if p.is_dir())
    if not skill_dirs:
        fail("No skills found in skills/")
    for sd in skill_dirs:
        sm = sd / "SKILL.md"
        if not sm.exists():
            fail(f"Skill directory {sd.name} missing SKILL.md")
            continue
        try:
            fm, body = split_frontmatter(sm.read_text(encoding="utf-8"))
        except Exception as exc:
            fail(f"skills/{sd.name}/SKILL.md: {exc}")
            continue
        m = re.search(r"^name:\s*['\"]?([^'\"\r\n]+?)['\"]?\s*$", fm, re.M)
        if not m:
            fail(f"skills/{sd.name}/SKILL.md missing 'name:' field")
        elif m.group(1) != sd.name:
            fail(f"skills/{sd.name}/SKILL.md name {m.group(1)!r} != dir name {sd.name!r}")
        dm = re.search(r"^description:\s*['\"]?([^\r\n]+?)['\"]?\s*$", fm, re.M)
        if not dm:
            fail(f"skills/{sd.name}/SKILL.md missing 'description:' field")
        elif len(dm.group(1).strip().strip('"').strip("'")) > 150:
            fail(f"skills/{sd.name}/SKILL.md description exceeds 150-char catalog budget ({len(dm.group(1))} chars)")
        if not body:
            fail(f"skills/{sd.name}/SKILL.md empty body")

    # 4b. Verify zero duplicate sub-playbook directory names across progressive-disclosure references
    seen_playbooks: dict[str, list[str]] = {}
    for sub in sorted(skills_dir.rglob("SKILL.md")):
        if sub.parent.parent == skills_dir:
            continue
        seen_playbooks.setdefault(sub.parent.name, []).append(sub.relative_to(skills_dir).as_posix())
    for pname, locs in seen_playbooks.items():
        if len(locs) > 1:
            fail(f"Duplicate reference playbook name {pname!r}: {locs}")

    # 5. Validate commands
    cmds_dir = BASE / "commands"
    for cmd in REQUIRED_COMMANDS:
        cp = cmds_dir / cmd
        if not cp.exists():
            fail(f"Missing required command commands/{cmd}")
            continue
        try:
            fm, body = split_frontmatter(cp.read_text(encoding="utf-8"))
            if not re.search(r"^description:\s*\S+", fm, re.M):
                fail(f"commands/{cmd}: missing description")
            if not body:
                fail(f"commands/{cmd}: empty body")
        except Exception as exc:
            fail(f"commands/{cmd}: {exc}")

    # 6. Validate merged Vibe Engineering Playbook templates & bilingual handbooks
    vibe_dir = skills_dir / "vibe"
    for tpl in REQUIRED_VIBE_TEMPLATES:
        if not (vibe_dir / "templates" / tpl).exists():
            fail(f"Missing merged Vibe template: skills/vibe/templates/{tpl}")
    for ref in REQUIRED_VIBE_REFS:
        if not (vibe_dir / "references" / ref).exists():
            fail(f"Missing merged Vibe reference: skills/vibe/references/{ref}")

    # 6b. Validate official Graphify v0.9.115 OpenCode references
    graphify_dir = skills_dir / "graphify"
    for ref in REQUIRED_GRAPHIFY_REFS:
        if not (graphify_dir / "references" / ref).exists():
            fail(f"Missing official Graphify reference: skills/graphify/references/{ref}")

    # 6c. Validate Horus Context Mode MCP bundle
    ctx_dir = BASE / "context-mode"
    for rel in REQUIRED_CONTEXT_MODE_FILES:
        if not (ctx_dir / rel).exists():
            fail(f"Missing Horus Context Mode runtime file: context-mode/{rel}")

    # 7. Syntax-check bundled Python scripts in memory (zero __pycache__ pollution)
    scripts_dir = ROOT / "scripts"
    if not (scripts_dir / "validate_horus.py").exists():
        scripts_dir = BASE / "scripts"
    py_scripts = [
        scripts_dir / "sync_upstream.py",
        scripts_dir / "validate_horus.py",
        scripts_dir / "migrate-opencode-db.py",
        scripts_dir / "horus_foundry.py",
        scripts_dir / "horus_todo.py",
        skills_dir / "planning-with-evidence" / "scripts" / "plan.py",
        skills_dir / "webapp-testing" / "scripts" / "with_server.py",
    ]
    for ps in py_scripts:
        if not ps.exists():
            fail(f"Missing script: {ps}")
            continue
        try:
            ast.parse(ps.read_text(encoding="utf-8"), filename=str(ps))
        except Exception as exc:
            fail(f"Syntax error in {ps}: {exc}")

    if errors:
        print(f"HORUS VALIDATION FAILED ({len(errors)} issue(s)):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(
        f"HORUS VALIDATION PASSED ({LAYOUT}): "
        f"{len(agent_files)} agents, {len(skill_dirs)} skills, "
        f"{len(REQUIRED_COMMANDS)} commands, "
        f"{len(REQUIRED_VIBE_TEMPLATES)} Vibe templates, "
        f"{len(REQUIRED_VIBE_REFS)} bilingual Vibe handbooks, "
        f"{len(REQUIRED_GRAPHIFY_REFS)} Graphify references."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
