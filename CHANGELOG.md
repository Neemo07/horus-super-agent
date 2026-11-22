# Changelog

## v0.3.7
- **Full `anthropics/skills` curated integration (26 → 31 focused skills):**
  - Upgraded `webapp-testing` (6 files, official `with_server.py` + Playwright examples) and `frontend-design` (2 files) to full upstream editions.
  - Added 5 high-value, non-overlapping skills: `mcp-builder` (11 files, wired to `web-engineer` + `AGENTS.md`), `pdf` (12 files), `docx` (61 files), `xlsx` (53 files), and `pptx` (58 files).
  - Deliberately excluded 12 overlapping or Claude-branded skills (`skill-creator`, `web-artifacts-builder`, `claude-api`, `brand-guidelines`, `academy-guide`, `discernment-nudge`, `internal-comms`, `slack-gif-creator`, `doc-coauthoring`, `theme-factory`, `algorithmic-art`, `canvas-design`) to keep Horus model-agnostic and lean.
  - Tightened frontmatter descriptions on `pdf`, `docx`, `xlsx`, and `pptx` (~2.1 KB saved from the always-on skill catalog) while keeping all bodies, scripts, and references verbatim.
  - Updated `AGENTS.md`, `SKILLS.md`, `README.md`, `scripts/sync_upstream.py`, installers, and added `test_anthropic_skills_full_integration_clean` in `tests/test_horus.py`.

## v0.3.6
- **Full `supabase-postgres-best-practices` upgrade (from `supabase/agent-skills` v1.1.1):**
  - Replaced the condensed offline edition with the full 36-file upstream skill (`.opencode/skills/supabase-postgres-best-practices/`), including all 31 rule reference files across 8 priority categories (`references/*.md`).
  - Tightened the frontmatter description from 803 chars to 247 chars (preserving all trigger keywords) to keep Horus's always-on skill catalog lean.
  - Updated `SKILLS.md`, `README.md`, installers, and added `test_supabase_postgres_best_practices_full_edition` in `tests/test_horus.py`.

## v0.3.5
- **Full `vercel-react-best-practices` upgrade (verbatim from `vercel-labs/agent-skills` v1.0.0):**
  - Replaced the condensed offline edition with the full 76-file upstream skill (`.opencode/skills/vercel-react-best-practices/`), including all 70 rule files across 8 priority categories (`rules/*.md`), compiled `AGENTS.md`, and `metadata.json`.
  - Updated `SKILLS.md`, `README.md`, installers, and added `test_vercel_react_best_practices_full_edition` in `tests/test_horus.py`.

## v0.3.4
- **Full Superpowers v7.0.2 upgrade (carefully merged without duplicates or plugin conflicts):**
  - Replaced the 6 condensed offline Superpowers skills (`brainstorming`, `test-driven-development`, `systematic-debugging`, `using-git-worktrees`, `finishing-a-development-branch`, `writing-skills`) with the full upstream v7.0.2 editions and all companion references/scripts (`visual-companion.md` + visual brainstorming server, `writing-good-tests.md`, `root-cause-tracing.md`, `defense-in-depth.md`, `condition-based-waiting.md`, `find-polluter.sh`, `writing-skills/references/`, `render-graphs.js`).
  - Kept the 8 superseded Superpowers skills and `.opencode/plugins/superpowers.js` excluded so there are zero trigger collisions or `using-superpowers` bootstrap conflicts with Horus `AGENTS.md` / `horus.md`.
  - Adapted all 6 skills cleanly for Horus: native OpenCode `question` polls in `brainstorming` & `finishing-a-development-branch`, bare OpenCode skill IDs (no `superpowers:` prefix), removed `Announce at start` noise, fixed broken `../using-superpowers/` links in `writing-skills`, and routed `brainstorming` handoff to `vibe-spec-plan` + `plan.py`.
  - Protected all Horus-adapted Superpowers skills in `scripts/sync_upstream.py` and added regression test `test_superpowers_v7_full_integration_clean` in `tests/test_horus.py`.

