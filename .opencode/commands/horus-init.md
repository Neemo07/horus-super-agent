---
description: Launch Horus interactive project kickoff wizard via OpenCode native question polls (SDD mode, lifecycle tier, subagent models, Graphify index, and plan.py init).
---

Run the **Horus Super Agent Kickoff Wizard** immediately:

1. Invoke OpenCode's built-in `question` tool with a 3-tab poll (`header` ≤ 12 chars, `options[].label` ≤ 30 chars, both `header` and `question` required on every tab, `custom: true` default):
   - Tab 1 (`Mode`): `SDD Wave Mode (Recommended)` vs `Single-Agent Mode`
   - Tab 2 (`Lifecycle`): `Production / MVP (Recommended)` vs `Existing Repo Task` vs `Prototype / PoC`
   - Tab 3 (`Models`): `Inherit session (Recommended)` vs `Custom per subagent`
2. If `Custom per subagent` is chosen, run `opencode models` and present a follow-up `question` poll per active subagent (`architect`, `c-engineer`, `ui-gui-engineer`, `web-engineer`, `re-analyst`, `reviewer`), then patch `model:` in `.opencode/agents/<name>.md` (omit for `inherit`).
3. Initialize `planning-with-evidence` (`python <plan.py> init`), create `.horus/STATE.md`, and build `graphify-out/graph.json` (`graphify . --no-viz`) if >15 source files exist.
4. If `Production / MVP` and `PRD.md` is missing, load `vibe` + `vibe-grill` and begin interactive poll discovery.

Project goal / context:
$ARGUMENTS
