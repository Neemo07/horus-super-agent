# Changelog

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
