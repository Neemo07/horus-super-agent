---
description: Show Horus project status, plan.py verification audit, active DAG wave, and git working tree in a zero-fluff summary.
---

Run a fast, read-only Horus health & progress check:

1. Locate `plan.py` (`.opencode/skills/planning-with-evidence/scripts/plan.py` or `~/.config/opencode/skills/planning-with-evidence/scripts/plan.py`).
2. Run `python <plan.py> status`, `python <plan.py> verify`, and `git status --short`.
3. Read `.horus/STATE.md` (if present) and report ONLY:
   - Progress bar & proven vs pending/blocked/unproven task counts
   - Active wave, SDD mode, and assigned subagent models
   - Working tree status & Graphify index freshness (`graphify-out/graph.json`)
   - Recommended next task (`plan.py next`)
4. If any tasks are `UNPROVEN` or `[!]`, ask how to proceed via the `question` tool (`header: "Next Step"`).

Extra filter or note:
$ARGUMENTS
