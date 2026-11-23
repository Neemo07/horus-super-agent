---
description: Manage the project's git-tracked `.todo.md` checklist, run 1-click AI Requirement Analysis, promote open items to `task_plan.md`, or launch the live Todo sidebar (`scripts/horus_todo.py`).
---

Load and follow the `horus-todo` skill immediately:

1. Run `python scripts/horus_todo.py list` to inspect the current `.todo.md` checklist and Git tracking state.
2. If `$ARGUMENTS` specifies `add`, `toggle`, `edit`, `remove`, `promote`, or `serve`, run the corresponding `horus_todo.py` subcommand and report the terse result.
3. If `$ARGUMENTS` is `analyze` (or the user asks for requirement analysis), audit open tasks against completed tasks for conflicts, duplication, dependency order, and scope clarity, then present proposed edits via OpenCode's native `question` tool (`header: "Todo Audit"`).
4. If `$ARGUMENTS` is empty, show the checklist summary and invoke OpenCode's `question` tool (`header: "Todo"`, options: `AI Requirement Analysis (Recommended)`, `Promote to task_plan.md`, `Add Task`, `Launch Live Sidebar`).

Arguments:
$ARGUMENTS
