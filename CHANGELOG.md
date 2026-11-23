# Changelog

## v0.5.0
- **Zero-Catalog-Bloat & Zero-Overlap Optimization Pass:**
  - Tightened all 39 skill frontmatter descriptions to a strict **≤ 145-character** budget, slashing always-on skill catalog overhead by **~44%** (`8,501 chars / ~2,125 tokens` → `~4,750 chars / ~1,185 tokens`) with mutually exclusive trigger boundaries across `speed-engineer` / `vercel-react-best-practices` / `supabase-postgres-best-practices`, `frontend-design` / `ui-ux-design-systems` / `design-engineering`, and `writing-skills` / `engineering-craft`.
  - Resolved the `prototype` sub-playbook name collision by renaming `design-engineering/references/prototype` → `ui-prototype` and `engineering-craft/references/prototype` → `tech-prototype`.
  - Enforced both invariants mechanically in `scripts/validate_horus.py` (150-char per-skill description cap + zero duplicate reference playbook names) and `tests/test_horus.py` (`test_zero_catalog_bloat_and_zero_playbook_collisions`).

## v0.4.8
- **Added `agent-architecture-reference` (17-chapter EN/ZH coding-agent architecture deep-dive):**
  - Bundled all 19 EN and 19 ZH architecture chapters under `.opencode/skills/agent-architecture-reference/references/{en,zh-CN}/` (skipping the duplicate VitePress website build to keep Horus lean).
  - Designed as a progressive-disclosure OpenCode router (`SKILL.md`) paired with Horus Context Mode (`ctx_search`) so agents query exact sections on demand without flooding the context window.
  - Wired into `AGENTS.md`, `SKILLS.md`, `README.md`, installers, and added `test_agent_architecture_reference_bilingual_chapters` in `tests/test_horus.py`.

## v0.4.7
- **Added `security-audit` (defensive AppSec & hardening skill) + `/security` slash command:**
  - Covers authorized, strictly defensive auditing across Web/API/Auth (OWASP, RLS, JWT/OAuth2, SSRF, race conditions), C/C++20/Win32 memory safety & compiler mitigations (`/GS`, `/guard:cf`, ASan/UBSan, defensive `libFuzzer`), and CI/CD, supply-chain, container, and crypto hygiene.
  - Produces CWE-grounded severity-ranked `file:line` remediation tables and integrates with OpenCode's native `question` tool (`Sec Scope` / `Sec Audit`).
  - Wired into `c-engineer.md`, `web-engineer.md`, `AGENTS.md`, `validate_horus.py`, `SKILLS.md`, `README.md`, and `tests/test_horus.py`.

## v0.4.6
- **Added `engineering-craft` (curated 18-playbook Real Engineers suite from `mattpocock/skills`, MIT) + `/craft` slash command:**
  - Bundled 18 high-value, non-overlapping playbooks (54 files) inside `.opencode/skills/engineering-craft/references/` behind a single progressive-disclosure OpenCode router (`SKILL.md`): `codebase-design`, `improve-codebase-architecture`, `domain-modeling`, `setup-ts-deep-modules`, `wayfinder`, `to-spec`, `to-tickets`, `pr`, `triage`, `retro`, `wizard`, `diagnosing-bugs`, `prototype`, `research`, `writing-for-agents`, `setup-pre-commit`, `teach`, and `to-questionnaire`.
  - Deliberately excluded overlapping/Claude-only/deprecated skills (`tdd`, `code-review`, `grill-me`, `handoff`, `implement`, `chief-of-staff`, `software-factory`, `git-guardrails-claude-code`, `claude-handoff`, `ask-matt`, `deprecated/*`) so Horus stays collision-free and lean.
  - Replaced Claude-only `AskUserQuestion` and `.claude/skills/` references with OpenCode's native `question` tool and `.opencode/skills/`, wired into `c-engineer.md`, `web-engineer.md`, `AGENTS.md`, `validate_horus.py`, `SKILLS.md`, `README.md`, and `tests/test_horus.py`.

## v0.4.5
- **Added `design-engineering` (full 20-playbook Design Engineering suite from `emilkowalski/skills`, MIT) + `/design` slash command:**
  - Bundled all 20 full playbooks (29 files) and both cheatsheets (`ui-cheatsheet.md`, `performance-cheatsheet.md`) inside `.opencode/skills/design-engineering/references/` behind a single progressive-disclosure OpenCode router (`SKILL.md`), avoiding ~4 KB of always-on catalog bloat while preserving 100% of the upstream craft depth.
  - Covers web & Expo animations, spring physics, choreography, 60/120fps motion performance, gestures, animation review/audit/removal, `break-ui` stress-testing, multi-variant prototyping, `learn-taste` (`DESIGN.md` adapted for OpenCode `AGENTS.md` with Claude `~/.claude/projects/` removed), `pick-ui-library`, Sonner, Apple design, mobile-native web, and modern Swift.
  - Wired into `ui-gui-engineer.md`, `web-engineer.md`, `AGENTS.md`, `validate_horus.py`, `SKILLS.md`, `README.md`, and `tests/test_horus.py`.

## v0.4.4
- **Upgraded `ui-ux-design-systems` with Design System Audit, Documentation & Extend modes:**
  - Folded Audit, Documentation, and Extend workflows directly into `.opencode/skills/ui-ux-design-systems/SKILL.md` (zero duplicate skill bloat; immediately available to `horus`, `architect`, `ui-gui-engineer`, `web-engineer`, and `reviewer`).
  - Upgraded Audit Mode with `graphify query` + `ctx_search` `file:line` scanning, severity-ranked findings (`BLOCKER`/`MAJOR`/`MINOR`), and OpenCode native `question` polls (`DS Mode` / `DS Audit`); upgraded Documentation Mode with full 7-state matrix, ARIA/keyboard contract, and Do/Don't code pairs; upgraded Extend Mode with primitive reuse, dark/light + RTL coverage, `findings.md` trade-offs, and Playwright verification.
  - Stripped third-party promotional attribution footers to preserve Horus's signal-only output standard, and added `test_design_system_audit_document_extend_merged_cleanly` in `tests/test_horus.py`.