## v0.3.3
- **Full official Graphify v0.9.115 (`graphifyy`) OpenCode integration:**
  - Replaced condensed `graphify-memory` with the verbatim official OpenCode skill (`.opencode/skills/graphify/SKILL.md`) plus all 8 official reference handbooks (`add-watch.md`, `exports.md`, `extraction-spec.md`, `github-and-merge.md`, `hooks.md`, `query.md`, `transcribe.md`, `update.md`).
  - Added `/graphify` slash command (`.opencode/commands/graphify.md`) and updated worker allowlists (`c-engineer`, `re-analyst`, `ui-gui-engineer`, `web-engineer`) from `graphify-memory` to `graphify`.
- **Fixed all Graphify CLI & MCP commands to match `graphifyy` v0.9.115:**
  - `opencode.jsonc`: fixed local MCP command from `["graphify", "--mcp"]` to `["graphify-mcp", "graphify-out/graph.json"]`.
  - `install.ps1`, `install.sh`, `README.md`: updated install hint to `uv tool install --upgrade "graphifyy[mcp]"`.
  - `AGENTS.md`, `horus.md`, `horus-init.md`, `subagent-driven-dev`: replaced `graphify . --no-viz` with `graphify extract . --code-only` and `graphify . --update` with `graphify update .`, and aligned `AGENTS.md` with Graphify's official always-on rules (`graphify query/path/explain/section`, `wiki/index.md`).
- **Validation & tests:** `validate_horus.py` now checks `/graphify` and all 8 Graphify references; `tests/test_horus.py` adds a regression test ensuring zero stale Graphify CLI/MCP strings remain.

## v0.3.2
- **Pruned 8 overlapping/superseded Superpowers skills (34 → 26 focused skills):**
  - Removed `subagent-driven-development`, `using-superpowers`, `executing-plans`, `writing-plans`, `dispatching-parallel-agents`, `verification-before-completion`, `requesting-code-review`, and `receiving-code-review`.
  - Folded `receiving-code-review`'s anti-sycophancy PR feedback rules into `vibe-critique/SKILL.md`.
- **Sharpened skill triggers & cut always-on catalog bloat (~29% smaller):**
  - Narrowed `brainstorming` to lightweight feature design on existing repos (eliminating collision with `vibe-grill`).
  - Trimmed `speed-engineer`'s frontmatter description from 723 chars to ~215 chars while keeping S/M/L sizing and Arabic triggers.
  - Clarified `frontend-design` (web aesthetic/typography) vs `ui-ux-design-systems` (OKLCH tokens, 4/8px grids, WCAG/APCA contrast).
- **Updated routing, allowlists, sync & regression tests:**
  - Updated `AGENTS.md`, `SKILLS.md`, `README.md`, and worker allowlists (`c-engineer`, `ui-gui-engineer`, `web-engineer`) with zero dangling references.
  - Scoped `scripts/sync_upstream.py` `superpowers` group to the 6 kept skills so upstream syncs never re-introduce pruned duplicates.
  - Added regression test in `tests/test_horus.py` verifying every agent skill allowlist target exists and no pruned skills remain.

## v0.3.1
- **Installer & config fixes:**
  - `install.ps1` and `install.sh` now strip JSONC `//` comments and trailing commas when writing a fresh global `opencode.json`, ensuring strict JSON compatibility.
  - Both installers now run `validate_horus.py` in both `project` and `global` modes.
  - Resolved the `model:` frontmatter contradiction: `horus.md`, `/horus-init`, and `subagent-driven-dev` now store session model maps in gitignored `.horus/STATE.md` and warn against committing local `model:` edits; `validate_horus.py` supports `--allow-session-models` and auto-relaxes when `.horus/STATE.md` is present.
- **Permission sandboxing & upstream sync safety:**
  - Added explicit `shell: "*"` deny baselines to all read-only subagents (`architect`, `re-analyst`, `reviewer`) before their narrow allowlists.
  - Expanded `reviewer.md` read-only verification commands for `WEB` pipeline projects (`pytest`, `npm test`, `pnpm test`, `npx vitest run`, `npx tsc --noEmit`, `npx playwright test`).
  - Protected Horus-customized skills (`vibe*`, `brainstorming`) and `/vibe` command in `scripts/sync_upstream.py` so default syncs never silently strip native OpenCode `question` poll upgrades (pass `--force-customized` to override).
