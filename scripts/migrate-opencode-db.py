#!/usr/bin/env python3
"""Move the live opencode.db aside, create a fresh V1-schema DB, and restore
content (projects, sessions, messages, parts) from the old DB.

Old schema (OpenCode Desktop 2.3.2): session_v2 + session_message(JSON blob)
New schema (opencode CLI 1.19.x):    session    + message + part

Usage:
  python migrate-opencode-db.py --db <path/to/opencode.db> [--dry-run]

Exit codes: 0 ok, 1 locked/failed, 2 dry-run ok
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time

SESS_COLS = [
    "id", "project_id", "workspace_id", "parent_id", "slug", "directory", "path",
    "title", "version", "share_url", "summary_additions", "summary_deletions",
    "summary_files", "summary_diffs", "metadata", "cost", "tokens_input",
    "tokens_output", "tokens_reasoning", "tokens_cache_read", "tokens_cache_write",
    "revert", "permission", "agent", "model", "time_created", "time_updated",
    "time_compacting", "time_archived",
]
PROJ_COLS = [
    "id", "worktree", "vcs", "name", "icon_url", "icon_url_override", "icon_color",
    "time_created", "time_updated", "time_initialized", "sandboxes", "commands",
]


def log(msg: str) -> None:
    print(msg, flush=True)


def is_locked(path: str) -> bool:
    """True when another process holds an exclusive handle on the file."""
    if not os.path.exists(path):
        return False
    try:
        with open(path, "rb+"):
            return False
    except OSError:
        return True


def table_names(con: sqlite3.Connection) -> set[str]:
    return {r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}


def backup(src: str, stamp: str) -> str:
    """Consistent snapshot via SQLite online backup API."""
    dst = f"{src}.backup-{stamp}"
    s = sqlite3.connect(f"file:{src}?mode=ro", uri=True)
    d = sqlite3.connect(dst)
    try:
        s.backup(d)
    finally:
        d.close()
        s.close()
    return dst


def verify_db(path: str) -> dict[str, object]:
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        out: dict[str, object] = {
            "integrity": con.execute("PRAGMA integrity_check").fetchone()[0]}
        for t in ("project", "session_v2", "session_message", "session", "message", "part"):
            if t in table_names(con):
                out[t] = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        return out
    finally:
        con.close()


def find_cli() -> str:
    """Resolve the real opencode executable (on Windows PATH it is a .ps1 shim)."""
    override = os.environ.get("OPENCODE_BIN")
    if override and os.path.exists(override):
        return override
    for name in ("opencode.exe", "opencode.cmd", "opencode"):
        found = shutil.which(name)
        if found and not found.lower().endswith(".ps1"):
            return found
    npm_exe = os.path.expandvars(
        r"%APPDATA%\npm\node_modules\opencode-ai\bin\opencode.exe")
    if os.path.exists(npm_exe):
        return npm_exe
    raise RuntimeError("opencode CLI not found; set OPENCODE_BIN")


def create_fresh(db_path: str) -> None:
    """Let the CLI build its own schema at the target path."""
    env = dict(os.environ)
    env["OPENCODE_DB"] = db_path
    # Run from a neutral dir: a project opencode.json/jsonc in cwd could be
    # rejected by this CLI version and abort schema creation.
    neutral = tempfile.mkdtemp(prefix="opencode-schema-")
    try:
        # `db path` opens (and therefore migrates/creates) the database.
        subprocess.run([find_cli(), "db", "path"], env=env, check=True,
                       capture_output=True, text=True, cwd=neutral)
    finally:
        shutil.rmtree(neutral, ignore_errors=True)


def restore(old_db: str, new_db: str) -> dict[str, int]:
    """Copy content old-schema -> new-schema."""
    o = sqlite3.connect(f"file:{old_db}?mode=ro", uri=True)
    n = sqlite3.connect(new_db)
    n.execute("PRAGMA foreign_keys=OFF")
    stats = {"project": 0, "session": 0, "message": 0, "part": 0, "skipped": 0}
    try:
        rows = o.execute(f"SELECT {','.join(PROJ_COLS)} FROM project").fetchall()
        n.executemany(
            f"INSERT OR REPLACE INTO project ({','.join(PROJ_COLS)}) "
            f"VALUES ({','.join('?' * len(PROJ_COLS))})", rows)
        stats["project"] = len(rows)

        rows = o.execute(f"SELECT {','.join(SESS_COLS)} FROM session_v2").fetchall()
        fixed = []
        for r in rows:
            r = list(r)
            if r[7] is None:  # title is NOT NULL in the new schema
                r[7] = ""
            fixed.append(r)
        n.executemany(
            f"INSERT OR REPLACE INTO session ({','.join(SESS_COLS)}) "
            f"VALUES ({','.join('?' * len(SESS_COLS))})", fixed)
        stats["session"] = len(fixed)

        valid = {r[0] for r in n.execute("SELECT id FROM session")}
        mrows = o.execute(
            "SELECT id,session_id,type,seq,time_created,time_updated,data "
            "FROM session_message ORDER BY session_id,seq").fetchall()
        for mid, sid, mtype, _seq, tc, tu, data in mrows:
            if sid not in valid:
                stats["skipped"] += 1
                continue
            try:
                d = json.loads(data)
            except (TypeError, ValueError):
                stats["skipped"] += 1
                continue
            role = mtype if mtype in ("user", "assistant", "system") else "user"
            mdata: dict[str, object] = {"role": role,
                                        "time": {"created": tc, "completed": tu}}
            if role == "assistant":
                for k in ("agent", "model", "cost", "tokens", "finish", "rawFinish"):
                    if k in d:
                        mdata[k] = d[k]
            elif "metadata" in d:
                mdata["metadata"] = d["metadata"]
            n.execute(
                "INSERT OR REPLACE INTO message "
                "(id,session_id,time_created,time_updated,data) VALUES (?,?,?,?,?)",
                (mid, sid, tc, tu, json.dumps(mdata)))
            stats["message"] += 1

            content = d.get("content")
            parts = content if isinstance(content, list) and content else None
            if parts is None:
                pdata: dict[str, object] = {"type": "text",
                                            "text": d.get("text") or ""}
                if "description" in d:
                    pdata["description"] = d["description"]
                parts = [pdata]
            for i, c in enumerate(parts):
                if not isinstance(c, dict):
                    continue
                n.execute(
                    "INSERT OR REPLACE INTO part "
                    "(id,message_id,session_id,time_created,time_updated,data) "
                    "VALUES (?,?,?,?,?,?)",
                    (f"{mid}_p{i}", mid, sid, tc, tu, json.dumps(c)))
                stats["part"] += 1
        n.commit()
        fk = n.execute("PRAGMA foreign_key_check").fetchall()
        stats["fk_violations"] = len(fk)  # type: ignore[assignment]
        return stats
    finally:
        n.close()
        o.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True, help="path to live opencode.db")
    ap.add_argument("--dry-run", action="store_true",
                    help="validate only; never move or write")
    args = ap.parse_args()
    db = os.path.abspath(args.db)

    if not os.path.exists(db):
        log(f"ERROR: not found: {db}")
        return 1

    for suffix in ("", "-wal", "-shm"):
        if is_locked(db + suffix):
            log(f"LOCKED: {db}{suffix} — close OpenCode Desktop and retry.")
            return 1

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    log(f"live db: {db}")
    log(f"before:  {verify_db(db)}")

    if args.dry_run:
        log("dry-run: lock check passed, nothing written.")
        return 2

    bak = backup(db, stamp)
    log(f"backup:  {bak}")
    log(f"backup check: {verify_db(bak)}")

    # Build the replacement BEFORE touching the live file, so a failure here
    # leaves the original DB untouched and working.
    stage = f"{db}.staging-{stamp}"
    log("creating fresh schema via CLI ...")
    create_fresh(stage)
    log(f"staging: {verify_db(stage)}")

    log("restoring content into staging db ...")
    stats = restore(bak, stage)
    log(f"restore: {stats}")
    if stats.get("fk_violations"):
        log("FAIL: foreign key violations; live DB untouched.")
        os.remove(stage)
        return 1

    moved = []
    for suffix in ("", "-wal", "-shm"):
        src = db + suffix
        if os.path.exists(src):
            dst = f"{db}.moved-{stamp}{suffix}"
            os.replace(src, dst)
            moved.append(dst)
            log(f"moved:   {src} -> {os.path.basename(dst)}")

    os.replace(stage, db)
    log(f"installed: {db}")

    log(f"new db:  {verify_db(db)}")
    log("OK: migration complete. Old DB kept at:")
    for m in moved:
        log(f"  {m}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
