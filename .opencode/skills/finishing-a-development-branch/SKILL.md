---
name: finishing-a-development-branch
description: "Use when implementation is complete, all tests pass, and you need to decide how to integrate the work - guides completion of development work by presenting structured options for merge, PR, or cleanup"
license: MIT
compatibility: opencode
metadata:
  source: obra/superpowers (superpowers plugin of obra/superpowers-marketplace)
  edition: condensed-offline
---
> Provenance: offline condensed edition re-authored from the `superpowers` plugin (MIT). Run `python scripts/sync_upstream.py --only superpowers` for the verbatim upstream skill.

# Finishing a Development Branch

1. **Verify tests first** (`verification-before-completion`). If failing, stop and report; do not offer options.
2. **Determine the base branch** (`git merge-base HEAD main`).
3. **Present exactly four options:** (1) merge locally, (2) push and create a Pull Request, (3) keep the branch as-is, (4) discard this work.
4. **Execute the choice:**
   - Merge: checkout base, pull, merge, re-run tests on the merged result, delete the feature branch.
   - PR: push with upstream, create the PR (summary + test plan).
   - Keep: report branch and worktree path; no cleanup.
   - Discard: list what will be deleted and require the user to type `discard` first.
5. **Clean up the worktree** for options 1 and 4 only (`git worktree remove`).

Never merge without re-testing; never delete work without typed confirmation; never force-push without an explicit request.
