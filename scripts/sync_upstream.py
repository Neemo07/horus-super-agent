#!/usr/bin/env python3
"""Replace the bundled offline skill editions with the verbatim upstream skills.

Needs: git, network access. Python 3.8+ standard library only.

  python scripts/sync_upstream.py --list
  python scripts/sync_upstream.py --dry-run
  python scripts/sync_upstream.py                          # sync uncustomized skills
  python scripts/sync_upstream.py --force-customized       # also overwrite Horus-poll upgrades
  python scripts/sync_upstream.py --only superpowers,vibe  # by group
  python scripts/sync_upstream.py --only webapp-testing    # by skill name
  python scripts/sync_upstream.py --dest ~/.config/opencode/skills

Skills are located by SKILL.md frontmatter name (or directory-name alias), not by
hard-coded paths. Horus-customized skills (native OpenCode `question` poll upgrades)
are skipped by default unless `--force-customized` is passed. Replaced folders are
backed up to <dest>/../.skills-sync-backup/<ts>/ and the commits used are recorded
in <dest>/../SOURCES.lock.json.
"""
import argparse
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

GROUPS = {
    "vibe": {
        "repo": "https://github.com/abduallahJamal/vibe-engineering-playbook.git",
        "skills": {n: [] for n in ("vibe", "vibe-grill", "vibe-spec-plan",
                                   "vibe-scoped-build", "vibe-critique", "vibe-test-gate")},
        "commands": {"vibe.md": ".opencode/commands/vibe.md"},
    },
    "anthropic": {
        "repo": "https://github.com/anthropics/skills.git",
        "skills": {n: [] for n in (
            "frontend-design", "webapp-testing", "mcp-builder",
            "pdf", "docx", "xlsx", "pptx",
        )},
    },
    "vercel": {
        "repo": "https://github.com/vercel-labs/agent-skills.git",
        "skills": {"vercel-react-best-practices": ["react-best-practices"]},
    },
    "supabase": {
        "repo": "https://github.com/supabase/agent-skills.git",
        "skills": {"supabase-postgres-best-practices": []},
    },
    "superpowers": {
        "marketplace": "https://github.com/obra/superpowers-marketplace.git",
        "plugin": "superpowers",
        "default_repo": "https://github.com/obra/superpowers.git",
        # Only sync the 6 non-overlapping Superpowers skills (Horus/Vibe supersede the rest)
        "skills": {n: [] for n in (
            "brainstorming",
            "test-driven-development",
            "systematic-debugging",
            "using-git-worktrees",
            "finishing-a-development-branch",
            "writing-skills",
        )},
    },
}
# Skills and commands customized by Horus with native OpenCode `question` poll integration.
# Skipped by default so syncing upstream does not silently strip Horus poll guardrails.
PROTECTED_CUSTOMIZED_SKILLS = {
    "vibe",
    "vibe-grill",
    "vibe-spec-plan",
    "vibe-scoped-build",
    "vibe-critique",
    "vibe-test-gate",
    "brainstorming",
    "systematic-debugging",
    "using-git-worktrees",
    "finishing-a-development-branch",
    "writing-skills",
}
PROTECTED_CUSTOMIZED_COMMANDS = {"vibe.md"}
SKIP_DIRS = {".git", "node_modules", ".backup", "__pycache__"}


def run(args, cwd=None):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{' '.join(args)}\n{r.stderr.strip()}")
    return r.stdout.strip()


def clone(url, into):
    remote = url.startswith(("http://", "https://", "git@", "file://"))
    cmd = ["git", "clone", "--quiet"] + (["--depth", "1"] if remote else []) + [url, str(into)]
    run(cmd)
    return run(["git", "rev-parse", "HEAD"], cwd=into)


def fm_name(skill_md):
    try:
        head = skill_md.read_text(encoding="utf-8", errors="replace").split("---", 2)
        m = re.search(r"^name:\s*['\"]?([^'\"\r\n]+?)['\"]?\s*$", head[1], re.M)
        return m.group(1) if m else None
    except (IndexError, OSError):
        return None


def skill_dirs(root):
    for cur, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        if "SKILL.md" in files:
            yield Path(cur)


def rank(root, p):
    rel = p.relative_to(root).as_posix()
    pref = 0 if rel.startswith(".opencode/skills") else 1 if rel.startswith("skills/") else 2
    return (pref, len(rel))


def find_skill(root, name, aliases):
    wanted = {name, *aliases}
    hits = [d for d in skill_dirs(root) if fm_name(d / "SKILL.md") == name or d.name in wanted]
    return sorted(hits, key=lambda d: rank(root, d))[0] if hits else None


