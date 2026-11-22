---
name: subagent-driven-development
description: "Use when executing implementation plans with independent tasks in the current session"
license: MIT
compatibility: opencode
metadata:
  source: obra/superpowers (superpowers plugin of obra/superpowers-marketplace)
  edition: condensed-offline
---
> Provenance: offline condensed edition re-authored from the `superpowers` plugin (MIT). Run `python scripts/sync_upstream.py --only superpowers` for the verbatim upstream skill.

# Subagent-Driven Development

Fresh subagent per task, two-stage review after each: **spec compliance first, then code quality**.

## Loop
1. Read the plan once; extract every task with its full text and context.
2. For each task dispatch an implementer subagent with the full task text (never make it read the plan file), relevant context and constraints.
3. If it asks questions, answer completely before it proceeds.
4. Dispatch a **spec-compliance reviewer**: does the code match the task, nothing missing, nothing extra? Fix and re-review until clean.
5. Dispatch a **code-quality reviewer**: only after spec compliance passes. Fix and re-review until approved.
6. Mark the task complete; next task. After the last task, one final whole-implementation review, then `finishing-a-development-branch`.

## Rules
Never skip either review. Never proceed with open review issues. Never let a subagent start on main without consent. Do not run implementers in parallel on overlapping files.

## Under Horus
`horus` is the controller: dispatch via the Dispatch Packet (`OWNED_FILES`, `VERIFY_CMD`), parallel only on disjoint `OWNED_FILES`, review through `reviewer`, close with `plan.py done --run`. Horus rules win on any conflict.
