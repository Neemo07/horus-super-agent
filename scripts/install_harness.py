#!/usr/bin/env python3
"""
Multi-harness adapter installer for Horus Super Agent v0.7.0.

Installs Horus from its single canonical `.opencode/` source of truth into:
  - Google Antigravity (IDE & `agy` CLI): `.agents/{skills,workflows,rules,agents,context-mode}` + `GEMINI.md` + `mcp_config.json`
    (or `~/.gemini/config/{skills,workflows,rules,agents,context-mode}` + non-destructive `mcp_config.json` merge in global mode)
  - DeepSeek Harness Desktop App / Web UI (`dsh` / `@deepseek-ai/dsh`):
    `skills/` + `AGENTS.md` + `.dsh/{agents,commands,context-mode,cordis.patch.yml}`
    (or `$DSH_HOME/skills/` + `$DSH_HOME/horus/{agents,commands,context-mode,scripts,AGENTS.md,cordis.patch.yml}` in global mode)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

VERSION = "0.7.0"
HELPER_SCRIPTS = [
    "sync_upstream.py",
    "validate_horus.py",
    "migrate-opencode-db.py",
    "horus_foundry.py",
    "horus_todo.py",
    "install_harness.py",
]


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(
        src,
        dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
    )


def write_with_backup(dst: Path, content: str, *, force: bool) -> str:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        if not force:
            return f"Kept existing {dst} (pass --force-config / -ForceConfig to upgrade with .bak backup)"
        shutil.copy2(dst, Path(str(dst) + ".bak"))
        dst.write_text(content, encoding="utf-8", newline="\n")
        return f"Updated {dst} (backup saved to {dst}.bak)"
    dst.write_text(content, encoding="utf-8", newline="\n")
    return f"Wrote {dst}"


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return "", text.strip()
    parts = re.split(r"\r?\n---\r?\n", text[4:], maxsplit=1)
    if len(parts) != 2:
        return "", text.strip()
    return parts[0], parts[1].strip()


def adapt_text_for_harness(text: str, harness: str, *, skills_root: str, ctx_server: str) -> str:
    out = text
    out = out.replace(".opencode/skills/", f"{skills_root}/")
    out = out.replace(".opencode/context-mode/server.js", ctx_server)
    if harness == "antigravity":
        note = (
            "\n> **Antigravity Runtime Adapter Note:** Whenever a Horus rule or skill references "
            "OpenCode's `question` tool, use Antigravity's native interactive prompt/confirmation UI "
            "(presenting concise recommended options with rationale) and wait for the user's choice.\n"
        )
        out = out.replace("\n## 1.", note + "\n## 1.", 1)
    elif harness == "dsh":
        note = (
            "\n> **DeepSeek Harness (DSH) Desktop App Adapter Note:** Whenever a Horus rule or skill "
            "references OpenCode's `question` tool, use DeepSeek Harness's native interactive approval/choice "
            "prompt (presenting concise recommended options with rationale) and wait for the user's choice. "
            "Skills live under `skills/` (project) or `$DSH_HOME/skills/` (global), and MCP servers are wired "
            "via `@deepseek-ai/dsh-mcp-client` in `$DSH_HOME/profiles/<profile>/cordis.patch.yml`.\n"
        )
        out = out.replace("\n## 1.", note + "\n## 1.", 1)
    return out


def convert_command_to_antigravity_workflow(cmd_path: Path) -> str:
    fm, body = split_frontmatter(cmd_path.read_text(encoding="utf-8"))
    name = cmd_path.stem
    dm = re.search(r"^description:\s*(.+)$", fm, re.M)
    desc = dm.group(1).strip() if dm else f'"Horus workflow: {name}"'
    if not (desc.startswith('"') or desc.startswith("'")):
        desc = f'"{desc}"'
    body = body.replace(".opencode/skills/", ".agents/skills/")
    body = body.replace("OpenCode's native `question` tool", "Antigravity's native interactive confirmation/choice prompt")
    body = body.replace("OpenCode's built-in `question` tool", "Antigravity's native interactive confirmation/choice prompt")
    return f"---\nname: {name}\ndescription: {desc}\n---\n\n# Workflow: /{name}\n\n{body}\n"


def merge_antigravity_mcp_config(cfg_path: Path, server_js: str) -> str:
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    data: dict = {}
    if cfg_path.exists():
        try:
            data = json.loads(cfg_path.read_text(encoding="utf-8-sig"))
            if not isinstance(data, dict):
                data = {}
        except Exception:
            shutil.copy2(cfg_path, Path(str(cfg_path) + ".bak"))
            data = {}
    servers = data.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        servers = {}
        data["mcpServers"] = servers
    servers["horus-context-mode"] = {
        "command": "node",
        "args": [server_js],
    }
    cfg_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    return f"Merged horus-context-mode into {cfg_path}"


def render_dsh_cordis_patch(server_js: str) -> str:
    # Exact Cordis YAML schema verified against @deepseek-ai/dsh-mcp-client
    escaped = server_js.replace("'", "''")
    return (
        "# Horus Super Agent v0.7.0 — DeepSeek Harness (DSH) Desktop App / Web UI Cordis MCP Patch\n"
        "# Merge into: $DSH_HOME/profiles/<profile>/cordis.patch.yml (DSH reloads live).\n"
        "# Requires Node.js >= 22.5.0 for horus-context-mode built-in node:sqlite.\n"
        "- insert:\n"
        "    - id: horus-context-mode\n"
        "      name: '@deepseek-ai/dsh-mcp-client'\n"
        "      config:\n"
        "        serverName: 'horus-context-mode'\n"
        "        transport: stdio\n"
        "        command: 'node'\n"
        "        args:\n"
        f"          - '{escaped}'\n"
        "        toolCallTimeoutMs: 120000\n"
        "\n"
        "# Optional: uncomment below only on massive repos if you want Graphify MCP in addition to CLI-first mode:\n"
        "#    - id: graphify\n"
        "#      name: '@deepseek-ai/dsh-mcp-client'\n"
        "#      config:\n"
        "#        serverName: 'graphify'\n"
        "#        transport: stdio\n"
        "#        command: 'graphify-mcp'\n"
        "#        args:\n"
        "#          - 'graphify-out/graph.json'\n"
        "#        toolCallTimeoutMs: 120000\n"
        "\n"
        "# Optional: if using ai-memory with DSH, run `ai-memory install-mcp --client dsh` and merge its entry here.\n"
    )


def install_antigravity(repo_root: Path, mode: str, target_dir: Path, force_config: bool) -> int:
    src_opencode = repo_root / ".opencode"
    if mode == "global":
        base = Path.home() / ".gemini" / "config"
        cfg_root = base
        skills_rel = str((base / "skills").as_posix())
        ctx_server = str((base / "context-mode" / "server.js").as_posix())
    else:
        base = target_dir / ".agents"
        cfg_root = target_dir
        skills_rel = ".agents/skills"
        ctx_server = ".agents/context-mode/server.js"

    copy_tree(src_opencode / "skills", base / "skills")
    copy_tree(src_opencode / "agents", base / "agents")
    copy_tree(src_opencode / "context-mode", base / "context-mode")

    wf_dir = base / "workflows"
    wf_dir.mkdir(parents=True, exist_ok=True)
    wf_count = 0
    for cmd_file in sorted((src_opencode / "commands").glob("*.md")):
        (wf_dir / cmd_file.name).write_text(
            convert_command_to_antigravity_workflow(cmd_file),
            encoding="utf-8",
            newline="\n",
        )
        wf_count += 1

    rules_dir = base / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    agents_md = (repo_root / "AGENTS.md").read_text(encoding="utf-8")
    horus_rule = (
        "---\n"
        "name: horus\n"
        'description: "Horus Super Agent v0.7.0 always-on harness rules for Google Antigravity"\n'
        "---\n\n"
        + adapt_text_for_harness(agents_md, "antigravity", skills_root=skills_rel, ctx_server=ctx_server)
    )
    (rules_dir / "horus.md").write_text(horus_rule, encoding="utf-8", newline="\n")

    if mode == "project":
        gemini_md = (
            "# Horus Super Agent (Google Antigravity / Gemini CLI)\n\n"
            "Follow all harness rules in `.agents/rules/horus.md`.\n"
            "- Skills (41 zero-bloat progressive-disclosure skills): `.agents/skills/`\n"
            "- Workflows (14 slash commands): `.agents/workflows/`\n"
            "- Subagent role playbooks (7): `.agents/agents/`\n"
            "- Horus Context Mode MCP server: `.agents/context-mode/server.js` (config snippet in `.agents/mcp_config.json`)\n"
        )
        print(write_with_backup(cfg_root / "GEMINI.md", gemini_md, force=force_config))
        mcp_path = base / "mcp_config.json"
        print(merge_antigravity_mcp_config(mcp_path, ctx_server))
    else:
        mcp_path = base / "mcp_config.json"
        print(merge_antigravity_mcp_config(mcp_path, ctx_server))

    scripts_dst = cfg_root / "scripts"
    scripts_dst.mkdir(parents=True, exist_ok=True)
    for s in HELPER_SCRIPTS:
        src_s = repo_root / "scripts" / s
        if src_s.exists():
            shutil.copy2(src_s, scripts_dst / s)

    skill_count = sum(1 for d in (base / "skills").iterdir() if d.is_dir() and (d / "SKILL.md").exists())
    agent_count = len(list((base / "agents").glob("*.md")))
    print(f"Installed Horus v{VERSION} (antigravity/{mode}) to {base}")
    print(
        f"HORUS VALIDATION PASSED (antigravity/{mode}): "
        f"{agent_count} agents, {skill_count} skills, {wf_count} workflows, rules/horus.md, mcp_config.json."
    )
    if mode == "global":
        print(
            "Note: If your Antigravity IDE reads ~/.gemini/antigravity/mcp_config.json instead of "
            "~/.gemini/config/mcp_config.json, copy the horus-context-mode block from "
            f"{mcp_path}."
        )
    return 0


def install_dsh(repo_root: Path, mode: str, target_dir: Path, force_config: bool) -> int:
    src_opencode = repo_root / ".opencode"
    dsh_home = Path(os.environ.get("DSH_HOME") or (Path.home() / ".dsh"))

    if mode == "global":
        base = dsh_home / "horus"
        skills_dst = dsh_home / "skills"
        cfg_root = base
        skills_rel = str(skills_dst.as_posix())
        ctx_server = str((base / "context-mode" / "server.js").as_posix())
    else:
        base = target_dir / ".dsh"
        skills_dst = target_dir / "skills"
        cfg_root = target_dir
        skills_rel = "skills"
        ctx_server = ".dsh/context-mode/server.js"

    skills_dst.mkdir(parents=True, exist_ok=True)
    for sd in sorted(d for d in (src_opencode / "skills").iterdir() if d.is_dir()):
        copy_tree(sd, skills_dst / sd.name)

    copy_tree(src_opencode / "agents", base / "agents")
    copy_tree(src_opencode / "commands", base / "commands")
    copy_tree(src_opencode / "context-mode", base / "context-mode")

    agents_md = (repo_root / "AGENTS.md").read_text(encoding="utf-8")
    dsh_agents_md = adapt_text_for_harness(agents_md, "dsh", skills_root=skills_rel, ctx_server=ctx_server)
    if mode == "project" and (target_dir / ".opencode").is_dir() and (cfg_root / "AGENTS.md").exists():
        # Co-installed alongside OpenCode: keep root AGENTS.md intact and store DSH-adapted rules under .dsh/
        print(write_with_backup(base / "AGENTS.md", dsh_agents_md, force=True))
    else:
        print(write_with_backup(cfg_root / "AGENTS.md", dsh_agents_md, force=force_config))

    patch_path = base / "cordis.patch.yml"
    patch_path.parent.mkdir(parents=True, exist_ok=True)
    patch_path.write_text(render_dsh_cordis_patch(ctx_server), encoding="utf-8", newline="\n")
    print(f"Wrote DSH Cordis MCP patch template to {patch_path}")

    scripts_dst = cfg_root / "scripts"
    scripts_dst.mkdir(parents=True, exist_ok=True)
    for s in HELPER_SCRIPTS:
        src_s = repo_root / "scripts" / s
        if src_s.exists():
            shutil.copy2(src_s, scripts_dst / s)

    skill_count = sum(1 for d in (src_opencode / "skills").iterdir() if d.is_dir() and (skills_dst / d.name / "SKILL.md").exists())
    agent_count = len(list((base / "agents").glob("*.md")))
    cmd_count = len(list((base / "commands").glob("*.md")))
    print(f"Installed Horus v{VERSION} (dsh/{mode}) to {base}")
    print(
        f"HORUS VALIDATION PASSED (dsh/{mode}): "
        f"{agent_count} agents, {skill_count} skills, {cmd_count} commands, cordis.patch.yml."
    )
    print(
        "Next step (DeepSeek Harness Desktop App / Web UI): merge the entry from "
        f"{patch_path} into $DSH_HOME/profiles/<profile>/cordis.patch.yml (DSH reloads live)."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Install Horus Super Agent adapters for Antigravity or DeepSeek Harness.")
    ap.add_argument("--harness", required=True, choices=["antigravity", "dsh"])
    ap.add_argument("--mode", default="project", choices=["project", "global"])
    ap.add_argument("--target-dir", default=".")
    ap.add_argument("--force-config", action="store_true")
    args = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parent.parent
    target_dir = Path(args.target_dir).resolve()

    if args.harness == "antigravity":
        return install_antigravity(repo_root, args.mode, target_dir, args.force_config)
    return install_dsh(repo_root, args.mode, target_dir, args.force_config)


if __name__ == "__main__":
    raise SystemExit(main())
