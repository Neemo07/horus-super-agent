---
name: executing-plans
description: "Use when you have a written implementation plan to execute in a separate session with review checkpoints"
license: MIT
compatibility: opencode
metadata:
  source: obra/superpowers (superpowers plugin of obra/superpowers-marketplace)
  edition: condensed-offline
---
> Provenance: offline condensed edition re-authored from the `superpowers` plugin (MIT). Run `python scripts/sync_upstream.py --only superpowers` for the verbatim upstream skill.

# Executing Plans

1. **Load and review the plan critically.** Raise concerns before starting; if there are none, proceed.
2. **Execute in batches** (default: first 3 tasks). For each task: mark in progress, follow every step exactly, run the verifications, mark complete.
3. **Report between batches:** what was implemented, verification output, then "ready for feedback". Wait.
4. **Apply feedback**, then next batch.
5. **Finish:** use `finishing-a-development-branch`.

## Stop immediately when
A blocker appears (missing dependency, failing test, unclear instruction), the plan has a gap, or a verification fails repeatedly. Ask; do not guess. Revisit the plan when feedback changes the approach. Never skip a verification step. Do not start implementation on main/master without explicit consent (use `using-git-worktrees`).