## v0.4.3
- **Added Horus Todo (upgraded, zero-dependency OpenCode port of `deepseek-ai/dsh-todo-list`, MIT):**
  - Created `scripts/horus_todo.py` — per-project git-tracked `.todo.md` checklist manager preserving all non-checklist headings/notes verbatim, refusing to clobber unmanaged `.todo.md` files, and auto-staging via `git add -- .todo.md` (never auto-commits).
  - **Key upgrades over original `dsh-todo-list`:** zero-dependency OpenCode CLI (`list`, `add`, `toggle`, `edit`, `remove`, `analyze`), 1-click **AI Requirement Analysis** integrated with OpenCode's native `question` tool, **`promote` bridge** into `task_plan.md` (`plan.py` proof-gated tasks), and an optional zero-dependency live-reloading local web sidebar (`serve --port 4178`).
  - Added `.opencode/skills/horus-todo/SKILL.md`, `/horus-todo` slash command, `AGENTS.md` routing, installer coverage (`install.ps1` / `install.sh`), `validate_horus.py` checks, and `TestHorusTodo` unit tests in `tests/test_horus.py`.

## v0.4.2
- **Added Horus Foundry (upgraded, zero-dependency OpenCode port of `@leixusam/foundry`, MIT):**
  - Created `scripts/horus_foundry.py` — a Python 3.8+ stdlib orchestrator that runs parallel background OpenCode agents (`opencode run --agent horus`) using Linear as a mobile-friendly todo list and state machine (`∞ Needs Research` → `Spec` → `Plan` → `Implement` → `Validate` → `Awaiting Merge` / `Done` | `∞ Blocked`, plus `oneshot` mode).
  - **Key upgrades over original Foundry:** zero npm dependencies / zero build step (direct Linear GraphQL API), 0-token deterministic Linear Reader/Claimer & Writer (saves 2 LLM calls per ticket), true parallel execution via isolated `git worktree` per ticket (`.horus/foundry/worktrees/<KEY>`), and full OpenCode model/provider independence.
  - Added `.opencode/skills/horus-foundry/SKILL.md`, `/horus-foundry` slash command, `AGENTS.md` routing, installer coverage (`install.ps1` / `install.sh`), `validate_horus.py` checks, and an end-to-end mock Linear GraphQL test (`TestHorusFoundry`) in `tests/test_horus.py`.

## v0.4.1
- **Added `horus-next-steps` (upgraded OpenCode-native port of `antigravity-plugin-suggest-next-steps`, MIT):**
  - Replaced Antigravity's `ask_question` / `is_multi_select` / `send_message` protocol with OpenCode's native `question` tool schema (`header` ≤ 12 chars, `options[].label` ≤ 30 chars, `options[].description`, `multiple`, `custom: true`), keeping chat signal-only without redundant prose walls.
  - Added state-aware grounding (`plan.py next`, `git status`, `graphify update .`, `vibe-test-gate`), smart suppression rules (never fires on trivial lookups, blockers, or skipped turns), and strict primary-agent-only isolation (`horus` only; excluded from all worker allowlists).
  - Wired into `AGENTS.md`, `.opencode/agents/horus.md`, `SKILLS.md`, `README.md`, installers, and added `test_horus_next_steps_opencode_native_and_primary_only` in `tests/test_horus.py`.

## v0.4.0
- **Added Horus Context Mode (full OpenCode-compatible port of `antigravity-plugin-context-mode` v2.0.0, MIT):**
  - Bundled zero-dependency Node.js >= 22.5 MCP server & SQLite FTS5 engine (BM25 + Trigram RRF) under `.opencode/context-mode/` (`server.js`, `lib/{store,chunker,executor,tools}.js`, and standalone web dashboard `dashboard/{server.mjs,index.html}`).
  - Rebranded cleanly to **Horus Context Mode** (`horus-context-mode`, default DB `~/.horus-context-mode/context.db`, default agent `horus`), stripped Antigravity-only `.gemini/plugins/` installer code, hardcoded `C:/Users/domus` `sidecar_sdk` paths, and `Antigravity` PowerShell probes.
  - Registered `horus-context-mode` as a native local MCP server in both `opencode.jsonc` (V2) and `opencode.v1.json` (V1), and updated `install.ps1` / `install.sh` to copy `context-mode/`, rewrite the global MCP path to `~/.config/opencode/context-mode/server.js`, and check Node.js >= 22.5.0.
  - Added `.opencode/skills/horus-context-mode/SKILL.md`, `/horus-context` slash command, `AGENTS.md` zero-bloat rules, and worker allowlists (`c-engineer`, `re-analyst`, `ui-gui-engineer`, `web-engineer`).
- **Synced all version headers to v0.4.0** across `AGENTS.md`, `opencode.jsonc`, `horus.md`, `validate_horus.py`, `SKILLS.md`, `README.md`, and installers.
- **Validation & tests:** `validate_horus.py` now checks `/horus-context` and all 8 `context-mode/` runtime files; `tests/test_horus.py` adds `test_horus_context_mode_integration_and_rebrand` (including `node --check` on every JS module and global MCP path rewrite verification).

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
