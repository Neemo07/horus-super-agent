---
name: horus-foundry
description: "Orchestrate parallel background OpenCode agents via Linear state machine and isolated git worktrees (scripts/horus_foundry.py)."
license: MIT
compatibility: opencode
metadata:
  source: leixusam/foundry (upgraded & ported for Horus / OpenCode)
  version: "0.4.2-horus"
---

# Horus Foundry — Parallel Background OpenCode Pods via Linear

Manage autonomous parallel **OpenCode** background workers from your phone or desktop using **Linear** as the queue and state machine — with **zero npm dependencies** and **true parallel git worktrees**.

## Why Horus Foundry Improves on Original Foundry
1. **Native OpenCode (`opencode run --agent horus`):** every background worker automatically inherits Horus's `AGENTS.md`, Graphify AST memory, Horus Context Mode, and `plan.py` proof gates (works with any OpenCode provider/model — not locked to Claude Code).
2. **True Parallel Isolation (`git worktree`):** each claimed Linear ticket gets its own isolated worktree at `.horus/foundry/worktrees/<ISSUE_KEY>` on branch `horus/<key>-<slug>`, so `--workers 3` never collides on working-tree files.
3. **0-Token Linear Reader & Writer:** instead of burning two extra LLM calls per ticket just to read/update Linear, `scripts/horus_foundry.py` scans, priority-sorts, claims (`∞ <Stage> In Progress`), comments, and advances tickets directly via Linear's GraphQL API.
4. **Honest Mobile Unblocking (`∞ Blocked`):** if a worker fails or emits `FOUNDRY_BLOCKED: <reason>`, the ticket moves to `∞ Blocked` with the exact error tail so you can clarify and drag it back to `∞ Needs ...` from the Linear mobile app.

## Linear State Machine (`∞` Prefix)
```
∞ Needs Research → ∞ Needs Specification* → ∞ Needs Plan → ∞ Needs Implement → ∞ Needs Validate → ∞ Awaiting Merge / ∞ Done
                                                                                                    (or ∞ Blocked on failure)
```
*(In `--mode oneshot`, tickets move directly through `∞ Oneshot In Progress` → `∞ Awaiting Merge` / `∞ Done`.)*

## Setup & Commands
1. **Configure credentials (gitignored `.horus/foundry.env`):**
   ```env
   LINEAR_API_KEY=lin_api_...
   LINEAR_TEAM_KEY=ENG
   HORUS_FOUNDRY_WORKERS=2
   HORUS_FOUNDRY_MODE=staged
   HORUS_FOUNDRY_MERGE=pr
   ```
2. **Initialize Linear workflow states (one-time):**
   ```bash
   python scripts/horus_foundry.py init-linear
   ```
3. **Check queued tickets & active worktrees:**
   ```bash
   python scripts/horus_foundry.py status
   ```
4. **Preview a wave (dry-run, zero mutations):**
   ```bash
   python scripts/horus_foundry.py run --workers 2 --once --dry-run
   ```
5. **Launch parallel background OpenCode pods:**
   ```bash
   python scripts/horus_foundry.py run --workers 2 --mode staged --merge pr
   ```

## Interactive OpenCode Workflow
When the user invokes `/horus-foundry`, use OpenCode's native `question` tool (`header: "Foundry"`) to choose:
- `Check Queue & Status (Recommended)` — run `horus_foundry.py status`
- `Dry-Run Next Wave` — preview ticket claims & worktree branches
- `Init Linear States` — create missing `∞` workflow states in Linear
- `Launch Background Pods` — confirm worker count, mode (`staged`/`oneshot`), and merge mode (`pr`/`merge`/`auto`) before starting
