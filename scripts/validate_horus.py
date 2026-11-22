#!/usr/bin/env python3
"""
Integrity & configuration validator for Horus Super Agent (OpenCode v0.3+).

Checks:
1. opencode.jsonc (V2) and opencode.v1.json (V1) parse cleanly and allow the built-in `question` tool.
2. Primary agent `horus.md` explicitly allows `question`; all subagents explicitly deny `question` and `subagent`.
3. Zero hardcoded `model:` fields in any agent frontmatter (enforces interactive in-session model selection).
4. Every skill under .opencode/skills/*/SKILL.md has valid YAML frontmatter matching its directory name.
5. Every slash command under .opencode/commands/*.md has valid frontmatter and non-empty body.
6. All merged Vibe Engineering Playbook templates (4) and bilingual EN/AR reference handbooks (8) exist.
7. Bundled Python scripts (plan.py, with_server.py, sync_upstream.py) compile cleanly.
"""
from __future__ import annotations

import json
import py_compile
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

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
    "horus-init.md",
    "horus-status.md",
    "horus-resume.md",
    "horus-review.md",
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


def main() -> int:
    errors: list[str] = []

    def fail(msg: str) -> None:
        errors.append(msg)

    # 1. Validate opencode.jsonc (V2)
    jsonc_path = ROOT / "opencode.jsonc"
    if not jsonc_path.exists():
        fail("Missing opencode.jsonc")
    else:
        try:
            cfg = json.loads(strip_jsonc_comments(jsonc_path.read_text(encoding="utf-8")))
            perms = cfg.get("permissions", [])
            has_q = any(
                p.get("action") == "question" and p.get("effect") == "allow"
                for p in perms
                if isinstance(p, dict)
            )
            if not has_q:
                fail("opencode.jsonc missing { action: 'question', resource: '*', effect: 'allow' }")
            if cfg.get("default_agent") != "horus":
                fail(f"opencode.jsonc default_agent expected 'horus', got {cfg.get('default_agent')!r}")
        except Exception as exc:
            fail(f"opencode.jsonc parse error: {exc}")

    # 2. Validate opencode.v1.json (V1)
    v1_path = ROOT / "opencode.v1.json"
    if v1_path.exists():
        try:
            v1 = json.loads(v1_path.read_text(encoding="utf-8"))
            if v1.get("permission", {}).get("question") != "allow":
                fail("opencode.v1.json missing permission.question = 'allow'")
        except Exception as exc:
            fail(f"opencode.v1.json parse error: {exc}")

    # 3. Validate agents
    agents_dir = ROOT / ".opencode" / "agents"
    agent_files = sorted(agents_dir.glob("*.md"))
    if not agent_files:
        fail("No agent files found in .opencode/agents/")
    for af in agent_files:
        try:
            fm, body = split_frontmatter(af.read_text(encoding="utf-8"))
        except Exception as exc:
            fail(f"{af.name}: {exc}")
            continue
        if not body:
            fail(f"{af.name}: empty prompt body")
        if re.search(r"^model:\s*\S+", fm, re.M):
            fail(f"{af.name}: hardcoded model: found in frontmatter (must be selected in session)")
        if af.name == "horus.md":
            if not re.search(r"action:\s*question\s*\n\s*resource:\s*\"?\*\"?\s*\n\s*effect:\s*allow", fm):
                fail("horus.md must explicitly allow the `question` tool")
        else:
            if not re.search(r"action:\s*question\s*\n\s*resource:\s*\"?\*\"?\s*\n\s*effect:\s*deny", fm):
                fail(f"{af.name}: subagent must explicitly deny `question` tool")
            if not re.search(r"action:\s*subagent\s*\n\s*resource:\s*\"?\*\"?\s*\n\s*effect:\s*deny", fm):
                fail(f"{af.name}: subagent must explicitly deny `subagent` tool")

    # 4. Validate skills
    skills_dir = ROOT / ".opencode" / "skills"
    skill_dirs = sorted(p for p in skills_dir.iterdir() if p.is_dir())
    if not skill_dirs:
        fail("No skills found in .opencode/skills/")
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
        if not re.search(r"^description:\s*\S+", fm, re.M):
            fail(f"skills/{sd.name}/SKILL.md missing 'description:' field")
        if not body:
            fail(f"skills/{sd.name}/SKILL.md empty body")

    # 5. Validate commands
    cmds_dir = ROOT / ".opencode" / "commands"
    for cmd in REQUIRED_COMMANDS:
        cp = cmds_dir / cmd
        if not cp.exists():
            fail(f"Missing required command .opencode/commands/{cmd}")
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
            fail(f"Missing merged Vibe template: .opencode/skills/vibe/templates/{tpl}")
    for ref in REQUIRED_VIBE_REFS:
        if not (vibe_dir / "references" / ref).exists():
            fail(f"Missing merged Vibe reference: .opencode/skills/vibe/references/{ref}")

    # 7. Compile-check bundled Python scripts
    py_scripts = [
        ROOT / "scripts" / "sync_upstream.py",
        ROOT / "scripts" / "validate_horus.py",
        skills_dir / "planning-with-evidence" / "scripts" / "plan.py",
        skills_dir / "webapp-testing" / "scripts" / "with_server.py",
    ]
    for ps in py_scripts:
        if not ps.exists():
            fail(f"Missing script: {ps.relative_to(ROOT)}")
            continue
        try:
            py_compile.compile(str(ps), doraise=True)
        except Exception as exc:
            fail(f"Syntax error in {ps.relative_to(ROOT)}: {exc}")

    if errors:
        print(f"HORUS VALIDATION FAILED ({len(errors)} issue(s)):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(
        f"HORUS VALIDATION PASSED: "
        f"{len(agent_files)} agents, {len(skill_dirs)} skills, "
        f"{len(REQUIRED_COMMANDS)} commands, "
        f"{len(REQUIRED_VIBE_TEMPLATES)} Vibe templates, "
        f"{len(REQUIRED_VIBE_REFS)} bilingual Vibe handbooks."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
