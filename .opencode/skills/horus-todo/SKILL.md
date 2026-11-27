---
name: horus-todo
description: "Git-tracked .todo.md checklist with AI requirement analysis, plan.py promotion, and live local sidebar (scripts/horus_todo.py)."
license: MIT
compatibility: opencode, antigravity, dsh
metadata:
  source: deepseek-ai/dsh-todo-list (upgraded & ported for Horus / OpenCode)
  version: "0.8.2-horus"
---

# Horus Todo (`.todo.md` + AI Requirement Analysis)

Lightweight, git-tracked per-project checklist stored in `.todo.md` at the repo root — compatible with both `<!-- horus-todo: ... -->` and `<!-- dsh-todo: ... -->` markers, and upgraded for OpenCode, Google Antigravity, and DeepSeek Harness with `plan.py` promotion and an optional live browser sidebar.

## 1. Decision Boundary: `.todo.md` vs. `task_plan.md` (`plan.py`)
| Need | Use |
| :--- | :--- |
| Lightweight human+agent backlog, quick ideas, or commit-tracked reminders | **`.todo.md` (`horus_todo.py`)** |
| Multi-step (3+) implementation with file locks, SHA-256 evidence proofs, or subagent waves | **`task_plan.md` (`plan.py`)** — graduate open items via `horus_todo.py promote` |

## 2. Tri-Harness Script Path Resolution
- **Project install:** `scripts/horus_todo.py`
- **Global standalone installs:** `~/.config/opencode/scripts/horus_todo.py` (OpenCode), `~/.gemini/config/scripts/horus_todo.py` (Antigravity), or `$DSH_HOME/horus/scripts/horus_todo.py` (DeepSeek Harness).

## 3. Core Commands (`scripts/horus_todo.py`)
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

## 4. AI Requirement Analysis Protocol
When asked to analyze `.todo.md` (or via `/horus-todo analyze`):
1. Run `python scripts/horus_todo.py list` and inspect repo context (`graphify query` + `git status --short`).
2. Audit **open items against completed items** for:
   - **Conflicts & duplication** (tasks already satisfied or contradicting completed work)
   - **Dependency ordering** (prerequisites that must run first)
   - **Scope & clarity** (vague or oversized items that should be split or promoted to `task_plan.md` with explicit verification commands)
3. Present your concrete proposed changes (reorder, split, prune, or promote) via OpenCode's native **`question` tool** (`header: "Todo Audit"`, `multiple: true`, recommended action first) — or a concise numbered confirmation prompt on Antigravity/DSH — before modifying `.todo.md`.

## 5. Safety Guarantees
- Rewrites **only** Markdown checklist lines (`- [ ]` / `- [x]`); headings, comments, and prose notes in `.todo.md` are preserved verbatim.
- Refuses to overwrite an unrelated `.todo.md` that lacks checklist lines and a todo marker.
- Stages `.todo.md` (`git add -- .todo.md`) inside Git work trees without ever auto-committing.