def onerror(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def install_dir(src, dest, name, backup_root, dry):
    action = "replace" if dest.exists() else "add"
    print(f"  {action:7} {name}  <-  {src}")
    if dry:
        return
    if dest.exists():
        bk = backup_root / name
        bk.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(dest), str(bk))
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns(".git"))
    md = dest / "SKILL.md"
    text = md.read_text(encoding="utf-8")
    fixed = re.sub(r"^(name:\s*).*$", lambda m: m.group(1) + name, text, count=1, flags=re.M)
    if fixed != text:
        md.write_text(fixed, encoding="utf-8", newline="\n")


def resolve_superpowers(cfg, work, overrides):
    if "superpowers" in overrides:
        return overrides["superpowers"]
    mk = work / "marketplace"
    clone(cfg["marketplace"], mk)
    for f in mk.rglob("marketplace.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        for p in data.get("plugins", []):
            if p.get("name") == cfg["plugin"]:
                src = p.get("source")
                if isinstance(src, dict):
                    return src.get("url") or ("https://github.com/%s.git" % src["repo"] if src.get("repo") else cfg["default_repo"])
                if isinstance(src, str) and src.startswith(("http", "git@")):
                    return src
    return cfg["default_repo"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dest", default=".opencode/skills", help="skills directory (default .opencode/skills)")
    ap.add_argument("--only", default="", help="comma list of group or skill names")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--force-customized", action="store_true",
                    help="also overwrite Horus-customized skills/commands (vibe*, brainstorming, vibe.md)")
    ap.add_argument("--override", action="append", default=[], metavar="GROUP=URL_OR_PATH",
                    help="use another repo/path for a group (testing, forks)")
    a = ap.parse_args()
    overrides = dict(o.split("=", 1) for o in a.override)

    if a.list:
        for g, c in GROUPS.items():
            names = "(all skills of the plugin)" if c["skills"] == "*" else ", ".join(c["skills"])
            print(f"{g:12} {names}")
        print(f"\nProtected (pass --force-customized to overwrite): {', '.join(sorted(PROTECTED_CUSTOMIZED_SKILLS))}")
        return 0
    if shutil.which("git") is None:
        print("git not found on PATH", file=sys.stderr)
        return 2

    only = {s.strip() for s in a.only.split(",") if s.strip()}
    dest = Path(a.dest).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_root = dest.parent / ".skills-sync-backup" / stamp
    lock_path = dest.parent / "SOURCES.lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8")) if lock_path.exists() else {}
    failures = []

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for g, cfg in GROUPS.items():
            wanted = None if cfg["skills"] == "*" else set(cfg["skills"])
            if only and g not in only and not (wanted and wanted & only):
                continue
            print(f"[{g}]")
            try:
                repo = resolve_superpowers(cfg, work, overrides) if g == "superpowers" else overrides.get(g, cfg["repo"])
                root = work / g
                sha = clone(repo, root)
                found = {}
                if cfg["skills"] == "*":
                    sk_root = root / "skills"
                    base = sk_root if sk_root.is_dir() else root
                    for d in sorted(skill_dirs(base)):
                        found[d.name] = d
                else:
                    for name, aliases in cfg["skills"].items():
                        d = find_skill(root, name, aliases)
                        if d is None:
                            failures.append(f"{g}/{name}: SKILL.md not found upstream")
                            print(f"  MISSING {name}")
                        else:
                            found[name] = d
                for name, d in found.items():
                    if only and g not in only and name not in only:
                        continue
                    if not a.force_customized and name in PROTECTED_CUSTOMIZED_SKILLS and (dest / name).exists():
                        print(f"  skip    {name}  (Horus-customized; pass --force-customized to overwrite)")
                        continue
                    install_dir(d, dest / name, name, backup_root, a.dry_run)
                    lock[name] = {"repo": repo, "commit": sha, "path": d.relative_to(root).as_posix(), "synced": stamp}
                for fname, rel in cfg.get("commands", {}).items():
                    src = root / rel
                    if src.is_file() and (not only or g in only):
                        cmd_dir = dest.parent / "commands"
                        if not a.force_customized and fname in PROTECTED_CUSTOMIZED_COMMANDS and (cmd_dir / fname).exists():
                            print(f"  skip    command {fname}  (Horus-customized; pass --force-customized to overwrite)")
                            continue
                        print(f"  command {fname}")
                        if not a.dry_run:
                            cmd_dir.mkdir(exist_ok=True)
                            if (cmd_dir / fname).exists():
                                (backup_root / "commands").mkdir(parents=True, exist_ok=True)
                                shutil.copy2(cmd_dir / fname, backup_root / "commands" / fname)
                            shutil.copy2(src, cmd_dir / fname)
            except RuntimeError as e:
                failures.append(f"{g}: {e}")
                print(f"  FAILED {e}")

    if not a.dry_run:
        lock_path.write_text(json.dumps(lock, indent=2, sort_keys=True), encoding="utf-8")
    print("\nDone." if not failures else "\nCompleted with problems:")
    for f in failures:
        print(" -", f)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
