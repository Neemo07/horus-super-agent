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
        self.assertEqual(len(playbooks), 23, f"Expected 23 design-engineering playbooks, got {len(playbooks)}")
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

    def test_v060_frontier_intelligence_contracts(self) -> None:
        agents_md = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Parallel-first execution", agents_md)
        self.assertIn("4-Layer Memory", agents_md)
        horus_md = (REPO_ROOT / ".opencode" / "agents" / "horus.md").read_text(encoding="utf-8")
        self.assertIn("v0.8.9", horus_md)
        self.assertIn("Parallel-first discovery", horus_md)
        self.assertIn("horus-memory", horus_md)
        reviewer_md = (REPO_ROOT / ".opencode" / "agents" / "reviewer.md").read_text(encoding="utf-8")
        for tool in ("mypy *", "ruff check*", "bandit *", "semgrep *", "cargo test*", "go test*"):
            self.assertIn(tool, reviewer_md, f"reviewer.md missing read-only verifier: {tool}")
        for agent_name in ("architect.md", "reviewer.md", "c-engineer.md", "web-engineer.md", "ui-gui-engineer.md", "re-analyst.md"):
            body = (REPO_ROOT / ".opencode" / "agents" / agent_name).read_text(encoding="utf-8")
            self.assertIn("Parallel-First", body, f"{agent_name} missing Parallel-First grounding rule")

    def test_antigravity_project_and_global_install(self) -> None:
        if os.name == "nt":
            self.skipTest("bash installer test runs on POSIX")
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            proj.mkdir()
            r1 = subprocess.run(["bash", str(INSTALL_SH), "project", str(proj), "--harness", "antigravity"], capture_output=True, text=True)
            self.assertEqual(r1.returncode, 0, r1.stdout + r1.stderr)
            self.assertIn("HORUS VALIDATION PASSED (antigravity/project)", r1.stdout)
            self.assertTrue((proj / "GEMINI.md").exists())
            self.assertTrue((proj / ".agents" / "rules" / "horus.md").exists())
            self.assertEqual(len(list((proj / ".agents" / "workflows").glob("*.md"))), 18)
            mcp = json.loads((proj / ".agents" / "mcp_config.json").read_text(encoding="utf-8"))
            self.assertIn("horus-context-mode", mcp["mcpServers"])

            # Global mode must non-destructively preserve existing mcpServers (e.g. ai-memory)
            fake_home = Path(tmp) / "home"
            existing_cfg = fake_home / ".gemini" / "config" / "mcp_config.json"
            existing_cfg.parent.mkdir(parents=True)
            existing_cfg.write_text(json.dumps({"mcpServers": {"ai-memory": {"serverUrl": "http://127.0.0.1:49374/mcp"}}}), encoding="utf-8")
            r2 = subprocess.run(["bash", str(INSTALL_SH), "global", "--harness", "antigravity"], env=dict(os.environ, HOME=str(fake_home)), capture_output=True, text=True)
            self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
            self.assertIn("HORUS VALIDATION PASSED (antigravity/global)", r2.stdout)
            merged = json.loads(existing_cfg.read_text(encoding="utf-8"))
            self.assertIn("ai-memory", merged["mcpServers"])
            self.assertIn("horus-context-mode", merged["mcpServers"])

    def test_dsh_project_global_and_all_harnesses_install(self) -> None:
        if os.name == "nt":
            self.skipTest("bash installer test runs on POSIX")
        import yaml
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "dsh_proj"
            proj.mkdir()
            r1 = subprocess.run(["bash", str(INSTALL_SH), "project", str(proj), "--harness", "dsh"], capture_output=True, text=True)
            self.assertEqual(r1.returncode, 0, r1.stdout + r1.stderr)
            self.assertIn("HORUS VALIDATION PASSED (dsh/project)", r1.stdout)
            self.assertTrue((proj / "AGENTS.md").exists())
            self.assertTrue((proj / "skills" / "horus-memory" / "SKILL.md").exists())
            patch_data = yaml.safe_load((proj / ".dsh" / "cordis.patch.yml").read_text(encoding="utf-8"))
            self.assertIsInstance(patch_data, list)
            self.assertEqual(patch_data[0]["insert"][0]["name"], "@deepseek-ai/dsh-mcp-client")

            # Global DSH mode using custom DSH_HOME
            dsh_home = Path(tmp) / "dsh_home"
            r2 = subprocess.run(["bash", str(INSTALL_SH), "global", "--harness", "dsh"], env=dict(os.environ, DSH_HOME=str(dsh_home)), capture_output=True, text=True)
            self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
            self.assertIn("HORUS VALIDATION PASSED (dsh/global)", r2.stdout)
            gpatch = yaml.safe_load((dsh_home / "horus" / "cordis.patch.yml").read_text(encoding="utf-8"))
            self.assertEqual(gpatch[0]["insert"][0]["id"], "horus-context-mode")

            # Multi-harness --harness all in one command
            all_proj = Path(tmp) / "all_proj"
            all_proj.mkdir()
            r3 = subprocess.run(["bash", str(INSTALL_SH), "project", str(all_proj), "--harness", "all", "--force-config"], capture_output=True, text=True)
            self.assertEqual(r3.returncode, 0, r3.stdout + r3.stderr)
            self.assertIn("HORUS VALIDATION PASSED (project)", r3.stdout)
            self.assertIn("HORUS VALIDATION PASSED (antigravity/project)", r3.stdout)
            self.assertIn("HORUS VALIDATION PASSED (dsh/project)", r3.stdout)
            self.assertIn(".opencode/skills/", (all_proj / "AGENTS.md").read_text(encoding="utf-8"))
            self.assertTrue((all_proj / ".dsh" / "AGENTS.md").exists())

    def test_tri_harness_zero_dangling_opencode_paths_and_validator(self) -> None:
        if os.name == "nt":
            self.skipTest("bash installer test runs on POSIX")
        with tempfile.TemporaryDirectory() as tmp:
            ag_dir = Path(tmp) / "ag_only"
            ag_dir.mkdir()
            r1 = subprocess.run(["bash", str(INSTALL_SH), "project", str(ag_dir), "--harness", "antigravity"], capture_output=True, text=True)
            self.assertEqual(r1.returncode, 0, r1.stdout + r1.stderr)
            plan_skill = (ag_dir / ".agents" / "skills" / "planning-with-evidence" / "SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn(".opencode/skills/", plan_skill)
            self.assertIn(".agents/skills/", plan_skill)
            rv1 = subprocess.run([sys.executable, str(ag_dir / "scripts" / "validate_horus.py")], capture_output=True, text=True)
            self.assertEqual(rv1.returncode, 0, rv1.stdout + rv1.stderr)
            self.assertIn("HORUS VALIDATION PASSED (antigravity/project)", rv1.stdout)

            dsh_dir = Path(tmp) / "dsh_only"
            dsh_dir.mkdir()
            r2 = subprocess.run(["bash", str(INSTALL_SH), "project", str(dsh_dir), "--harness", "dsh"], capture_output=True, text=True)
            self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
            dsh_plan_skill = (dsh_dir / "skills" / "planning-with-evidence" / "SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn(".opencode/skills/", dsh_plan_skill)
            rv2 = subprocess.run([sys.executable, str(dsh_dir / "scripts" / "validate_horus.py")], capture_output=True, text=True)
            self.assertEqual(rv2.returncode, 0, rv2.stdout + rv2.stderr)
            self.assertIn("HORUS VALIDATION PASSED (dsh/project)", rv2.stdout)

    def test_foundry_accepts_tri_harness_runners(self) -> None:
        r = run_py(REPO_ROOT / "scripts" / "horus_foundry.py", "run", "--help")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("--runner", r.stdout)
        self.assertIn("antigravity", r.stdout)
        self.assertIn("dsh", r.stdout)

    def test_standalone_global_all_harnesses_works_for_every_app(self) -> None:
        if os.name == "nt":
            self.skipTest("bash installer test runs on POSIX")
        import yaml
        with tempfile.TemporaryDirectory() as tmp:
            fake_home = Path(tmp) / "home"
            dsh_home = Path(tmp) / "dsh_home"
            # Pre-populate user GEMINI.md, Antigravity IDE mcp_config.json, and a DSH profile cordis.patch.yml
            (fake_home / ".gemini").mkdir(parents=True)
            (fake_home / ".gemini" / "GEMINI.md").write_text("# My Personal Gemini Notes\n", encoding="utf-8")
            (fake_home / ".gemini" / "antigravity").mkdir(parents=True)
            (fake_home / ".gemini" / "antigravity" / "mcp_config.json").write_text(
                json.dumps({"mcpServers": {"ai-memory": {"serverUrl": "http://127.0.0.1:49374/mcp"}}}),
                encoding="utf-8",
            )
            prof = dsh_home / "profiles" / "standard" / "cordis.patch.yml"
            prof.parent.mkdir(parents=True)
            prof.write_text("- insert:\n    - id: existing-plugin\n      name: '@deepseek-ai/dsh-todo-list'\n", encoding="utf-8")

            env = dict(os.environ, HOME=str(fake_home), DSH_HOME=str(dsh_home))
            # Run twice to verify full idempotency
            for _ in range(2):
                r = subprocess.run(
                    ["bash", str(INSTALL_SH), "global", "--harness", "all", "--apply-dsh-profiles"],
                    env=env,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

            # Verify OpenCode global standalone
            self.assertTrue((fake_home / ".config" / "opencode" / "opencode.json").exists())
            # Verify Antigravity global standalone (preserved user GEMINI.md + merged BOTH mcp_config.json files)
            gem_txt = (fake_home / ".gemini" / "GEMINI.md").read_text(encoding="utf-8")
            self.assertIn("# My Personal Gemini Notes", gem_txt)
            self.assertEqual(gem_txt.count("<!-- HORUS:BEGIN -->"), 1)
            ide_mcp = json.loads((fake_home / ".gemini" / "antigravity" / "mcp_config.json").read_text(encoding="utf-8"))
            self.assertIn("ai-memory", ide_mcp["mcpServers"])
            self.assertIn("horus-context-mode", ide_mcp["mcpServers"])
            # Verify DSH global standalone (preserved existing plugin, wired horus-context-mode once, valid YAML)
            dsh_agents = (dsh_home / "AGENTS.md").read_text(encoding="utf-8")
            self.assertEqual(dsh_agents.count("<!-- HORUS:BEGIN -->"), 1)
            prof_txt = prof.read_text(encoding="utf-8")
            self.assertEqual(prof_txt.count("id: horus-context-mode"), 1)
            prof_data = yaml.safe_load(prof_txt)
            self.assertEqual(len(prof_data), 2)

    def test_standalone_global_resolves_all_scripts_skills_plugins_for_all_3_apps(self) -> None:
        if os.name == "nt":
            self.skipTest("bash installer test runs on POSIX")
        # Verify horus-memory bundles hook templates for all 3 apps
        hm_refs = REPO_ROOT / ".opencode" / "skills" / "horus-memory" / "references"
        for hdir in ("opencode-hooks", "antigravity-hooks", "dsh-hooks"):
            self.assertGreaterEqual(len(list((hm_refs / hdir).glob("*"))), 10, f"Missing hook templates in {hdir}")

        with tempfile.TemporaryDirectory() as tmp:
            fake_home = Path(tmp) / "home"
            dsh_home = Path(tmp) / "dsh_home"
            brand_new_app = Path(tmp) / "brand_new_app"
            fake_home.mkdir()
            brand_new_app.mkdir()
            env = dict(os.environ, HOME=str(fake_home), DSH_HOME=str(dsh_home))

            r = subprocess.run(
                ["bash", str(INSTALL_SH), "global", "--harness", "all", "--apply-dsh-profiles"],
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

            # Check each of the 3 global installs has exact absolute script & dashboard paths that actually exist on disk
            checks = [
                (fake_home / ".config" / "opencode", fake_home / ".config" / "opencode" / "skills", fake_home / ".config" / "opencode" / "scripts"),
                (fake_home / ".gemini" / "config", fake_home / ".gemini" / "config" / "skills", fake_home / ".gemini" / "config" / "scripts"),
                (dsh_home / "horus", dsh_home / "skills", dsh_home / "horus" / "scripts"),
            ]
            for base_dir, skills_dir, scripts_dir in checks:
                todo_skill = (skills_dir / "horus-todo" / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn((scripts_dir / "horus_todo.py").as_posix(), todo_skill)
                ctx_skill = (skills_dir / "horus-context-mode" / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn((base_dir / "context-mode" / "dashboard" / "server.mjs").as_posix(), ctx_skill)
                plan_py = skills_dir / "planning-with-evidence" / "scripts" / "plan.py"
                self.assertTrue(plan_py.exists())
                # Actually execute installed scripts from inside an empty brand_new_app directory!
                for sc in (plan_py, scripts_dir / "horus_todo.py", scripts_dir / "horus_foundry.py"):
                    res = subprocess.run([sys.executable, str(sc), "--help"], cwd=str(brand_new_app), capture_output=True, text=True)
                    self.assertEqual(res.returncode, 0, f"Standalone run failed for {sc}: {res.stderr}")

    def test_ai_design_skills_figma_and_landing_page_zero_bloat(self) -> None:
        de_refs = REPO_ROOT / ".opencode" / "skills" / "design-engineering" / "references"
        fd = de_refs / "figma-designer" / "SKILL.md"
        lp = de_refs / "landing-page-design" / "SKILL.md"
        self.assertTrue(fd.exists(), "Missing figma-designer playbook")
        self.assertTrue(lp.exists(), "Missing landing-page-design playbook")
        # Must NOT exist as top-level skills (zero catalog bloat)
        self.assertFalse((REPO_ROOT / ".opencode" / "skills" / "figma-designer").exists())
        self.assertFalse((REPO_ROOT / ".opencode" / "skills" / "landing-page-design").exists())
        # Must include OpenCode question tool integration and zero-overlap scope
        self.assertIn("question", lp.read_text(encoding="utf-8"))
        self.assertIn("ui-ux-design-systems", lp.read_text(encoding="utf-8"))
        self.assertIn("question", fd.read_text(encoding="utf-8"))

    def test_agent_reach_integration_zero_bloat_and_signal_only(self) -> None:
        ar = REPO_ROOT / ".opencode" / "skills" / "agent-reach"
        sm = ar / "SKILL.md"
        self.assertTrue(sm.exists())
        self.assertTrue((REPO_ROOT / ".opencode" / "commands" / "reach.md").exists())
        body = sm.read_text(encoding="utf-8")
        self.assertNotIn("{{VERSION}}", body)
        self.assertIn("question", body)
        self.assertIn("horus-context-mode", body)
        for ref in ("capabilities.md", "maintenance.md", "sessions.md"):
            self.assertTrue((ar / "references" / ref).exists(), f"Missing agent-reach ref: {ref}")

    def test_v076_xhigh_deep_reasoning_and_foundry_variant(self) -> None:
        agents_md = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("xhigh", agents_md)
        self.assertIn("Competing hypotheses", agents_md)
        self.assertIn("Adversarial self-refutation", agents_md)
        horus_md = (REPO_ROOT / ".opencode" / "agents" / "horus.md").read_text(encoding="utf-8")
        self.assertIn("variant: high", horus_md)
        r = run_py(REPO_ROOT / "scripts" / "horus_foundry.py", "run", "--help")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("--variant", r.stdout)

    def test_v078_model_agnostic_reasoning_amplifier(self) -> None:
        agents_md = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for needle in ("Reasoning Amplifier", "4-Line Pre-Edit Contract", "Hard 2-Strike Diagnosis Reset", "5-Point Pre-Delivery Self-Check"):
            self.assertIn(needle, agents_md)
        for wf in ("horus.md", "c-engineer.md", "web-engineer.md", "ui-gui-engineer.md"):
            body = (REPO_ROOT / ".opencode" / "agents" / wf).read_text(encoding="utf-8")
            self.assertIn("Reasoning Amplifier", body, f"{wf} missing Reasoning Amplifier")

    def test_vibe_wired_with_system_design_and_ui_design_systems(self) -> None:
        vsp = (REPO_ROOT / ".opencode" / "skills" / "vibe-spec-plan" / "SKILL.md").read_text(encoding="utf-8")
        vsb = (REPO_ROOT / ".opencode" / "skills" / "vibe-scoped-build" / "SKILL.md").read_text(encoding="utf-8")
        for needle in ("scalability-and-system-design.md", "domain-modeling/SKILL.md", "ui-ux-design-systems", "figma-designer/SKILL.md"):
            self.assertIn(needle, vsp, f"vibe-spec-plan missing {needle}")
        for needle in ("ui-ux-design-systems", "break-ui/SKILL.md", "webapp-testing", "senior-engineering-partner"):
            self.assertIn(needle, vsb, f"vibe-scoped-build missing {needle}")

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


    def test_v080_core_skills_upgraded_cleanly(self):
        """v0.8.9: Verify all 8 upgraded core Horus skills keep valid frontmatter and key additions."""
        expected_markers = {
            "anti-hallucination-harness": ["False-Negative Search Guard", "ctx_search", "4-Line Pre-Edit Contract"],
            "native-gui-architecture": ["DWMWA_USE_IMMERSIVE_DARK_MODE", "WM_DPICHANGED", "D2DERR_RECREATE_TARGET"],
            "planning-with-evidence": ["SHA-256", "memory_handoff_begin", "os.replace"],
            "modern-c-mastery": ["SIZE_MAX", "/fsanitize=address", "libFuzzer"],
            "reverse-engineer-anything": ["OBSERVED", "INFERRED", "graphify"],
            "cpp20-win32-re": ["SetWindowLongPtr", "<intrin.h>", "uintptr_t"],
            "subagent-driven-dev": ["variant: high", "parentID", "INVARIANTS"],
            "horus-foundry": ["--runner", "--variant high", "HORUS_FOUNDRY_VARIANT=high", "antigravity"],
        }
        import yaml
        for skill, markers in expected_markers.items():
            p = REPO_ROOT / ".opencode" / "skills" / skill / "SKILL.md"
            raw = p.read_text(encoding="utf-8")
            self.assertTrue(raw.startswith("---\n"), f"{skill} missing YAML frontmatter")
            fm_end = raw.index("\n---\n", 4)
            meta = yaml.safe_load(raw[4:fm_end])
            self.assertEqual(meta["name"], skill)
            self.assertLessEqual(len(meta["description"]), 150, f"{skill} description > 150c")
            for m in markers:
                self.assertIn(m, raw, f"{skill} missing v0.8.9 marker: {m}")

    def test_v082_batch2_skills_upgraded_cleanly(self):
        """v0.8.9: Verify all 10 Batch-2 upgraded Horus skills keep valid frontmatter and key additions."""
        expected_markers = {
            "security-audit": ["OBSERVED", "THEORETICAL", "audit-report-format.md"],
            "ui-ux-design-systems": ["margin-inline", "clamp(", "WCAG 2.2 AA"],
            "horus-todo": ["Decision Boundary", "$DSH_HOME/horus/scripts/horus_todo.py", "promote"],
            "horus-context-mode": ["journal_mode = WAL", "~16 KB", "4-Layer Memory Boundary"],
            "horus-memory": ["Write Hygiene", "memory_handoff_begin", "parentID"],
            "horus-next-steps": ["Zero Generic Filler", "Antigravity / DeepSeek Harness", "Next Step"],
            "vibe-grill": ["10 Core Dimensions", "System Design Boundaries", "UI & Locale System"],
            "vibe-critique": ["Pre-Critique Grounding", "Adversarial Self-Refutation", "security-audit"],
            "vibe-test-gate": ["Zero-Waiver Security Floor", "libFuzzer", "verify --rerun"],
            "agent-architecture-reference": ["Horus Subsystem Quick-Lookup Map", "horus-context-mode", "install_harness.py"],
        }
        import yaml
        for skill, markers in expected_markers.items():
            p = REPO_ROOT / ".opencode" / "skills" / skill / "SKILL.md"
            raw = p.read_text(encoding="utf-8")
            self.assertTrue(raw.startswith("---\n"), f"{skill} missing YAML frontmatter")
            fm_end = raw.index("\n---\n", 4)
            meta = yaml.safe_load(raw[4:fm_end])
            self.assertEqual(meta["name"], skill)
            self.assertLessEqual(len(meta["description"]), 150, f"{skill} description > 150c")
            for m in markers:
                self.assertIn(m, raw, f"{skill} missing v0.8.9 marker: {m}")

    def test_v083_all_42_skills_upgraded_cleanly(self):
        """v0.8.9: Verify all 24 Batch-3 upstream/router skills include Horus Super-Upgrade gates and valid frontmatter."""
        batch3 = [
            "brainstorming", "systematic-debugging", "test-driven-development",
            "using-git-worktrees", "finishing-a-development-branch", "writing-skills",
            "senior-engineering-partner", "engineering-craft", "speed-engineer",
            "vercel-react-best-practices", "supabase-postgres-best-practices",
            "mcp-builder", "webapp-testing", "design-engineering", "frontend-design",
            "graphify", "agent-reach", "vibe", "vibe-spec-plan", "vibe-scoped-build",
            "docx", "pdf", "pptx", "xlsx",
        ]
        import yaml
        for skill in batch3:
            p = REPO_ROOT / ".opencode" / "skills" / skill / "SKILL.md"
            raw = p.read_text(encoding="utf-8")
            self.assertTrue(raw.startswith("---\n"), f"{skill} missing YAML frontmatter")
            fm_end = raw.index("\n---\n", 4)
            meta = yaml.safe_load(raw[4:fm_end])
            self.assertEqual(meta["name"], skill)
            self.assertLessEqual(len(meta["description"]), 150, f"{skill} description > 150c")
            self.assertIn("## Horus Super-Upgrade", raw, f"{skill} missing Horus Super-Upgrade section")

    def test_v084_taskmaster_promax_integration(self):
        """v0.8.9: Verify TaskMasterProMax upgraded dashboard, Foundry loop presets, RPG method, bridge, and zero catalog bloat."""
        # 1. Upgraded dashboard files + /portfolio command
        for f in ("server.mjs", "model.mjs", "index.html", "app.mjs", "styles.css", "demo.mjs"):
            self.assertTrue((REPO_ROOT / ".opencode" / "dashboard" / f).exists(), f"Missing dashboard/{f}")
        model_js = (REPO_ROOT / ".opencode" / "dashboard" / "model.mjs").read_text(encoding="utf-8")
        for fn in ("parseHorusPlan", "parseHorusTodo", "horus-plan", "taskmaster", "[PROVEN]"):
            self.assertIn(fn, model_js)
        self.assertTrue((REPO_ROOT / ".opencode" / "commands" / "portfolio.md").exists())

        # 2. RPG method & TaskMasterProMax bridge references (zero new top-level skills)
        self.assertTrue((REPO_ROOT / ".opencode" / "skills" / "vibe-spec-plan" / "references" / "rpg-method.md").exists())
        self.assertTrue((REPO_ROOT / ".opencode" / "skills" / "planning-with-evidence" / "references" / "taskmaster-promax-bridge.md").exists())

        # 3. horus_foundry.py loop --dry-run works locally without LINEAR_API_KEY
        env = dict(os.environ)
        env.pop("LINEAR_API_KEY", None)
        r = subprocess.run(
            [sys.executable, str(FOUNDRY_PY), "loop", "--preset", "test-coverage", "-n", "3", "--runner", "opencode", "--variant", "high", "--dry-run"],
            capture_output=True, text=True, check=True, env=env,
        )
        data = json.loads(r.stdout.strip())
        self.assertEqual(data["mode"], "loop")
        self.assertEqual(data["preset"], "test-coverage")
        self.assertEqual(data["variant"], "high")
        self.assertTrue(data["dry_run"])

        # 4. Missing --prompt-file fails cleanly with exit code 1 (no traceback)
        r_bad = subprocess.run(
            [sys.executable, str(FOUNDRY_PY), "loop", "--prompt-file", "/nonexistent/prompt.md", "--dry-run"],
            capture_output=True, text=True, env=env,
        )
        self.assertEqual(r_bad.returncode, 1)
        self.assertIn("--prompt-file not found", r_bad.stderr)

        # 5. Dashboard HTML uses Horus Portfolio branding & mentions task_plan.md
        idx_html = (REPO_ROOT / ".opencode" / "dashboard" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Horus<span>Portfolio</span>", idx_html)
        self.assertIn("task_plan.md", idx_html)


    def test_v086_modern_web_guidance_integration(self):
        """v0.8.9: Verify modern-web-guidance skill, offline references, /modernize command, agent wiring, and <=5200c catalog cap."""
        mwg = REPO_ROOT / ".opencode" / "skills" / "modern-web-guidance"
        raw = (mwg / "SKILL.md").read_text(encoding="utf-8")
        import yaml
        meta = yaml.safe_load(raw[4:raw.index("\n---\n", 4)])
        self.assertEqual(meta["name"], "modern-web-guidance")
        self.assertLessEqual(len(meta["description"]), 150)
        for marker in ("npx -y modern-web-guidance@latest", "legacy-scan", "ctx_search", "webapp-testing", "Zero-Overlap"):
            self.assertIn(marker, raw)
        self.assertTrue((mwg / "references" / "platform-cheatsheet.md").exists())
        self.assertTrue((mwg / "references" / "legacy-modernization.md").exists())
        self.assertTrue((REPO_ROOT / ".opencode" / "commands" / "modernize.md").exists())
        for ag in ("web-engineer.md", "ui-gui-engineer.md"):
            self.assertIn("modern-web-guidance", (REPO_ROOT / ".opencode" / "agents" / ag).read_text(encoding="utf-8"))
        # Verify total catalog stays <= 5200 chars across all 43 skills
        all_skills = sorted((REPO_ROOT / ".opencode" / "skills").glob("*/SKILL.md"))
        self.assertEqual(len(all_skills), 44)
        total_chars = sum(len(yaml.safe_load(s.read_text(encoding="utf-8")[4:s.read_text(encoding="utf-8").index("\n---\n", 4)])["description"]) for s in all_skills)
        self.assertLessEqual(total_chars, 5200, f"Catalog exceeded 5200c: {total_chars}")

    def test_v088_open_code_review_integration(self):
        """v0.8.9: Verify unified open-code-review skill, review_pr.py, V1/V2 plugin, /ocr-review command, and <=5200c cap."""
        ocr = REPO_ROOT / ".opencode" / "skills" / "open-code-review"
        raw = (ocr / "SKILL.md").read_text(encoding="utf-8")
        import yaml
        meta = yaml.safe_load(raw[4:raw.index("\n---\n", 4)])
        self.assertEqual(meta["name"], "open-code-review")
        self.assertLessEqual(len(meta["description"]), 150)
        for marker in ("ocr review --audience agent", "ocr delegate preview", "review_pr.py", "Zero-Overlap", "ctx_search"):
            self.assertIn(marker, raw)
        self.assertTrue((ocr / "scripts" / "review_pr.py").exists())
        self.assertTrue((ocr / "references" / "native-and-pr.md").exists())
        self.assertTrue((ocr / "references" / "delegate-mode.md").exists())
        self.assertTrue((ocr / "references" / "opencode-plugin" / "open-code-review.ts").exists())
        self.assertTrue((REPO_ROOT / ".opencode" / "commands" / "ocr-review.md").exists())
        self.assertIn("open-code-review", (REPO_ROOT / ".opencode" / "agents" / "reviewer.md").read_text(encoding="utf-8"))
        all_skills = sorted((REPO_ROOT / ".opencode" / "skills").glob("*/SKILL.md"))
        self.assertEqual(len(all_skills), 44)
        total_chars = sum(len(yaml.safe_load(s.read_text(encoding="utf-8")[4:s.read_text(encoding="utf-8").index("\n---\n", 4)])["description"]) for s in all_skills)
        self.assertLessEqual(total_chars, 5200, f"Catalog exceeded 5200c: {total_chars}")

if __name__ == "__main__":
    unittest.main()
