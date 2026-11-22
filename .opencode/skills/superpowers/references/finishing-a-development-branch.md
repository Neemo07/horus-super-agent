# Superpowers: Finishing a Development Branch

Run after all tasks in `task_plan.md` are verified `[x]` and `plan.py verify` passes.

## Steps
1. **Verify Tests:** Run the full project test/build suite. If anything fails, stop and fix — never present finish options on a red suite.
2. **Detect Git State:** Check current branch, base branch (`main`/`master`/upstream), working tree cleanliness, and whether running inside a git worktree.
3. **Present Options via OpenCode `question` Tool:**
   - **Merge locally** into base branch (and clean up feature branch/worktree)
   - **Push & open Pull Request** (respects `git push` confirmation gate)
   - **Keep branch as-is** (leave untouched for manual review)
   - **Discard work** (requires explicit confirmation before destructive reset/delete)
4. **Execute Choice & Cleanup:** Carry out the selected option cleanly, run `plan.py handoff`, and remove temporary worktrees if merged or discarded.
