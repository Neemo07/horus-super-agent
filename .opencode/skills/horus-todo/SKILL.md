---
name: horus-todo
description: "Git-tracked .todo.md checklist with AI requirement analysis, plan.py promotion, and live local sidebar (scripts/horus_todo.py)."
license: MIT
compatibility: opencode
metadata:
  source: deepseek-ai/dsh-todo-list (upgraded & ported for Horus / OpenCode)
  version: "0.4.3-horus"
---

# Horus Todo (`.todo.md` + AI Requirement Analysis)

Lightweight, git-tracked per-project checklist stored in `.todo.md` at the repo root — compatible with both `<!-- horus-todo: ... -->` and `<!-- dsh-todo: ... -->` markers, and upgraded for OpenCode with native `question` polls, `plan.py` promotion, and an optional live browser sidebar.

## How `.todo.md` Fits with `task_plan.md` (`plan.py`)
- **`.todo.md` (Horus Todo):** lightweight, git-tracked backlog & scratchpad that travels with every commit so humans and OpenCode share one living checklist.
- **`task_plan.md` (`plan.py`):** formal evidence-gated DAG execution plan for multi-step builds (`plan.py done --run`). Graduate open `.todo.md` items straight into `task_plan.md` anytime with `python scripts/horus_todo.py promote`.

## Core Commands (`scripts/horus_todo.py`)
```bash
python scripts/horus_todo.py list                     # progress + items + git tracking badge
python scripts/horus_todo.py add "Add rate limiter"   # appends item + runs `git add -- .todo.md`
python scripts/horus_todo.py toggle 1                 # check/uncheck item #1
python scripts/horus_todo.py edit 1 "Updated text"    # edit item #1 inline
python scripts/horus_todo.py remove 2                 # delete item #2
python scripts/horus_todo.py analyze                  # generate structured AI Requirement Analysis
python scripts/horus_todo.py promote                  # graduate open items into task_plan.md
python scripts/horus_todo.py serve --port 4178        # launch live-reloading browser sidebar UI
```

## AI Requirement Analysis Protocol
When asked to analyze `.todo.md` (or via `/horus-todo analyze`):
1. Run `python scripts/horus_todo.py list` and inspect the repo context (`graphify query` or `git status`).
2. Audit **open items against completed items** for:
   - **Conflicts & duplication** (tasks already satisfied or contradicting completed work)
   - **Dependency ordering** (prerequisites that must run first)
   - **Scope & clarity** (vague or oversized items that should be split)
3. Present your concrete proposed changes (reorder, split, prune, or promote to `task_plan.md`) via OpenCode's native **`question` tool** (`header: "Todo Audit"`, `multiple: true`, recommended action first) before modifying `.todo.md`.

## Safety Guarantees
- Rewrites **only** Markdown checklist lines (`- [ ]` / `- [x]`); headings, comments, and prose notes in `.todo.md` are preserved verbatim.
- Refuses to overwrite an unrelated `.todo.md` that lacks checklist lines and a todo marker.
- Stages `.todo.md` (`git add -- .todo.md`) inside Git work trees without ever auto-committing.
