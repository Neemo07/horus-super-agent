---
description: Run an adversarial read-only review (reviewer + vibe-critique + vibe-test-gate anti-test-theater audit) on the current git diff or specified target.
---

Run an independent **Adversarial Review & Test-Theater Audit**:

1. Inspect `git status --short` and `git diff` (or the specified target files/branch in `$ARGUMENTS`).
2. Dispatch the read-only `reviewer` subagent (or apply `vibe-critique` + `vibe-test-gate` directly if in Single-Agent Mode) with zero praise and strict `file:line` evidence:
   - Spec compliance against `PRD.md` / `task_plan.md`
   - Top 3 highest-severity production/security/ABI/performance risks with confidence scores (`0–100`)
   - Anti-Test-Theater mutation check on modified tests
   - `plan.py verify` check for `UNPROVEN` completions
3. Present the terse verdict (`PASS` / `FAIL`) and, if `FAIL` or risks exist, invoke OpenCode's `question` tool (`header: "Review"`, options: `Fix Blockers Now (Recommended)`, `Re-run Full Tests`, `Accept & Document Risk`).

Target / scope:
$ARGUMENTS
