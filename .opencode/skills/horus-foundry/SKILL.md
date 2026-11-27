---
name: horus-foundry
description: "Orchestrate parallel background OpenCode agents via Linear state machine and isolated git worktrees (scripts/horus_foundry.py)."
license: MIT
compatibility: opencode, antigravity, dsh
metadata:
  source: leixusam/foundry (upgraded & ported for Horus / OpenCode / Antigravity / DSH)
  version: "0.8.0-horus"
---

# Horus Foundry — Parallel Background Pods via Linear (OpenCode / Antigravity / DSH)

Manage autonomous parallel background workers from your phone or desktop using **Linear** as the queue and state machine — with **zero npm dependencies**, **true parallel `git worktree` isolation**, and **tri-harness runner support (`--runner opencode|antigravity|dsh`)**.

## Why Horus Foundry Improves on Original Foundry
1. **Tri-Harness CLI Runners + Reasoning Variants:** Run background pods via `--runner opencode` (`opencode run --agent horus --variant high`), `--runner antigravity` (`agy run`), or `--runner dsh` (`dsh run`), overriding binaries with `OPENCODE_BIN`, `ANTIGRAVITY_BIN`, or `DSH_BIN`.
2. **True Parallel Isolation (`git worktree`):** Each claimed Linear ticket gets its own isolated worktree at `.horus/foundry/worktrees/<ISSUE_KEY>` on branch `horus/<key>-<slug>`, so `--workers 3` never collides on working-tree files.
3. **0-Token Linear Reader & Writer:** `scripts/horus_foundry.py` scans, priority-sorts, claims (`∞ <Stage> In Progress`), comments, and advances tickets directly via Linear's GraphQL API (zero LLM tokens burned on queue management).
4. **Honest Mobile Unblocking (`∞ Blocked`):** If a worker fails or emits `FOUNDRY_BLOCKED: <reason>`, the ticket moves to `∞ Blocked` with the exact error tail so you can clarify and drag it back to `∞ Needs ...` from the Linear mobile app.

## Linear State Machine (`∞` Prefix)
```
∞ Needs Research → ∞ Needs Specification* → ∞ Needs Plan → ∞ Needs Implement → ∞ Needs Validate → ∞ Awaiting Merge / ∞ Done
                                                                                                    (or ∞ Blocked on failure)
```
*(In `--mode oneshot`, tickets move directly through `∞ Oneshot In Progress` → `∞ Awaiting Merge` / `∞ Done`.)*

## Setup & Commands
*(In global standalone installs, `scripts/horus_foundry.py` is auto-resolved to `~/.config/opencode/scripts/`, `~/.gemini/config/scripts/`, or `$DSH_HOME/horus/scripts/`.)*

1. **Configure credentials (gitignored `.horus/foundry.env`):**
   ```env
   LINEAR_API_KEY=lin_api_...
   LINEAR_TEAM_KEY=ENG
   HORUS_FOUNDRY_RUNNER=opencode
   HORUS_FOUNDRY_VARIANT=high
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
   python scripts/horus_foundry.py run --runner opencode --variant high --workers 2 --once --dry-run
   ```
5. **Launch parallel background pods:**
   ```bash
   python scripts/horus_foundry.py run --runner opencode --variant high --workers 2 --mode staged --merge pr
   ```

## Interactive Workflow
When the user invokes `/horus-foundry`, use OpenCode's native `question` tool (`header: "Foundry"`, or Antigravity/DSH native prompt) to choose:
- `Check Queue & Status (Recommended)` — run `horus_foundry.py status`
- `Dry-Run Next Wave` — preview ticket claims & worktree branches
- `Init Linear States` — create missing `∞` workflow states in Linear
- `Launch Background Pods` — confirm runner (`opencode`/`antigravity`/`dsh`), variant (`high`), worker count, mode (`staged`/`oneshot`), and merge mode (`pr`/`merge`/`auto`) before starting

## 6. Local Fresh-Context Autonomous Loops (`horus_foundry.py loop` — Zero Linear Key)
Run TaskMasterProMax-style fresh-context iterations across **OpenCode (`--variant high`)**, **Google Antigravity (`agy`)**, or **DeepSeek Harness (`dsh`)** with 5 built-in presets (`default`, `test-coverage`, `linting`, `duplication`, `entropy`) and early exit on `<loop-complete>` / `<loop-blocked>`:
```bash
python scripts/horus_foundry.py loop --preset test-coverage -n 5 --runner opencode --variant high --dry-run
python scripts/horus_foundry.py loop --preset linting -n 10 --runner opencode --variant high
```