- **Hardened Python tooling & test suite:**
  - `plan.py`: added atomic temp-file writes (`os.replace`), cross-platform advisory locking (`fcntl`/`msvcrt`) around state-mutating commands, and SHA-256 verification on `--file` evidence inside `verify`.
  - `validate_horus.py`: switched from `py_compile.compile()` to in-memory `ast.parse()` (zero `__pycache__` pollution), added `migrate-opencode-db.py` syntax coverage, enforced strict `.json` parsing, and added read-only `shell: "*"` deny verification.
  - `migrate-opencode-db.py`: replaced fixed column lists with dynamic `PRAGMA table_info()` intersection and added POSIX-aware lock probing (`fuser`/`lsof`).
  - Polish: updated `architect.md` description for Web/Next.js/Supabase, gave `web-engineer.md` a distinct badge color (`#10b981`), added `vibe-scoped-build` parity to `c-engineer.md` and `ui-gui-engineer.md`, and added `tests/test_horus.py`.

## v0.3
- **Native OpenCode App Poll UI (`question` tool) everywhere:**
  - Enabled `{ "action": "question", "resource": "*", "effect": "allow" }` in `opencode.jsonc` (V2), `"question": "allow"` in `opencode.v1.json` (V1), and `question: allow` in `.opencode/agents/horus.md`.
  - Explicitly denied `question` on all 6 background subagents (`architect`, `c-engineer`, `ui-gui-engineer`, `web-engineer`, `re-analyst`, `reviewer`) and added `DECISION_OPTIONS` to worker Result Envelopes so only `horus` presents clean interactive polls to the user.
  - Added strict OpenCode `question` schema guardrails (`header` ≤ 12 chars, `options[].label` ≤ 30 chars, required non-empty `question` field on every tab, `(Recommended)` first, native `"Type your own answer"` enabled) across `AGENTS.md`, `horus.md`, `vibe`, `vibe-grill`, `vibe-spec-plan`, `vibe-test-gate`, `subagent-driven-dev`, and `brainstorming`.
- **Full `vibe-engineering-playbook` (v1.0.0) merge:**
  - Upgraded all 6 Vibe skills (`vibe`, `vibe-grill`, `vibe-spec-plan`, `vibe-scoped-build`, `vibe-critique`, `vibe-test-gate`) and `/vibe` command from condensed offline editions to the full upstream playbook + OpenCode native poll integration.
  - Bundled all 4 official templates (`AGENTS.template.md`, `AGENTS.template.ar.md`, `PRD.template.md`, `IMPLEMENTATION_PLAN.template.md`) in `.opencode/skills/vibe/templates/` and all 8 bilingual EN/AR handbooks (`workflow-7-stages`, `checklists`, `anti-patterns`, `prompt-blueprints`) in `.opencode/skills/vibe/references/`.
- **4 new Horus slash commands:** `/horus-init`, `/horus-status`, `/horus-resume`, `/horus-review` (alongside upgraded `/vibe`).
- **Automated integrity validator:** added `scripts/validate_horus.py` checking configs, permissions, zero hardcoded `model:` fields, skills, commands, merged Vibe assets, and Python script syntax.
- **Safer upgrades:** `install.sh` (`--force-config`) and `install.ps1` (`-ForceConfig`) now upgrade `AGENTS.md` and `opencode.jsonc` with `.bak` backups and run `validate_horus.py` automatically.
- **Fixes:** added missing `web-engineer` to `AGENTS.md` kickoff subagent list and clarified `subagent-driven-dev` precedence over `subagent-driven-development`.

## v0.2
- Added 25 skills: speed-engineer, frontend-design, webapp-testing, vercel-react-best-practices, supabase-postgres-best-practices, 6 vibe skills (+ `/vibe` command), 14 superpowers skills. See SKILLS.md for provenance.
- New `web-engineer` subagent; `horus` gains Step 0 (classify/discover) and a `WEB` pipeline (architect → web-engineer → webapp-testing → reviewer → vibe-test-gate).
- `architect`, `reviewer`, `c-engineer`, `ui-gui-engineer` wired to the new skills; `subagent-driven-dev` knows `web-engineer`.
- `AGENTS.md`: compact Skill Routing & Precedence table (Horus rules win over superpowers/vibe equivalents).
- `scripts/sync_upstream.py`: replace offline editions with verbatim upstream skills (backup + lock file).
- Installers now copy `commands/` and `sync_upstream.py`, and hint at the Playwright setup.
