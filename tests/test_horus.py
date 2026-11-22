#!/usr/bin/env python3
"""Automated test suite for Horus Super Agent (stdlib unittest, pytest-compatible)."""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLAN_PY = REPO_ROOT / ".opencode" / "skills" / "planning-with-evidence" / "scripts" / "plan.py"
VALIDATE_PY = REPO_ROOT / "scripts" / "validate_horus.py"
SYNC_PY = REPO_ROOT / "scripts" / "sync_upstream.py"
MIGRATE_PY = REPO_ROOT / "scripts" / "migrate-opencode-db.py"
INSTALL_SH = REPO_ROOT / "install.sh"


def run_py(script: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
    )


class TestValidateHorus(unittest.TestCase):
    def test_repo_passes_and_creates_no_pycache(self) -> None:
        # Remove any existing pycache first
        for d in REPO_ROOT.rglob("__pycache__"):
            if ".git" not in d.parts:
                shutil.rmtree(d, ignore_errors=True)
        r = run_py(VALIDATE_PY, cwd=REPO_ROOT)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("HORUS VALIDATION PASSED (project)", r.stdout)
        pycaches = [d for d in REPO_ROOT.rglob("__pycache__") if ".git" not in d.parts]
        self.assertEqual(pycaches, [], f"validate_horus.py polluted repo with __pycache__: {pycaches}")


    def test_agent_skill_allowlists_and_no_pruned_skills(self) -> None:
        skills_dir = REPO_ROOT / ".opencode" / "skills"
        existing = {p.name for p in skills_dir.iterdir() if p.is_dir()}
        pruned = {
            "subagent-driven-development",
            "using-superpowers",
            "executing-plans",
            "writing-plans",
            "dispatching-parallel-agents",
            "verification-before-completion",
            "requesting-code-review",
            "receiving-code-review",
        }
        self.assertEqual(existing & pruned, set(), f"Pruned skills still present: {existing & pruned}")
        import re as _re
        for af in sorted((REPO_ROOT / ".opencode" / "agents").glob("*.md")):
            txt = af.read_text(encoding="utf-8")
            for m in _re.finditer(r'action:\s*skill\s*\n\s*resource:\s*"?([^\n"]+)"?\s*\n\s*effect:\s*allow', txt):
                res = m.group(1).strip()
                if res != "*":
                    self.assertIn(res, existing, f"{af.name} allows nonexistent skill: {res}")

    def test_graphify_v09_integration_and_no_stale_commands(self) -> None:
        g_skill = REPO_ROOT / ".opencode" / "skills" / "graphify" / "SKILL.md"
        self.assertTrue(g_skill.exists(), "Official graphify SKILL.md missing")
        self.assertFalse((REPO_ROOT / ".opencode" / "skills" / "graphify-memory").exists())
        self.assertTrue((REPO_ROOT / ".opencode" / "commands" / "graphify.md").exists())
        refs = sorted(p.name for p in (REPO_ROOT / ".opencode" / "skills" / "graphify" / "references").glob("*.md"))
        self.assertEqual(len(refs), 8, f"Expected 8 Graphify references, got {refs}")

        # Ensure broken CLI/MCP strings do not linger in Horus config/agents/commands
        for rel in ("opencode.jsonc", "AGENTS.md", "install.ps1", "install.sh",
                    ".opencode/agents/horus.md", ".opencode/commands/horus-init.md"):
            txt = (REPO_ROOT / rel).read_text(encoding="utf-8")
            self.assertNotIn('"graphify", "--mcp"', txt, f"Stale MCP command in {rel}")
            self.assertNotIn("graphify . --no-viz", txt, f"Stale CLI flag in {rel}")
            self.assertNotIn("graphify . --update", txt, f"Stale update flag in {rel}")
            self.assertNotIn("graphify-memory", txt, f"Stale skill name in {rel}")

    def test_superpowers_v7_full_integration_clean(self) -> None:
        skills_dir = REPO_ROOT / ".opencode" / "skills"
        expected_assets = [
            skills_dir / "brainstorming" / "visual-companion.md",
            skills_dir / "brainstorming" / "scripts" / "server.cjs",
            skills_dir / "test-driven-development" / "writing-good-tests.md",
            skills_dir / "systematic-debugging" / "root-cause-tracing.md",
            skills_dir / "systematic-debugging" / "defense-in-depth.md",
            skills_dir / "systematic-debugging" / "find-polluter.sh",
            skills_dir / "writing-skills" / "render-graphs.js",
            skills_dir / "writing-skills" / "references" / "bulletproofing.md",
        ]
        for asset in expected_assets:
            self.assertTrue(asset.exists(), f"Missing Superpowers v7.0.2 companion asset: {asset}")
        for name in ("brainstorming", "test-driven-development", "systematic-debugging",
                     "using-git-worktrees", "finishing-a-development-branch", "writing-skills"):
            txt = (skills_dir / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn("superpowers:", txt, f"Claude prefix left in {name}/SKILL.md")
            self.assertNotIn("Announce at start", txt, f"Signal-only violation in {name}/SKILL.md")
            self.assertNotIn("../using-superpowers/", txt, f"Broken relative link in {name}/SKILL.md")

    def test_vercel_react_best_practices_full_edition(self) -> None:
        vdir = REPO_ROOT / ".opencode" / "skills" / "vercel-react-best-practices"
        self.assertTrue((vdir / "SKILL.md").exists())
        self.assertTrue((vdir / "AGENTS.md").exists())
        self.assertTrue((vdir / "metadata.json").exists())
        rules = [p for p in (vdir / "rules").glob("*.md") if not p.name.startswith("_")]
        self.assertGreaterEqual(len(rules), 70, f"Expected >= 70 Vercel React rules, got {len(rules)}")

    def test_supabase_postgres_best_practices_full_edition(self) -> None:
        sdir = REPO_ROOT / ".opencode" / "skills" / "supabase-postgres-best-practices"
        self.assertTrue((sdir / "SKILL.md").exists())
        refs = [p for p in (sdir / "references").glob("*.md") if not p.name.startswith("_")]
        self.assertGreaterEqual(len(refs), 31, f"Expected >= 31 Supabase Postgres references, got {len(refs)}")

    def test_anthropic_skills_full_integration_clean(self) -> None:
        skills_dir = REPO_ROOT / ".opencode" / "skills"
        for name in ("webapp-testing", "frontend-design", "mcp-builder", "pdf", "docx", "xlsx", "pptx"):
            self.assertTrue((skills_dir / name / "SKILL.md").exists(), f"Missing Anthropic skill: {name}")
        self.assertTrue((skills_dir / "webapp-testing" / "scripts" / "with_server.py").exists())
        # Ensure overlapping / Claude-branded skills remain excluded
        for excluded in ("skill-creator", "claude-api", "brand-guidelines", "web-artifacts-builder", "slack-gif-creator"):
            self.assertFalse((skills_dir / excluded).exists(), f"Excluded skill crept in: {excluded}")

    def test_global_install_produces_strict_json_and_validates(self) -> None:
        if os.name == "nt":
            self.skipTest("bash installer test runs on POSIX")
        with tempfile.TemporaryDirectory() as tmp:
            fake_home = Path(tmp) / "home"
            fake_home.mkdir()
            env = dict(os.environ, HOME=str(fake_home))
            r = subprocess.run(
                ["bash", str(INSTALL_SH), "global"],
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            cfg_file = fake_home / ".config" / "opencode" / "opencode.json"
            self.assertTrue(cfg_file.exists(), "global opencode.json not created")
            # Must parse as strict JSON (zero // comments)
            data = json.loads(cfg_file.read_text(encoding="utf-8"))
            self.assertEqual(data.get("default_agent"), "horus")
            self.assertIn("HORUS VALIDATION PASSED (global)", r.stdout)


class TestPlanPy(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.work = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_init_start_done_run_and_verify(self) -> None:
        r = run_py(PLAN_PY, "--dir", str(self.work), "init")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.work / "task_plan.md").exists())

        r = run_py(PLAN_PY, "--dir", str(self.work), "start", "T1.1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("- [~] T1.1", (self.work / "task_plan.md").read_text(encoding="utf-8"))

        r = run_py(PLAN_PY, "--dir", str(self.work), "done", "T1.1", "--run", f"{sys.executable} -c \"print('ok')\"")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("- [x] T1.1", (self.work / "task_plan.md").read_text(encoding="utf-8"))

        r = run_py(PLAN_PY, "--dir", str(self.work), "verify", "--rerun")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("OK: every [x] task has passing evidence (commands re-run)", r.stdout)

    def test_hand_ticked_task_flagged_unproven(self) -> None:
        run_py(PLAN_PY, "--dir", str(self.work), "init")
        tp = self.work / "task_plan.md"
        tp.write_text(tp.read_text(encoding="utf-8").replace("- [ ] T1.1", "- [x] T1.1", 1), encoding="utf-8")
        r = run_py(PLAN_PY, "--dir", str(self.work), "verify")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("PROBLEM T1.1 marked [x] but has no passing evidence", r.stdout)

    def test_file_evidence_sha256_tamper_detected(self) -> None:
        run_py(PLAN_PY, "--dir", str(self.work), "init")
        artifact = self.work / "output.txt"
        artifact.write_text("original verified output\n", encoding="utf-8")
        r = run_py(PLAN_PY, "--dir", str(self.work), "done", "T1.2", "--file", "output.txt")
        self.assertEqual(r.returncode, 0, r.stderr)

        r = run_py(PLAN_PY, "--dir", str(self.work), "verify")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

        # Mutate the artifact after proof -> verify must fail
        artifact.write_text("tampered content\n", encoding="utf-8")
        r = run_py(PLAN_PY, "--dir", str(self.work), "verify")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("evidence file modified since proof", r.stdout)

    def test_handoff_generation(self) -> None:
        run_py(PLAN_PY, "--dir", str(self.work), "init")
        r = run_py(PLAN_PY, "--dir", str(self.work), "handoff", "--note", "ready for wave 2")
        self.assertEqual(r.returncode, 0, r.stderr)
        handoff = (self.work / "HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("ready for wave 2", handoff)


class TestSyncUpstream(unittest.TestCase):
    def test_list_shows_protected_customized_skills(self) -> None:
        r = run_py(SYNC_PY, "--list")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Protected (pass --force-customized to overwrite)", r.stdout)
        self.assertIn("brainstorming", r.stdout)
        self.assertIn("vibe-grill", r.stdout)


class TestMigrateOpenCodeDb(unittest.TestCase):
    def test_restore_handles_schema_column_drift(self) -> None:
        spec = importlib.util.spec_from_file_location("migrate_opencode_db", MIGRATE_PY)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            old_db = Path(tmp) / "old.db"
            new_db = Path(tmp) / "new.db"

            # Old DB has a subset of columns + an extra legacy column
            o = sqlite3.connect(old_db)
            o.executescript("""
                CREATE TABLE project (id TEXT PRIMARY KEY, worktree TEXT, name TEXT, legacy_extra TEXT);
                CREATE TABLE session_v2 (id TEXT PRIMARY KEY, project_id TEXT, title TEXT, time_created INT, time_updated INT);
                CREATE TABLE session_message (
                    id TEXT PRIMARY KEY, session_id TEXT, type TEXT, seq INT,
                    time_created INT, time_updated INT, data TEXT
                );
                INSERT INTO project VALUES ('p1', '/repo', 'Horus', 'unused');
                INSERT INTO session_v2 VALUES ('s1', 'p1', NULL, 100, 200);
                INSERT INTO session_message VALUES ('m1', 's1', 'user', 1, 100, 101, '{"text": "hello"}');
            """)
            o.commit()
            o.close()

            # New DB has slightly different columns (no legacy_extra, title NOT NULL)
            n = sqlite3.connect(new_db)
            n.executescript("""
                CREATE TABLE project (id TEXT PRIMARY KEY, worktree TEXT, name TEXT, new_col TEXT);
                CREATE TABLE session (id TEXT PRIMARY KEY, project_id TEXT, title TEXT NOT NULL, time_created INT, time_updated INT);
                CREATE TABLE message (id TEXT PRIMARY KEY, session_id TEXT, time_created INT, time_updated INT, data TEXT);
                CREATE TABLE part (id TEXT PRIMARY KEY, message_id TEXT, session_id TEXT, time_created INT, time_updated INT, data TEXT);
            """)
            n.commit()
            n.close()

            stats = mod.restore(str(old_db), str(new_db))
            self.assertEqual(stats["project"], 1)
            self.assertEqual(stats["session"], 1)
            self.assertEqual(stats["message"], 1)
            self.assertEqual(stats["part"], 1)
            self.assertEqual(stats["fk_violations"], 0)

            n = sqlite3.connect(new_db)
            title = n.execute("SELECT title FROM session WHERE id='s1'").fetchone()[0]
            self.assertEqual(title, "")
            n.close()


if __name__ == "__main__":
    unittest.main()
