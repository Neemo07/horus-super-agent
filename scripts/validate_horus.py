#!/usr/bin/env python3
"""
Multi-harness integrity & configuration validator for Horus Super Agent (v0.7.1+).

Supports:
  - OpenCode (V2 `opencode.jsonc` / global strict `opencode.json` / V1 `opencode.v1.json`)
  - Google Antigravity (`.agents/` + `GEMINI.md` project, or `~/.gemini/config/` global)
  - DeepSeek Harness Desktop App / Web UI (`skills/` + `.dsh/` + `AGENTS.md` project, or `$DSH_HOME/horus/` global)
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

NESTED = ROOT / ".opencode"
BASE = NESTED if NESTED.is_dir() else ROOT
LAYOUT = "project" if NESTED.is_dir() else "global"

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
    "reach.md",
    "portfolio.md",
    "modernize.md",
    "ocr-review.md",
    "design.md",
    "craft.md",
    "partner.md",
    "security.md",
    "horus-context.md",
    "horus-memory.md",
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
    lines = [ln for ln in text.splitlines() if not ln.lstrip().startswith("//")]
    cleaned = "\n".join(lines)
    return re.sub(r",\s*([}\]])", r"\1", cleaned)


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        raise ValueError("Missing opening YAML frontmatter delimiter '---'")
    parts = re.split(r"\r?\n---\r?\n", text[4:], maxsplit=1)
    if len(parts) != 2:
        raise ValueError("Missing closing YAML frontmatter delimiter '---'")
    return parts[0], parts[1].strip()


def v2_permissions(cfg: dict) -> list[dict]:
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


def find_opencode_config(root: Path) -> Path | None:
    for name in ("opencode.jsonc", "opencode.json"):
        p = root / name
        if p.exists():
            return p
    return None


def validate_skills_dir(skills_dir: Path, fail) -> list[Path]:
    if not skills_dir.is_dir():
        fail(f"Missing skills directory: {skills_dir}")
        return []
    skill_dirs = sorted(p for p in skills_dir.iterdir() if p.is_dir())
    if not skill_dirs:
        fail(f"No skills found in {skills_dir}")
        return []
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

    seen_playbooks: dict[str, list[str]] = {}
    for sub in sorted(skills_dir.rglob("SKILL.md")):
        if sub.parent.parent == skills_dir:
            continue
        seen_playbooks.setdefault(sub.parent.name, []).append(sub.relative_to(skills_dir).as_posix())
    for pname, locs in seen_playbooks.items():
        if len(locs) > 1:
            fail(f"Duplicate reference playbook name {pname!r}: {locs}")
    return skill_dirs


def validate_context_mode(cm_dir: Path, fail) -> None:
    if not cm_dir.is_dir():
        fail(f"Missing Horus Context Mode directory: {cm_dir}")
        return
    for rel in REQUIRED_CONTEXT_MODE_FILES:
        if not (cm_dir / rel).exists():
            fail(f"Missing Horus Context Mode file: {cm_dir / rel}")


def validate_python_scripts(root: Path, skills_dir: Path, fail) -> None:
    py_targets = [
        skills_dir / "planning-with-evidence" / "scripts" / "plan.py",
        skills_dir / "webapp-testing" / "scripts" / "with_server.py",
        root / "scripts" / "sync_upstream.py",
        root / "scripts" / "validate_horus.py",
        root / "scripts" / "migrate-opencode-db.py",
        root / "scripts" / "horus_foundry.py",
        root / "scripts" / "horus_todo.py",
        root / "scripts" / "install_harness.py",
    ]
    for pt in py_targets:
        if pt.exists():
            try:
                ast.parse(pt.read_text(encoding="utf-8-sig"), filename=str(pt))
            except Exception as exc:
                fail(f"Python syntax error in {pt}: {exc}")


def validate_opencode(root: Path, allow_models: bool) -> list[str]:
    errors: list[str] = []
    fail = errors.append

    nested = root / ".opencode"
    base = nested if nested.is_dir() else root
    layout = "project" if nested.is_dir() else "global"

    jsonc_path = find_opencode_config(root)
    if jsonc_path is None:
        fail(f"Missing opencode.jsonc or opencode.json in {root}")
    else:
        try:
            raw = jsonc_path.read_text(encoding="utf-8-sig")
            cfg = json.loads(raw) if jsonc_path.suffix == ".json" else json.loads(strip_jsonc_comments(raw))
            perms = v2_permissions(cfg)
            if not any(p.get("action") == "question" and p.get("effect") == "allow" for p in perms):
                fail(f"{jsonc_path.name} missing question -> allow permission")
            if cfg.get("default_agent") != "horus":
                fail(f"{jsonc_path.name} default_agent expected 'horus', got {cfg.get('default_agent')!r}")
        except Exception as exc:
            fail(f"{jsonc_path.name} parse error: {exc}")

    v1_path = root / "opencode.v1.json"
    if v1_path.exists():
        try:
            v1 = json.loads(v1_path.read_text(encoding="utf-8-sig"))
            if v1.get("permission", {}).get("question") != "allow":
                fail("opencode.v1.json missing permission.question = 'allow'")
        except Exception as exc:
            fail(f"opencode.v1.json parse error: {exc}")

    agents_dir = base / "agents"
    agent_files = sorted(agents_dir.glob("*.md")) if agents_dir.is_dir() else []
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
            if re.search(r"action:\s*edit\s*\n\s*resource:\s*\"?\*\"?\s*\n\s*effect:\s*deny", fm):
                if not re.search(r"action:\s*shell\s*\n\s*resource:\s*\"?\*\"?\s*\n\s*effect:\s*deny", fm):
                    fail(f"{af.name}: read-only subagent must explicitly deny `shell: \"*\"` baseline")

    skills_dir = base / "skills"
    skill_dirs = validate_skills_dir(skills_dir, fail)

    cmds_dir = base / "commands"
    for cmd in REQUIRED_COMMANDS:
        cp = cmds_dir / cmd
        if not cp.exists():
            fail(f"Missing required command: commands/{cmd}")
            continue
        try:
            _, body = split_frontmatter(cp.read_text(encoding="utf-8"))
            if not body:
                fail(f"commands/{cmd}: empty body")
        except Exception as exc:
            fail(f"commands/{cmd}: {exc}")

    vibe_dir = skills_dir / "vibe"
    for tpl in REQUIRED_VIBE_TEMPLATES:
        if not (vibe_dir / "templates" / tpl).exists():
            fail(f"Missing Vibe template: skills/vibe/templates/{tpl}")
    for ref in REQUIRED_VIBE_REFS:
        if not (vibe_dir / "references" / ref).exists():
            fail(f"Missing Vibe handbook: skills/vibe/references/{ref}")

    graphify_refs = skills_dir / "graphify" / "references"
    for gref in REQUIRED_GRAPHIFY_REFS:
        if not (graphify_refs / gref).exists():
            fail(f"Missing Graphify reference: skills/graphify/references/{gref}")

    validate_context_mode(base / "context-mode", fail)
    validate_python_scripts(root, skills_dir, fail)

    if not errors:
        print(
            f"HORUS VALIDATION PASSED ({layout}): "
            f"{len(agent_files)} agents, {len(skill_dirs)} skills, {len(REQUIRED_COMMANDS)} commands, "
            f"{len(REQUIRED_VIBE_TEMPLATES)} Vibe templates, {len(REQUIRED_VIBE_REFS)} bilingual Vibe handbooks, "
            f"{len(REQUIRED_GRAPHIFY_REFS)} Graphify references."
        )
    return errors


def validate_antigravity(root: Path) -> list[str]:
    errors: list[str] = []
    fail = errors.append

    nested = root / ".agents"
    base = nested if nested.is_dir() else root
    layout = "antigravity/project" if nested.is_dir() else "antigravity/global"

    skill_dirs = validate_skills_dir(base / "skills", fail)
    agents = sorted((base / "agents").glob("*.md")) if (base / "agents").is_dir() else []
    if len(agents) < 7:
        fail(f"Antigravity agents/ expected >=7 files, found {len(agents)}")

    wf_dir = base / "workflows"
    for cmd in REQUIRED_COMMANDS:
        wp = wf_dir / cmd
        if not wp.exists():
            fail(f"Missing Antigravity workflow: workflows/{cmd}")
            continue
        try:
            fm, body = split_frontmatter(wp.read_text(encoding="utf-8"))
            if "name:" not in fm or not body:
                fail(f"Invalid Antigravity workflow frontmatter/body: workflows/{cmd}")
        except Exception as exc:
            fail(f"workflows/{cmd}: {exc}")

    rule_file = base / "rules" / "horus.md"
    if not rule_file.exists():
        fail(f"Missing Antigravity rule file: {rule_file}")

    mcp_file = base / "mcp_config.json"
    if not mcp_file.exists():
        fail(f"Missing Antigravity MCP config: {mcp_file}")
    else:
        try:
            data = json.loads(mcp_file.read_text(encoding="utf-8-sig"))
            if "horus-context-mode" not in data.get("mcpServers", {}):
                fail(f"{mcp_file} missing mcpServers.horus-context-mode")
        except Exception as exc:
            fail(f"{mcp_file} parse error: {exc}")

    validate_context_mode(base / "context-mode", fail)
    validate_python_scripts(root, base / "skills", fail)

    if not errors:
        print(
            f"HORUS VALIDATION PASSED ({layout}): "
            f"{len(agents)} agents, {len(skill_dirs)} skills, {len(REQUIRED_COMMANDS)} workflows, rules/horus.md, mcp_config.json."
        )
    return errors


def validate_dsh(root: Path) -> list[str]:
    errors: list[str] = []
    fail = errors.append

    nested = root / ".dsh"
    if nested.is_dir():
        base = nested
        skills_dir = root / "skills"
        layout = "dsh/project"
    else:
        base = root
        skills_dir = root.parent / "skills"
        layout = "dsh/global"

    skill_dirs = validate_skills_dir(skills_dir, fail)
    agents = sorted((base / "agents").glob("*.md")) if (base / "agents").is_dir() else []
    if len(agents) < 7:
        fail(f"DSH agents/ expected >=7 files, found {len(agents)}")

    cmds_dir = base / "commands"
    for cmd in REQUIRED_COMMANDS:
        if not (cmds_dir / cmd).exists():
            fail(f"Missing DSH command playbook: commands/{cmd}")

    patch_file = base / "cordis.patch.yml"
    if not patch_file.exists():
        fail(f"Missing DSH Cordis MCP patch: {patch_file}")
    else:
        raw = patch_file.read_text(encoding="utf-8")
        if "@deepseek-ai/dsh-mcp-client" not in raw or "horus-context-mode" not in raw:
            fail(f"{patch_file} missing @deepseek-ai/dsh-mcp-client horus-context-mode entry")

    if not ((root / "AGENTS.md").exists() or (base / "AGENTS.md").exists()):
        fail("Missing AGENTS.md for DeepSeek Harness")

    validate_context_mode(base / "context-mode", fail)
    validate_python_scripts(root, skills_dir, fail)

    if not errors:
        print(
            f"HORUS VALIDATION PASSED ({layout}): "
            f"{len(agents)} agents, {len(skill_dirs)} skills, {len(REQUIRED_COMMANDS)} commands, cordis.patch.yml."
        )
    return errors


def detect_harnesses(root: Path) -> list[str]:
    found: list[str] = []
    if (root / ".opencode").is_dir() or find_opencode_config(root) is not None:
        found.append("opencode")
    if (root / ".agents").is_dir() or ((root / "rules" / "horus.md").exists() and (root / "workflows").is_dir()):
        found.append("antigravity")
    if (root / ".dsh").is_dir() or (root / "cordis.patch.yml").exists():
        found.append("dsh")
    return found or ["opencode"]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate Horus Super Agent installation and integrity.")
    ap.add_argument(
        "--allow-session-models",
        action="store_true",
        help="Allow local `model:` overrides in agent frontmatter (also auto-enabled when .horus/STATE.md exists).",
    )
    ap.add_argument(
        "--harness",
        choices=("auto", "opencode", "antigravity", "dsh", "all"),
        default="auto",
        help="Target harness layout to validate (default: auto-detect all installed harnesses).",
    )
    ap.add_argument(
        "--root",
        default=None,
        help="Optional target root directory to validate (default: parent of scripts/).",
    )
    args = ap.parse_args(argv)
    root = Path(args.root).resolve() if args.root else ROOT
    allow_models = args.allow_session_models or (root / ".horus" / "STATE.md").exists()

    targets = detect_harnesses(root) if args.harness == "auto" else (["opencode", "antigravity", "dsh"] if args.harness == "all" else [args.harness])

    all_errors: list[str] = []
    for h in targets:
        if h == "opencode":
            all_errors.extend(validate_opencode(root, allow_models))
        elif h == "antigravity":
            all_errors.extend(validate_antigravity(root))
        elif h == "dsh":
            all_errors.extend(validate_dsh(root))

    if all_errors:
        print("HORUS VALIDATION FAILED:", file=sys.stderr)
        for e in all_errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
