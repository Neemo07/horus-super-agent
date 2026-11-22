---
description: Activate the 7-stage Vibe Engineering workflow — specs before prompts, interactive OpenCode question polls, scoped increments, adversarial critique, and 16-point production gate verification.
---

Load and follow the `vibe` skill immediately to orchestrate the request using disciplined Vibe Engineering:

1. Classify whether the target is a disposable prototype (`PoC` / `Software for One`) or a real-user system (`MVP` / `Production`) — if unclear, ask via OpenCode's built-in `question` tool (never plain-text chat lists).
2. Inspect the workspace for `AGENTS.md` / `CLAUDE.md`, `PRD.md`, `IMPLEMENTATION_PLAN.md`, and Horus `task_plan.md` / `.horus/STATE.md` before proposing or modifying any code.
3. Route to the appropriate stage skill (`vibe-grill`, `vibe-spec-plan`, `vibe-scoped-build`, `vibe-critique`, or `vibe-test-gate`), using bundled templates in `.opencode/skills/vibe/templates/` and pausing at mandatory human review gates via the `question` tool.

User request:
$ARGUMENTS
