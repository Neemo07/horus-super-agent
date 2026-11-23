#!/usr/bin/env python3
"""
Horus Todo — Git-tracked `.todo.md` checklist, 1-click AI Requirement Analysis,
`plan.py` promoter, and optional live local sidebar UI for OpenCode (v0.4.3).

Inspired by deepseek-ai/dsh-todo-list (MIT), upgraded for OpenCode & Horus:
  - Zero external dependencies (Python 3.8+ stdlib only).
  - `.todo.md` is the single source of truth; rewrites ONLY checklist lines and
    preserves all headings, comments, and prose notes verbatim.
  - Refuses to overwrite an unrelated `.todo.md` lacking tasks or a todo marker.
  - Automatically stages `.todo.md` via `git add -- .todo.md` inside a Git repo
    (never auto-commits; reports if gitignored).
  - Generates structured AI Requirement Analysis prompts (conflicts, ordering,
    duplication, reasonableness of open vs completed tasks).
  - Promotes open `.todo.md` items into Horus `task_plan.md` (`plan.py` format).
  - Optional local live-reloading web sidebar (`serve --port 4178`).

Usage:
  python scripts/horus_todo.py list
  python scripts/horus_todo.py add "Wire OAuth refresh rotation"
  python scripts/horus_todo.py toggle 1
  python scripts/horus_todo.py edit 1 "Wire OAuth refresh rotation + tests"
  python scripts/horus_todo.py remove 2
  python scripts/horus_todo.py analyze
  python scripts/horus_todo.py promote [--phase "Phase 1: Backlog"]
  python scripts/horus_todo.py serve [--port 4178]
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

TODO_MARKERS = ("<!-- horus-todo:", "<!-- dsh-todo:")
HEADER_MARKER = (
    "<!-- horus-todo: managed by Horus Todo (OpenCode). "
    "Checklist lines are tasks; all other headings and notes are preserved. -->"
)
TASK_RE = re.compile(r"^(\s*)([-*+])\s+\[( |x|X)\]\s+(.*?)\s*$")
MAX_ITEMS = 200
MAX_ITEM_LEN = 500


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def parse_todo_text(raw: str) -> dict:
    lines = raw.splitlines()
    has_marker = any(any(m in ln for m in TODO_MARKERS) for ln in lines[:10])
    items = []
    for idx, ln in enumerate(lines):
        m = TASK_RE.match(ln)
        if m:
            items.append({
                "line": idx,
                "indent": m.group(1),
                "bullet": m.group(2),
                "done": m.group(3).lower() == "x",
                "text": m.group(4).strip(),
            })
    managed = has_marker or len(items) > 0 or raw.strip() == ""
    return {"lines": lines, "items": items, "managed": managed, "has_marker": has_marker}


def serialize_todo(raw: str, items: list[dict]) -> str:
    """Rewrite only checklist lines in `raw`, preserving all headings/notes verbatim."""
    if not raw.strip():
        out = [HEADER_MARKER, "", "# Todo list", ""]
        for it in items:
            mark = "x" if it.get("done") else " "
            out.append(f"{it.get('indent', '')}{it.get('bullet', '-')} [{mark}] {it['text']}")
        return "\n".join(out) + "\n"

    parsed = parse_todo_text(raw)
    if not parsed["managed"]:
        raise RuntimeError("unmanaged-file: .todo.md exists without todo marker or checklist lines; refusing to overwrite.")

    lines = list(parsed["lines"])
    task_positions = [it["line"] for it in parsed["items"]]
    new_lines: list[str] = []
    written = 0

    for idx, ln in enumerate(lines):
        if idx in task_positions:
            if written < len(items):
                it = items[written]
                mark = "x" if it.get("done") else " "
                new_lines.append(f"{it.get('indent', '')}{it.get('bullet', '-')} [{mark}] {it['text']}")
                written += 1
            # Else item was deleted: omit this old task line
        else:
            new_lines.append(ln)

    # Append any extra newly added items right after the last original task line (or at end)
    if written < len(items):
        extras = [
            f"{it.get('indent', '')}{it.get('bullet', '-')} [{'x' if it.get('done') else ' '}] {it['text']}"
            for it in items[written:]
        ]
        new_lines.extend(extras)

    return "\n".join(new_lines).rstrip("\n") + "\n"


def inspect_and_stage_git(repo_root: Path, rel_name: str, stage: bool = False) -> dict:
    try:
        inside = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=str(repo_root), capture_output=True, text=True, timeout=10,
        )
        if inside.returncode != 0 or inside.stdout.strip() != "true":
            return {"in_git": False, "tracked": False, "ignored": False}

        ign = subprocess.run(
            ["git", "check-ignore", "-q", rel_name],
            cwd=str(repo_root), capture_output=True, text=True, timeout=10,
        )
        if ign.returncode == 0:
            return {"in_git": True, "tracked": False, "ignored": True}

        if stage and (repo_root / rel_name).exists():
            subprocess.run(
                ["git", "add", "--", rel_name],
                cwd=str(repo_root), capture_output=True, text=True, timeout=15,
            )

        ls = subprocess.run(
            ["git", "ls-files", "--error-unmatch", rel_name],
            cwd=str(repo_root), capture_output=True, text=True, timeout=10,
        )
        return {"in_git": True, "tracked": ls.returncode == 0, "ignored": False}
    except Exception:
        return {"in_git": False, "tracked": False, "ignored": False}


def load_state(repo_root: Path, filename: str = ".todo.md") -> dict:
    p = (repo_root / filename).resolve()
    # Guard against path traversal outside repo_root
    if repo_root.resolve() not in p.parents and p != repo_root.resolve():
        raise RuntimeError(f"Todo file must stay inside project root: {filename}")
    raw = p.read_text(encoding="utf-8") if p.exists() else ""
    parsed = parse_todo_text(raw)
    done = sum(1 for it in parsed["items"] if it["done"])
    total = len(parsed["items"])
    return {
        "path": p,
        "rel": filename,
        "exists": p.exists(),
        "raw": raw,
        "managed": parsed["managed"],
        "items": parsed["items"],
        "counts": {"total": total, "done": done, "open": total - done},
        "mtime": p.stat().st_mtime if p.exists() else 0.0,
    }


def save_items(repo_root: Path, filename: str, items: list[dict], git_track: bool = True) -> dict:
    if len(items) > MAX_ITEMS:
        raise RuntimeError(f"Too many todo items ({len(items)} > {MAX_ITEMS})")
    cleaned = []
    for it in items:
        text = re.sub(r"[\r\n]+", " ", str(it.get("text", "")).strip())[:MAX_ITEM_LEN]
        if not text:
            continue
        cleaned.append({
            "done": bool(it.get("done", False)),
            "text": text,
            "indent": it.get("indent", ""),
            "bullet": it.get("bullet", "-"),
        })
    st = load_state(repo_root, filename)
    if st["exists"] and not st["managed"]:
        raise RuntimeError("unmanaged-file: .todo.md has no checklist lines or todo marker; refusing to overwrite.")
    content = serialize_todo(st["raw"], cleaned)
    atomic_write(st["path"], content)
    git_info = inspect_and_stage_git(repo_root, filename, stage=git_track)
    after = load_state(repo_root, filename)
    after["git"] = git_info
    return after


def build_analysis_prompt(state: dict) -> str:
    open_items = [it["text"] for it in state["items"] if not it["done"]]
    done_items = [it["text"] for it in state["items"] if it["done"]]
    c = state["counts"]
    open_block = "\n".join(f"{i+1}. [ ] {t}" for i, t in enumerate(open_items)) or "(none)"
    done_block = "\n".join(f"- [x] {t}" for t in done_items) or "(none)"
    return (
        f"Analyze the project's `{state['rel']}` checklist ({c['done']}/{c['total']} done, {c['open']} open).\n\n"
        f"## Open Tasks\n{open_block}\n\n"
        f"## Completed Tasks\n{done_block}\n\n"
        f"## Requirement Analysis Audit\n"
        f"1. **Conflicts & Redundancy:** Flag any open task that conflicts with or duplicates completed work or another open task.\n"
        f"2. **Dependency Order:** Recommend the optimal execution order and highlight prerequisites.\n"
        f"3. **Reasonableness & Scope:** Flag vague, oversized, or stale items and suggest concrete rewrites or splits.\n"
        f"4. **Actionable Offer:** Present proposed `.todo.md` edits (or promotion into `task_plan.md` via `plan.py`) using OpenCode's native `question` tool."
    )


def promote_to_task_plan(repo_root: Path, filename: str, phase: str) -> tuple[int, Path]:
    st = load_state(repo_root, filename)
    open_items = [it["text"] for it in st["items"] if not it["done"]]
    tp = repo_root / "task_plan.md"
    if not open_items:
        return 0, tp

    if tp.exists():
        txt = tp.read_text(encoding="utf-8")
    else:
        txt = "# Task Plan\n\n## Goal\nDeliver verified items promoted from `.todo.md`.\n"

    # Determine next phase/task numbers cleanly
    existing_ids = re.findall(r"- \[[ ~x!]\] T(\d+)\.(\d+)", txt)
    phase_num = max((int(a) for a, _ in existing_ids), default=0) + 1
    lines = [f"\n## {phase}"]
    for i, text in enumerate(open_items, start=1):
        lines.append(f"- [ ] T{phase_num}.{i} {text} | accept: verified via build/test")
    atomic_write(tp, txt.rstrip() + "\n" + "\n".join(lines) + "\n")
    return len(open_items), tp


SIDEBAR_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Horus Todo (.todo.md)</title>
<style>
  :root { color-scheme: dark; --bg:#0d1017; --card:#141923; --border:#242c3d; --fg:#e6edf3; --muted:#8b949e; --accent:#00d4aa; --danger:#ef4444; }
  * { box-sizing:border-box; }
  body { margin:0; font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; background:var(--bg); color:var(--fg); display:flex; justify-content:center; padding:24px 16px; }
  .panel { width:100%; max-width:520px; background:var(--card); border:1px solid var(--border); border-radius:12px; overflow:hidden; box-shadow:0 12px 32px rgba(0,0,0,.45); }
  header { padding:14px 16px; border-bottom:1px solid var(--border); display:flex; align-items:center; justify-content:space-between; gap:8px; }
  h1 { margin:0; font-size:15px; display:flex; align-items:center; gap:8px; }
  .pill { font-size:11px; padding:2px 8px; border-radius:999px; background:#1c2536; color:var(--accent); border:1px solid #26354d; }
  .actions { display:flex; gap:6px; }
  button { background:#1c2536; color:var(--fg); border:1px solid var(--border); border-radius:7px; padding:6px 10px; font-size:12px; cursor:pointer; }
  button:hover { border-color:var(--accent); color:var(--accent); }
  button.primary { background:var(--accent); color:#041512; border-color:var(--accent); font-weight:600; }
  ul { list-style:none; margin:0; padding:8px 0; max-height:60vh; overflow:auto; }
  li { display:flex; align-items:center; gap:10px; padding:8px 16px; border-bottom:1px solid rgba(255,255,255,.03); }
  li:hover { background:rgba(255,255,255,.02); }
  li.done .txt { text-decoration:line-through; color:var(--muted); }
  .txt { flex:1; word-break:break-word; cursor:text; }
  .del { opacity:0; color:var(--danger); background:none; border:none; padding:2px 6px; font-size:14px; }
  li:hover .del { opacity:1; }
  footer { padding:12px 16px; border-top:1px solid var(--border); display:flex; gap:8px; }
  input[type=text] { flex:1; background:#0b0e14; color:var(--fg); border:1px solid var(--border); border-radius:8px; padding:8px 10px; font-size:13px; }
  input[type=text]:focus { outline:none; border-color:var(--accent); }
  .meta { padding:8px 16px; font-size:11px; color:var(--muted); display:flex; justify-content:space-between; background:#10141d; }
  #toast { position:fixed; bottom:16px; right:16px; background:#1c2536; border:1px solid var(--accent); color:var(--fg); padding:8px 12px; border-radius:8px; font-size:12px; display:none; }
</style>
</head>
<body>
<div class="panel">
  <header>
    <h1>Horus Todo <span class="pill" id="prog">0/0</span></h1>
    <div class="actions">
      <button id="btnAnalyze" title="Copy AI Requirement Analysis prompt for OpenCode">AI Analysis</button>
      <button id="btnPromote" title="Promote open items to task_plan.md">→ plan.py</button>
    </div>
  </header>
  <ul id="list"></ul>
  <footer>
    <input id="newTask" type="text" placeholder="Add task to .todo.md and press Enter..." />
    <button class="primary" id="btnAdd">Add</button>
  </footer>
  <div class="meta"><span id="gitBadge">Checking git...</span><span>.todo.md (live sync)</span></div>
</div>
<div id="toast"></div>
<script>
let items = [], lastMtime = 0;
const toast = (m) => { const t = document.getElementById('toast'); t.textContent = m; t.style.display = 'block'; setTimeout(() => t.style.display = 'none', 2600); };
async function api(path, body) {
  const r = await fetch(path, { method: body ? 'POST' : 'GET', headers: {'Content-Type':'application/json'}, body: body ? JSON.stringify(body) : undefined });
  return r.json();
}
function render(data) {
  items = data.items || []; lastMtime = data.mtime || 0;
  document.getElementById('prog').textContent = `${data.counts.done}/${data.counts.total}`;
  const g = data.git || {};
  document.getElementById('gitBadge').textContent = !g.in_git ? 'Not a git repo' : g.ignored ? '⚠ .todo.md is gitignored' : g.tracked ? '✓ Git tracked' : 'Untracked';
  const ul = document.getElementById('list'); ul.innerHTML = '';
  items.forEach((it, idx) => {
    const li = document.createElement('li'); if (it.done) li.className = 'done';
    const cb = document.createElement('input'); cb.type = 'checkbox'; cb.checked = it.done;
    cb.onchange = () => { items[idx].done = cb.checked; save(); };
    const sp = document.createElement('span'); sp.className = 'txt'; sp.textContent = it.text;
    sp.onclick = () => { const v = prompt('Edit task:', it.text); if (v !== null && v.trim()) { items[idx].text = v.trim(); save(); } };
    const del = document.createElement('button'); del.className = 'del'; del.textContent = '×';
    del.onclick = () => { items.splice(idx, 1); save(); };
    li.append(cb, sp, del); ul.append(li);
  });
}
async function load() { const d = await api('/api/state'); if (d.ok) render(d); }
async function save() { const d = await api('/api/save', { items }); if (d.ok) render(d); else toast('Error: ' + d.error); }
document.getElementById('btnAdd').onclick = () => {
  const inp = document.getElementById('newTask'); const v = inp.value.trim(); if (!v) return;
  items.push({ done: false, text: v }); inp.value = ''; save();
};
document.getElementById('newTask').addEventListener('keydown', e => { if (e.key === 'Enter') document.getElementById('btnAdd').click(); });
document.getElementById('btnAnalyze').onclick = async () => {
  const d = await api('/api/analyze'); if (!d.ok) return toast(d.error);
  await navigator.clipboard.writeText(d.prompt); toast('AI Requirement Analysis prompt copied — paste into OpenCode!');
};
document.getElementById('btnPromote').onclick = async () => {
  const d = await api('/api/promote', {}); toast(d.ok ? `Promoted ${d.count} task(s) to task_plan.md` : d.error);
};
load();
setInterval(async () => { const d = await api('/api/state'); if (d.ok && d.mtime !== lastMtime) render(d); }, 2500);
</script>
</body>
</html>
"""


