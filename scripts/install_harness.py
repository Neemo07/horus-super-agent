#!/usr/bin/env python3
"""
Multi-harness standalone & project adapter installer for Horus Super Agent v0.7.8.

Ensures every skill, command/workflow, agent brief, plugin/hook reference, and script
(`plan.py`, `horus_todo.py`, `horus_foundry.py`, `validate_horus.py`, `context-mode`)
works standalone from ANY project directory across:
  - OpenCode (V1/V2): `~/.config/opencode/` (global standalone) or `.opencode/` (project)
  - Google Antigravity (IDE & `agy` CLI): `~/.gemini/config/` + `~/.gemini/GEMINI.md` + `~/.gemini/antigravity/mcp_config.json` (global standalone) or `.agents/` (project)
  - DeepSeek Harness Desktop App / Web UI (`dsh`): `$DSH_HOME/skills/` + `$DSH_HOME/horus/` + `$DSH_HOME/AGENTS.md` + `$DSH_HOME/profiles/*/cordis.patch.yml` (global standalone) or `skills/` + `.dsh/` (project)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

VERSION = "0.7.8"
MARKER_BEGIN = "<!-- HORUS:BEGIN -->"
MARKER_END = "<!-- HORUS:END -->"
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


def rewrite_paths_in_text(
    text: str,
    *,
    skills_root: str,
    ctx_root: str,
    scripts_root: str | None = None,
) -> str:
    """Rewrite relative `.opencode/` and Horus `scripts/*.py` paths to exact installed locations."""
    out = (
        text.replace(".opencode/skills/", f"{skills_root}/")
        .replace(".opencode/context-mode/", f"{ctx_root}/")
    )
    if scripts_root:
        for script_name in HELPER_SCRIPTS:
            # Replace standalone `scripts/<name>` without double-prefixing already absolute paths
            out = re.sub(
                rf"(?<![A-Za-z0-9_./\\-])scripts/{re.escape(script_name)}\b",
                f"{scripts_root}/{script_name}",
                out,
            )
    return out


def rewrite_installed_markdown_paths(
    root_dir: Path,
    *,
    skills_root: str,
    ctx_root: str,
    scripts_root: str | None = None,
) -> None:
    if not root_dir.is_dir():
        return
    for md in root_dir.rglob("*.md"):
        try:
            raw = md.read_text(encoding="utf-8")
        except Exception:
            continue
        # Preserve YAML frontmatter untouched (keeps catalog description <= 150 chars regardless of $HOME depth)
        if raw.startswith("---\n") or raw.startswith("---\r\n"):
            parts = re.split(r"(\r?\n---\r?\n)", raw[4:], maxsplit=1)
            if len(parts) == 3:
                fm_part, sep_part, body_part = parts
                new_body = rewrite_paths_in_text(
                    body_part,
                    skills_root=skills_root,
                    ctx_root=ctx_root,
                    scripts_root=scripts_root,
                )
                updated = raw[:4] + fm_part + sep_part + new_body
            else:
                updated = rewrite_paths_in_text(raw, skills_root=skills_root, ctx_root=ctx_root, scripts_root=scripts_root)
        else:
            updated = rewrite_paths_in_text(raw, skills_root=skills_root, ctx_root=ctx_root, scripts_root=scripts_root)
        if updated != raw:
            md.write_text(updated, encoding="utf-8", newline="\n")


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


def upsert_marked_block(dst: Path, block_body: str) -> str:
    dst.parent.mkdir(parents=True, exist_ok=True)
    marked = f"{MARKER_BEGIN}\n{block_body.strip()}\n{MARKER_END}\n"
    if not dst.exists():
        dst.write_text(marked, encoding="utf-8", newline="\n")
        return f"Created {dst} with Horus standalone block"
    existing = dst.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(MARKER_BEGIN) + r".*?" + re.escape(MARKER_END) + r"\r?\n?", re.S)
    if pattern.search(existing):
        updated = pattern.sub(marked, existing, count=1)
        if updated != existing:
            dst.write_text(updated, encoding="utf-8", newline="\n")
            return f"Updated Horus standalone block in {dst}"
        return f"Horus standalone block already current in {dst}"
    sep = "\n" if existing.endswith("\n") else "\n\n"
    dst.write_text(existing + sep + marked, encoding="utf-8", newline="\n")
    return f"Appended Horus standalone block to {dst} (preserved existing content)"


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return "", text.strip()
    parts = re.split(r"\r?\n---\r?\n", text[4:], maxsplit=1)
    if len(parts) != 2:
        return "", text.strip()
    return parts[0], parts[1].strip()


def adapt_text_for_harness(
    text: str,
    harness: str,
    *,
    skills_root: str,
    ctx_root: str,
    scripts_root: str | None = None,
) -> str:
    out = rewrite_paths_in_text(
        text,
        skills_root=skills_root,
        ctx_root=ctx_root,
        scripts_root=scripts_root,
    )
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
            "Skills live under `skills/` (project) or `$DSH_HOME/skills/` (global standalone), and MCP servers "
            "are wired via `@deepseek-ai/dsh-mcp-client` in `$DSH_HOME/profiles/<profile>/cordis.patch.yml`.\n"
        )
        out = out.replace("\n## 1.", note + "\n## 1.", 1)
    return out


def convert_command_to_antigravity_workflow(
    cmd_path: Path,
    *,
    skills_root: str,
    ctx_root: str,
    scripts_root: str | None = None,
) -> str:
    fm, body = split_frontmatter(cmd_path.read_text(encoding="utf-8"))
    name = cmd_path.stem
    dm = re.search(r"^description:\s*(.+)$", fm, re.M)
    desc = dm.group(1).strip() if dm else f'"Horus workflow: {name}"'
    if not (desc.startswith('"') or desc.startswith("'")):
        desc = f'"{desc}"'
    body = rewrite_paths_in_text(
        body,
        skills_root=skills_root,
        ctx_root=ctx_root,
        scripts_root=scripts_root,
    )
    body = (
        body.replace("OpenCode's native `question` tool", "Antigravity's native interactive confirmation/choice prompt")
        .replace("OpenCode's built-in `question` tool", "Antigravity's native interactive confirmation/choice prompt")
    )
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


def render_dsh_cordis_entry(server_js: str) -> str:
    escaped = server_js.replace("'", "''")
    return (
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
    )


def render_dsh_cordis_patch(server_js: str) -> str:
    return (
        f"# Horus Super Agent v{VERSION} — DeepSeek Harness (DSH) Desktop App / Web UI Cordis MCP Patch\n"
        "# Merge into: $DSH_HOME/profiles/<profile>/cordis.patch.yml (DSH reloads live).\n"
        "# Requires Node.js >= 22.5.0 for horus-context-mode built-in node:sqlite.\n"
        + render_dsh_cordis_entry(server_js)
        + "\n"
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


def apply_dsh_profiles(dsh_home: Path, server_js: str) -> list[str]:
    profiles_dir = dsh_home / "profiles"
    if not profiles_dir.is_dir():
        return []
    messages: list[str] = []
    entry = render_dsh_cordis_entry(server_js)
    for pf in sorted(profiles_dir.glob("*/cordis.patch.yml")):
        raw = pf.read_text(encoding="utf-8")
        if "id: horus-context-mode" in raw:
            messages.append(f"DSH profile already wired: {pf}")
            continue
        shutil.copy2(pf, Path(str(pf) + ".bak"))
        sep = "\n" if raw.endswith("\n") else "\n\n"
        pf.write_text(raw + sep + entry, encoding="utf-8", newline="\n")
        messages.append(f"Wired horus-context-mode into DSH profile {pf} (backup: {pf}.bak)")
    return messages


def run_validator(scripts_dst: Path, harness: str, root: Path) -> int:
    val = scripts_dst / "validate_horus.py"
    if not val.exists():
        return 0
    r = subprocess.run([sys.executable, str(val), "--harness", harness, "--root", str(root)])
    return r.returncode


def finalize_opencode_global(base: Path) -> int:
    """Resolve all skill, context-mode, and script paths in ~/.config/opencode/ for standalone global use."""
    skills_root = (base / "skills").as_posix()
    ctx_root = (base / "context-mode").as_posix()
    scripts_root = (base / "scripts").as_posix()
    for sub in ("skills", "agents", "commands"):
        rewrite_installed_markdown_paths(
            base / sub,
            skills_root=skills_root,
            ctx_root=ctx_root,
            scripts_root=scripts_root,
        )
    agents_md = base / "AGENTS.md"
    if agents_md.exists():
        raw = agents_md.read_text(encoding="utf-8")
        updated = rewrite_paths_in_text(raw, skills_root=skills_root, ctx_root=ctx_root, scripts_root=scripts_root)
        if updated != raw:
            agents_md.write_text(updated, encoding="utf-8", newline="\n")
    return 0


def install_antigravity(repo_root: Path, mode: str, target_dir: Path, force_config: bool) -> int:
    src_opencode = repo_root / ".opencode"
    if mode == "global":
        base = Path.home() / ".gemini" / "config"
        cfg_root = base
        skills_rel = (base / "skills").as_posix()
        ctx_root = (base / "context-mode").as_posix()
        scripts_root: str | None = (cfg_root / "scripts").as_posix()
    else:
        base = target_dir / ".agents"
        cfg_root = target_dir
        skills_rel = ".agents/skills"
        ctx_root = ".agents/context-mode"
        scripts_root = None
    ctx_server = f"{ctx_root}/server.js"

    copy_tree(src_opencode / "skills", base / "skills")
    copy_tree(src_opencode / "agents", base / "agents")
    copy_tree(src_opencode / "context-mode", base / "context-mode")
    rewrite_installed_markdown_paths(base / "skills", skills_root=skills_rel, ctx_root=ctx_root, scripts_root=scripts_root)
    rewrite_installed_markdown_paths(base / "agents", skills_root=skills_rel, ctx_root=ctx_root, scripts_root=scripts_root)

    wf_dir = base / "workflows"
    wf_dir.mkdir(parents=True, exist_ok=True)
    for cmd_file in sorted((src_opencode / "commands").glob("*.md")):
        (wf_dir / cmd_file.name).write_text(
            convert_command_to_antigravity_workflow(
                cmd_file,
                skills_root=skills_rel,
                ctx_root=ctx_root,
                scripts_root=scripts_root,
            ),
            encoding="utf-8",
            newline="\n",
        )

    rules_dir = base / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    agents_md = (repo_root / "AGENTS.md").read_text(encoding="utf-8")
    horus_rule = (
        "---\n"
        "name: horus\n"
        f'description: "Horus Super Agent v{VERSION} always-on harness rules for Google Antigravity"\n'
        "---\n\n"
        + adapt_text_for_harness(
            agents_md,
            "antigravity",
            skills_root=skills_rel,
            ctx_root=ctx_root,
            scripts_root=scripts_root,
        )
    )
    (rules_dir / "horus.md").write_text(horus_rule, encoding="utf-8", newline="\n")

    if mode == "project":
        gemini_md = (
            "# Horus Super Agent (Google Antigravity / Gemini CLI)\n\n"
            "Follow all harness rules in `.agents/rules/horus.md`.\n"
            "- Skills (42 zero-bloat progressive-disclosure skills): `.agents/skills/`\n"
            "- Workflows (15 slash commands): `.agents/workflows/`\n"
            "- Subagent role playbooks (7): `.agents/agents/`\n"
            "- Horus Context Mode MCP server: `.agents/context-mode/server.js` (config snippet in `.agents/mcp_config.json`)\n"
        )
        print(write_with_backup(cfg_root / "GEMINI.md", gemini_md, force=force_config))
        print(merge_antigravity_mcp_config(base / "mcp_config.json", ctx_server))
    else:
        global_gemini_block = (
            f"# Horus Super Agent v{VERSION} (Global Standalone — Every Antigravity Workspace)\n\n"
            f"Follow all harness rules in `{(base / 'rules' / 'horus.md').as_posix()}`.\n"
            f"- Global skills (42): `{skills_rel}/`\n"
            f"- Global workflows (15): `{(base / 'workflows').as_posix()}/`\n"
            f"- Global subagent playbooks (7): `{(base / 'agents').as_posix()}/`\n"
            f"- Global scripts: `{scripts_root}/`\n"
            f"- Global Context Mode MCP: `{ctx_server}`"
        )
        print(upsert_marked_block(Path.home() / ".gemini" / "GEMINI.md", global_gemini_block))
        print(merge_antigravity_mcp_config(base / "mcp_config.json", ctx_server))
        print(merge_antigravity_mcp_config(Path.home() / ".gemini" / "antigravity" / "mcp_config.json", ctx_server))

    scripts_dst = cfg_root / "scripts"
    scripts_dst.mkdir(parents=True, exist_ok=True)
    for s in HELPER_SCRIPTS:
        src_s = repo_root / "scripts" / s
        if src_s.exists():
            shutil.copy2(src_s, scripts_dst / s)

    print(f"Installed Horus v{VERSION} (antigravity/{mode}) to {base}")
    return run_validator(scripts_dst, "antigravity", cfg_root)


def install_dsh(
    repo_root: Path,
    mode: str,
    target_dir: Path,
    force_config: bool,
    apply_profiles: bool = False,
) -> int:
    src_opencode = repo_root / ".opencode"
    dsh_home = Path(os.environ.get("DSH_HOME") or (Path.home() / ".dsh"))

    if mode == "global":
        base = dsh_home / "horus"
        skills_dst = dsh_home / "skills"
        cfg_root = base
        skills_rel = skills_dst.as_posix()
        ctx_root = (base / "context-mode").as_posix()
        scripts_root: str | None = (cfg_root / "scripts").as_posix()
    else:
        base = target_dir / ".dsh"
        skills_dst = target_dir / "skills"
        cfg_root = target_dir
        skills_rel = "skills"
        ctx_root = ".dsh/context-mode"
        scripts_root = None
    ctx_server = f"{ctx_root}/server.js"

    skills_dst.mkdir(parents=True, exist_ok=True)
    for sd in sorted(d for d in (src_opencode / "skills").iterdir() if d.is_dir()):
        copy_tree(sd, skills_dst / sd.name)
    rewrite_installed_markdown_paths(skills_dst, skills_root=skills_rel, ctx_root=ctx_root, scripts_root=scripts_root)

    copy_tree(src_opencode / "agents", base / "agents")
    copy_tree(src_opencode / "commands", base / "commands")
    copy_tree(src_opencode / "context-mode", base / "context-mode")
    rewrite_installed_markdown_paths(base / "agents", skills_root=skills_rel, ctx_root=ctx_root, scripts_root=scripts_root)
    rewrite_installed_markdown_paths(base / "commands", skills_root=skills_rel, ctx_root=ctx_root, scripts_root=scripts_root)

    agents_md = (repo_root / "AGENTS.md").read_text(encoding="utf-8")
    dsh_agents_md = adapt_text_for_harness(
        agents_md,
        "dsh",
        skills_root=skills_rel,
        ctx_root=ctx_root,
        scripts_root=scripts_root,
    )
    if mode == "project" and (target_dir / ".opencode").is_dir() and (cfg_root / "AGENTS.md").exists():
        print(write_with_backup(base / "AGENTS.md", dsh_agents_md, force=True))
    else:
        print(write_with_backup(cfg_root / "AGENTS.md", dsh_agents_md, force=force_config))

    if mode == "global":
        global_dsh_block = (
            f"# Horus Super Agent v{VERSION} (Global Standalone — Every DeepSeek Harness Workspace)\n\n"
            f"Follow all harness rules in `{(base / 'AGENTS.md').as_posix()}`.\n"
            f"- Global skills (42): `{skills_rel}/`\n"
            f"- Global subagent playbooks (7): `{(base / 'agents').as_posix()}/`\n"
            f"- Global command playbooks (15): `{(base / 'commands').as_posix()}/`\n"
            f"- Global scripts: `{scripts_root}/`\n"
            f"- Global Context Mode MCP: `{ctx_server}` (Cordis patch: `{(base / 'cordis.patch.yml').as_posix()}`)"
        )
        print(upsert_marked_block(dsh_home / "AGENTS.md", global_dsh_block))

    patch_path = base / "cordis.patch.yml"
    patch_path.parent.mkdir(parents=True, exist_ok=True)
    patch_path.write_text(render_dsh_cordis_patch(ctx_server), encoding="utf-8", newline="\n")
    print(f"Wrote DSH Cordis MCP patch template to {patch_path}")

    if mode == "global" and apply_profiles:
        msgs = apply_dsh_profiles(dsh_home, ctx_server)
        for m in msgs:
            print(m)
        if not msgs:
            print(f"No existing profiles found under {dsh_home / 'profiles'}; merge {patch_path} after creating your first DSH profile.")

    scripts_dst = cfg_root / "scripts"
    scripts_dst.mkdir(parents=True, exist_ok=True)
    for s in HELPER_SCRIPTS:
        src_s = repo_root / "scripts" / s
        if src_s.exists():
            shutil.copy2(src_s, scripts_dst / s)

    print(f"Installed Horus v{VERSION} (dsh/{mode}) to {base}")
    rc = run_validator(scripts_dst, "dsh", cfg_root)
    if not (mode == "global" and apply_profiles):
        print(
            "Next step (DeepSeek Harness Desktop App / Web UI): merge the entry from "
            f"{patch_path} into $DSH_HOME/profiles/<profile>/cordis.patch.yml (or re-run with --apply-dsh-profiles / -ApplyDshProfiles)."
        )
    return rc


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Install Horus Super Agent adapters for OpenCode, Antigravity, or DeepSeek Harness.")
    ap.add_argument("--harness", required=True, choices=["opencode-global", "antigravity", "dsh"])
    ap.add_argument("--mode", default="project", choices=["project", "global"])
    ap.add_argument("--target-dir", default=".")
    ap.add_argument("--force-config", action="store_true")
    ap.add_argument(
        "--apply-dsh-profiles",
        action="store_true",
        help="In global DSH mode, safely append horus-context-mode into existing $DSH_HOME/profiles/*/cordis.patch.yml files.",
    )
    args = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parent.parent
    target_dir = Path(args.target_dir).resolve()

    if args.harness == "opencode-global":
        return finalize_opencode_global(target_dir)
    if args.harness == "antigravity":
        return install_antigravity(repo_root, args.mode, target_dir, args.force_config)
    return install_dsh(repo_root, args.mode, target_dir, args.force_config, apply_profiles=args.apply_dsh_profiles)


if __name__ == "__main__":
    raise SystemExit(main())
