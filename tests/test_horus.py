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
FOUNDRY_PY = REPO_ROOT / "scripts" / "horus_foundry.py"
TODO_PY = REPO_ROOT / "scripts" / "horus_todo.py"
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

    def test_horus_context_mode_integration_and_rebrand(self) -> None:
        ctx_dir = REPO_ROOT / ".opencode" / "context-mode"
        for rel in ("package.json", "server.js", "lib/store.js", "lib/chunker.js",
                    "lib/executor.js", "lib/tools.js", "dashboard/server.mjs", "dashboard/index.html"):
            p = ctx_dir / rel
            self.assertTrue(p.exists(), f"Missing Horus Context Mode file: {rel}")
            if p.suffix in (".js", ".mjs", ".html"):
                txt = p.read_text(encoding="utf-8")
                self.assertNotIn('"antigravity-plugin-context-mode"', txt, f"Unrebranded runtime name in {rel}")
                self.assertNotIn("Antigravity Context Mode", txt, f"Unrebranded UI title in {rel}")
                self.assertNotIn("C:/Users/domus", txt, f"Hardcoded author path left in {rel}")
        # Check MCP registration in both V2 and V1 configs
        v1 = json.loads((REPO_ROOT / "opencode.v1.json").read_text(encoding="utf-8"))
        self.assertIn("horus-context-mode", v1.get("mcp", {}))
        self.assertTrue((REPO_ROOT / ".opencode" / "skills" / "horus-context-mode" / "SKILL.md").exists())
        self.assertTrue((REPO_ROOT / ".opencode" / "commands" / "horus-context.md").exists())
        if shutil.which("node"):
            for js in ("server.js", "lib/store.js", "lib/chunker.js", "lib/executor.js", "lib/tools.js", "dashboard/server.mjs"):
                r = subprocess.run(["node", "--check", str(ctx_dir / js)], capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, f"node --check failed for {js}: {r.stderr}")

    def test_horus_next_steps_opencode_native_and_primary_only(self) -> None:
        ns = REPO_ROOT / ".opencode" / "skills" / "horus-next-steps" / "SKILL.md"
        self.assertTrue(ns.exists(), "Missing horus-next-steps skill")
        txt = ns.read_text(encoding="utf-8")
        # Must use OpenCode native `question` tool schema, zero Antigravity schema leftovers
        self.assertNotIn("ask_question", txt)
        self.assertNotIn("is_multi_select", txt)
        self.assertNotIn("send_message", txt)
        self.assertIn('"header": "Next Step"', txt)
        # Must NOT be explicitly granted to any worker subagent
        for worker in ("c-engineer.md", "re-analyst.md", "ui-gui-engineer.md", "web-engineer.md"):
            wtxt = (REPO_ROOT / ".opencode" / "agents" / worker).read_text(encoding="utf-8")
            self.assertNotIn("horus-next-steps", wtxt, f"Primary-only skill leaked to worker {worker}")

    def test_design_system_audit_document_extend_merged_cleanly(self) -> None:
        ds = REPO_ROOT / ".opencode" / "skills" / "ui-ux-design-systems" / "SKILL.md"
        txt = ds.read_text(encoding="utf-8")
        for heading in ("### A. Audit Mode", "### B. Documentation Mode", "### C. Extend Mode"):
            self.assertIn(heading, txt)
        self.assertNotIn("collectivebrain.de", txt)
        self.assertNotIn("whitefox-automations.com", txt)

    def test_design_engineering_20_playbooks_progressive_disclosure(self) -> None:
        de = REPO_ROOT / ".opencode" / "skills" / "design-engineering"
        refs = de / "references"
        self.assertTrue((de / "SKILL.md").exists())
        self.assertTrue((REPO_ROOT / ".opencode" / "commands" / "design.md").exists())
        self.assertTrue((refs / "ui-cheatsheet.md").exists())
        self.assertTrue((refs / "performance-cheatsheet.md").exists())
        playbooks = sorted(p.name for p in refs.iterdir() if p.is_dir() and (p / "SKILL.md").exists())
        self.assertEqual(len(playbooks), 21, f"Expected 21 design-engineering playbooks, got {len(playbooks)}")
        self.assertIn("stageshow", playbooks)
        self.assertTrue((refs / "stageshow" / "kit" / "act.ts").exists())
        self.assertTrue((refs / "stageshow" / "scripts" / "film.mjs").exists())
        self.assertGreaterEqual(len(list((refs / "stageshow" / "references").glob("*.md"))), 15)
        lt_txt = (refs / "learn-taste" / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("~/.claude/projects/", lt_txt)

    def test_engineering_craft_18_playbooks_progressive_disclosure(self) -> None:
        ec = REPO_ROOT / ".opencode" / "skills" / "engineering-craft"
        refs = ec / "references"
        self.assertTrue((ec / "SKILL.md").exists())
        self.assertTrue((REPO_ROOT / ".opencode" / "commands" / "craft.md").exists())
        playbooks = sorted(p.name for p in refs.iterdir() if p.is_dir() and (p / "SKILL.md").exists())
        self.assertEqual(len(playbooks), 18, f"Expected 18 engineering-craft playbooks, got {len(playbooks)}")
        # Ensure Claude-only tool/path strings were replaced
        for md in refs.rglob("*.md"):
            txt = md.read_text(encoding="utf-8", errors="replace")
            self.assertNotIn("AskUserQuestion", txt, f"Claude AskUserQuestion left in {md}")
            self.assertNotIn("~/.claude/skills/", txt, f"Claude skills path left in {md}")

    def test_defensive_security_audit_skill_and_command(self) -> None:
        sa = REPO_ROOT / ".opencode" / "skills" / "security-audit" / "SKILL.md"
        self.assertTrue(sa.exists())
        self.assertTrue((REPO_ROOT / ".opencode" / "commands" / "security.md").exists())
        txt = sa.read_text(encoding="utf-8")
        self.assertIn("CWE-639", txt)
        self.assertIn("libFuzzer", txt)

    def test_agent_architecture_reference_bilingual_chapters(self) -> None:
        ar = REPO_ROOT / ".opencode" / "skills" / "agent-architecture-reference"
        self.assertTrue((ar / "SKILL.md").exists())
        en = list((ar / "references" / "en").glob("*.md"))
        zh = list((ar / "references" / "zh-CN").glob("*.md"))
        self.assertEqual(len(en), 19, f"Expected 19 EN chapters, got {len(en)}")
        self.assertEqual(len(zh), 19, f"Expected 19 ZH chapters, got {len(zh)}")

    def test_zero_catalog_bloat_and_zero_playbook_collisions(self) -> None:
        import re as _re
        skills_dir = REPO_ROOT / ".opencode" / "skills"
        total_desc = 0
        for sd in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
            txt = (sd / "SKILL.md").read_text(encoding="utf-8")
            fm = _re.split(r"\r?\n---\r?\n", txt[4:], maxsplit=1)[0]
            dm = _re.search(r"^description:\s*(.+)$", fm, _re.M)
            self.assertIsNotNone(dm, f"Missing description in {sd.name}")
            desc = dm.group(1).strip().strip('"').strip("'")
            self.assertLessEqual(len(desc), 150, f"Bloated description in {sd.name}: {len(desc)} chars")
            total_desc += len(desc)
        self.assertLessEqual(total_desc, 5200, f"Total catalog too large: {total_desc} chars")
        # Ensure zero duplicate playbook names across all references
        seen = {}
        for p in skills_dir.rglob("SKILL.md"):
            seen.setdefault(p.parent.name, []).append(p.relative_to(skills_dir).as_posix())
        dups = {k: v for k, v in seen.items() if len(v) > 1}
        self.assertEqual(dups, {}, f"Duplicate playbook names found: {dups}")

    def test_horus_memory_ai_memory_integration_zero_bloat(self) -> None:
        hm = REPO_ROOT / ".opencode" / "skills" / "horus-memory"
        self.assertTrue((hm / "SKILL.md").exists())
        self.assertTrue((REPO_ROOT / ".opencode" / "commands" / "horus-memory.md").exists())
        refs = hm / "references"
        for h in ("retrieval.md", "durable-pages.md", "handoff.md", "learning-maintenance.md", "messaging.md"):
            self.assertTrue((refs / h).exists(), f"Missing horus-memory handbook: {h}")
        self.assertGreaterEqual(len(list((refs / "opencode-hooks").glob("*"))), 10)
        # Ensure upstream's 7 split ai-memory-* skills did not creep in as top-level skills
        for bad in ("ai-memory-retrieval", "ai-memory-durable-pages", "ai-memory-handoff", "ai-memory-messaging"):
            self.assertFalse((REPO_ROOT / ".opencode" / "skills" / bad).exists())

    def test_senior_engineering_partner_integration_zero_bloat_zero_overlap(self) -> None:
        sp = REPO_ROOT / ".opencode" / "skills" / "senior-engineering-partner"
        sm = sp / "SKILL.md"
        self.assertTrue(sm.exists())
        self.assertTrue((REPO_ROOT / ".opencode" / "commands" / "partner.md").exists())
        # Must be a lean progressive-disclosure router, NOT the 92 KB monolith
        self.assertLessEqual(sm.stat().st_size, 10000, "senior-engineering-partner SKILL.md should be lean router")
        refs = sp / "references"
        self.assertEqual(len(list(refs.glob("*"))), 39, "Expected 39 unique non-overlapping references")
        for excluded in (
            "engineering-workflow.md", "debugging.md", "multi-agent-coordination.md",
            "ui-design-and-accessibility.md", "databases.md", "local-and-agentic-ai-tools.md",
            "skill-self-improvement.md", "frontend-web-security.md",
        ):
            self.assertFalse((refs / excluded).exists(), f"Overlapping ref should be excluded: {excluded}")
        scripts_dir = sp / "scripts"
        for sc in ("audit.sh", "actions-lint.sh", "leakage-guard.sh", "render-diagrams.sh", "self-review.md"):
            self.assertTrue((scripts_dir / sc).exists(), f"Missing helper script: {sc}")

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
            mcp_cmd = data.get("mcp", {}).get("horus-context-mode", {}).get("command", [])
            self.assertTrue(any(".config/opencode/context-mode/server.js" in c for c in mcp_cmd), f"Global MCP path not rewritten: {mcp_cmd}")
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


class TestHorusFoundry(unittest.TestCase):
    def test_foundry_mock_linear_status_and_dry_run(self) -> None:
        from http.server import BaseHTTPRequestHandler, HTTPServer
        import threading

        class MockLinear(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass
            def do_POST(self):
                length = int(self.headers.get("Content-Length", "0"))
                body = json.loads(self.rfile.read(length).decode("utf-8"))
                q = body.get("query", "")
                if "teams" in q:
                    resp = {"data": {"teams": {"nodes": [{"id": "t1", "key": "HRS", "name": "Horus"}]}}}
                elif "states" in q:
                    resp = {"data": {"team": {"states": {"nodes": [
                        {"id": "s1", "name": "∞ Needs Research", "type": "unstarted", "position": 1},
                        {"id": "s2", "name": "∞ Research In Progress", "type": "started", "position": 2},
                        {"id": "s3", "name": "∞ Needs Plan", "type": "unstarted", "position": 3},
                        {"id": "s4", "name": "∞ Needs Implement", "type": "unstarted", "position": 4},
                        {"id": "s5", "name": "∞ Implement In Progress", "type": "started", "position": 5},
                        {"id": "s6", "name": "∞ Needs Validate", "type": "unstarted", "position": 6},
                    ]}}}}
                elif "issues" in q:
                    resp = {"data": {"issues": {"nodes": [
                        {"id": "i2", "identifier": "HRS-2", "title": "Low priority task", "description": "desc2",
                         "priority": 3, "url": "https://linear.app/hrs/HRS-2",
                         "state": {"id": "s1", "name": "∞ Needs Research", "type": "unstarted"}, "labels": {"nodes": []}},
                        {"id": "i1", "identifier": "HRS-1", "title": "Urgent auth fix", "description": "desc1",
                         "priority": 1, "url": "https://linear.app/hrs/HRS-1",
                         "state": {"id": "s4", "name": "∞ Needs Implement", "type": "unstarted"}, "labels": {"nodes": []}},
                    ]}}}
                else:
                    resp = {"data": {}}
                raw = json.dumps(resp).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

        srv = HTTPServer(("127.0.0.1", 0), MockLinear)
        port = srv.server_address[1]
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        try:
            env = dict(os.environ, LINEAR_API_KEY="lin_test", LINEAR_API_URL=f"http://127.0.0.1:{port}/graphql")
            r = subprocess.run(
                [sys.executable, str(FOUNDRY_PY), "run", "--workers", "1", "--once", "--dry-run"],
                env=env, capture_output=True, text=True,
            )
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            # Priority 1 (HRS-1) must be picked before Priority 3 (HRS-2)
            self.assertIn('"issue": "HRS-1"', r.stdout)
            self.assertIn('"stage": "implement"', r.stdout)
            self.assertIn('"branch": "horus/hrs-1-urgent-auth-fix"', r.stdout)
            self.assertIn('"status": "DRY_RUN"', r.stdout)
        finally:
            srv.shutdown()
            srv.server_close()


class TestHorusTodo(unittest.TestCase):
    def test_todo_roundtrip_preserves_notes_git_tracks_analyzes_and_promotes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=str(work), check=True)

            # Seed .todo.md with custom headings and prose notes
            todo = work / ".todo.md"
            todo.write_text("# My Notes\nKeep this note intact.\n\n- [ ] First task\n", encoding="utf-8")

            r = run_py(TODO_PY, "--dir", str(work), "add", "Second task")
            self.assertEqual(r.returncode, 0, r.stderr)
            r = run_py(TODO_PY, "--dir", str(work), "toggle", "1")
            self.assertEqual(r.returncode, 0, r.stderr)

            txt = todo.read_text(encoding="utf-8")
            self.assertIn("# My Notes", txt)
            self.assertIn("Keep this note intact.", txt)
            self.assertIn("- [x] First task", txt)
            self.assertIn("- [ ] Second task", txt)

            # Verify `git add -- .todo.md` staged it in the git index
            ls = subprocess.run(["git", "ls-files", ".todo.md"], cwd=str(work), capture_output=True, text=True)
            self.assertEqual(ls.stdout.strip(), ".todo.md")

            # Verify AI Requirement Analysis prompt includes open & completed tasks
            r = run_py(TODO_PY, "--dir", str(work), "analyze")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("Second task", r.stdout)
            self.assertIn("First task", r.stdout)
            self.assertIn("Conflicts & Redundancy", r.stdout)

            # Verify promote creates/appends plan.py-compatible task_plan.md
            r = run_py(TODO_PY, "--dir", str(work), "promote")
            self.assertEqual(r.returncode, 0, r.stderr)
            tp = (work / "task_plan.md").read_text(encoding="utf-8")
            self.assertIn("- [ ] T1.1 Second task | accept:", tp)

    def test_todo_refuses_to_overwrite_unmanaged_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            (work / ".todo.md").write_text("Unrelated prose document with zero checklists.\n", encoding="utf-8")
            r = run_py(TODO_PY, "--dir", str(work), "--no-git", "add", "Should fail")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("unmanaged-file", r.stderr)


if __name__ == "__main__":
    unittest.main()