def serve_sidebar(repo_root: Path, filename: str, port: int, git_track: bool) -> None:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def _json(self, code: int, obj: dict) -> None:
            raw = json.dumps(obj).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):
            if self.path == "/":
                raw = SIDEBAR_HTML.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)
                return
            if self.path == "/api/state":
                st = load_state(repo_root, filename)
                st["git"] = inspect_and_stage_git(repo_root, filename, stage=False)
                self._json(200, {"ok": True, "items": st["items"], "counts": st["counts"], "mtime": st["mtime"], "git": st["git"]})
                return
            if self.path == "/api/analyze":
                st = load_state(repo_root, filename)
                if st["counts"]["open"] == 0:
                    self._json(200, {"ok": False, "error": "No open tasks to analyze."})
                    return
                self._json(200, {"ok": True, "prompt": build_analysis_prompt(st)})
                return
            self._json(404, {"ok": False, "error": "not-found"})

        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length).decode("utf-8") or "{}") if length else {}
            try:
                if self.path == "/api/save":
                    st = save_items(repo_root, filename, body.get("items", []), git_track=git_track)
                    self._json(200, {"ok": True, "items": st["items"], "counts": st["counts"], "mtime": st["mtime"], "git": st["git"]})
                    return
                if self.path == "/api/promote":
                    cnt, tp = promote_to_task_plan(repo_root, filename, body.get("phase", "Phase 1: Promoted from .todo.md"))
                    self._json(200, {"ok": True, "count": cnt, "path": str(tp)})
                    return
            except Exception as exc:
                self._json(400, {"ok": False, "error": str(exc)})
                return
            self._json(404, {"ok": False, "error": "not-found"})

    srv = HTTPServer(("127.0.0.1", port), Handler)
    print(f"Horus Todo live sidebar listening at http://127.0.0.1:{port} (watching {repo_root / filename})")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Horus Todo — Git-tracked .todo.md checklist & AI requirement analyzer.")
    ap.add_argument("--dir", default=".", help="Project root directory (default: current)")
    ap.add_argument("--file", default=".todo.md", help="Relative todo filename (default: .todo.md)")
    ap.add_argument("--no-git", action="store_true", help="Disable automatic `git add -- .todo.md`")
    sp = ap.add_subparsers(dest="cmd", required=True)

    sp.add_parser("list", help="Show .todo.md checklist and Git tracking status")
    p_add = sp.add_parser("add", help="Add a task to .todo.md"); p_add.add_argument("text")
    p_tog = sp.add_parser("toggle", help="Toggle task #N (1-indexed)"); p_tog.add_argument("index", type=int)
    p_ed = sp.add_parser("edit", help="Edit task #N"); p_ed.add_argument("index", type=int); p_ed.add_argument("text")
    p_rm = sp.add_parser("remove", help="Remove task #N"); p_rm.add_argument("index", type=int)
    sp.add_parser("analyze", help="Output structured AI Requirement Analysis prompt for OpenCode")
    p_pro = sp.add_parser("promote", help="Promote open .todo.md items into task_plan.md (plan.py format)")
    p_pro.add_argument("--phase", default="Phase 1: Promoted from .todo.md")
    p_srv = sp.add_parser("serve", help="Start live-reloading local browser sidebar UI")
    p_srv.add_argument("--port", type=int, default=4178)

    args = ap.parse_args(argv)
    repo_root = Path(args.dir).resolve()
    git_track = not args.no_git

    if args.cmd == "list":
        st = load_state(repo_root, args.file)
        g = inspect_and_stage_git(repo_root, args.file, stage=False)
        c = st["counts"]
        git_tag = "git:tracked" if g["tracked"] else ("git:IGNORED" if g["ignored"] else ("git:untracked" if g["in_git"] else "no-git"))
        print(f"Horus Todo ({args.file}) — {c['done']}/{c['total']} done [{git_tag}]")
        for i, it in enumerate(st["items"], start=1):
            mark = "x" if it["done"] else " "
            print(f"  {i:>2}. [{mark}] {it['text']}")
        return 0

    if args.cmd == "add":
        st = load_state(repo_root, args.file)
        items = list(st["items"]) + [{"done": False, "text": args.text}]
        after = save_items(repo_root, args.file, items, git_track=git_track)
        print(f"Added #{after['counts']['total']}: {args.text}")
        return 0

    if args.cmd in ("toggle", "edit", "remove"):
        st = load_state(repo_root, args.file)
        items = list(st["items"])
        idx = args.index - 1
        if idx < 0 or idx >= len(items):
            print(f"ERROR: task index {args.index} out of range (1..{len(items)})", file=sys.stderr)
            return 1
        if args.cmd == "toggle":
            items[idx]["done"] = not items[idx]["done"]
        elif args.cmd == "edit":
            items[idx]["text"] = args.text
        else:
            items.pop(idx)
        save_items(repo_root, args.file, items, git_track=git_track)
        print(f"Updated {args.file} ({args.cmd} #{args.index})")
        return 0

    if args.cmd == "analyze":
        st = load_state(repo_root, args.file)
        if st["counts"]["open"] == 0:
            print("No open tasks in .todo.md to analyze.")
            return 0
        print(build_analysis_prompt(st))
        return 0

    if args.cmd == "promote":
        cnt, tp = promote_to_task_plan(repo_root, args.file, args.phase)
        print(f"Promoted {cnt} open task(s) from {args.file} -> {tp.name}")
        return 0

    if args.cmd == "serve":
        serve_sidebar(repo_root, args.file, args.port, git_track=git_track)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
