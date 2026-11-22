---
name: using-git-worktrees
description: "Use when starting feature work that needs isolation from the current workspace or before executing implementation plans"
license: MIT
compatibility: opencode
metadata:
  source: obra/superpowers (superpowers plugin of obra/superpowers-marketplace)
  edition: condensed-offline
---
> Provenance: offline condensed edition re-authored from the `superpowers` plugin (MIT). Run `python scripts/sync_upstream.py --only superpowers` for the verbatim upstream skill.

# Using Git Worktrees

Isolated workspace on a new branch, sharing one repository.

1. **Pick the location:** existing `.worktrees/` or `worktrees/`; else the preference in AGENTS.md; else ask (project-local hidden directory vs global `~/.config/<tool>/worktrees/<project>`).
2. **Safety:** for a project-local directory verify it is git-ignored (`git check-ignore -q <dir>`). If not, add it to `.gitignore` and commit before creating the worktree.
3. **Create:** `git worktree add <dir>/<branch> -b <branch>`; `cd` into it.
4. **Setup:** run the project's install/setup (detect from lockfiles/manifests).
5. **Baseline:** run the test suite. If it fails, report the failures and ask whether to proceed; never start from an unknown baseline.
6. Report the path and baseline result.

Never skip the ignore check; never assume a location; never proceed past failing baseline tests without consent.
