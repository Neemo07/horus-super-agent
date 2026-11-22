---
description: Cold-start or post-compaction session resume — reloads HANDOFF.md, task_plan.md, findings.md, and .horus/STATE.md, verifies evidence, and confirms next wave via question poll.
---

Execute the **Horus Cold-Start Resume Protocol**:

1. Read `HANDOFF.md`, `task_plan.md`, tail of `findings.md`, `progress.md`, and `.horus/STATE.md`.
2. Run `python <plan.py> verify` and `git status --short`.
3. Summarize the current state in ≤ 5 terse bullets (active wave, proven progress, any `UNPROVEN` or blocked tasks, next ready frontier from `plan.py next`).
4. Invoke OpenCode's `question` tool (`header: "Resume"`, options: `Continue Next Wave (Recommended)`, `Fix Unproven First`, `Review Findings & Plan`) before executing any edits.

Optional resume note:
$ARGUMENTS
