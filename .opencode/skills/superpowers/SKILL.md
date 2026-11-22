---
name: superpowers
description: "Core Superpowers software engineering methodology (obra/superpowers v7.0.2 from obra/superpowers-marketplace — core plugin only): mandatory skill-check discipline, interactive brainstorming before coding, RED-GREEN-REFACTOR TDD, 4-phase systematic debugging, evidence-based verification before completion, git worktree isolation, and structured branch finishing — mapped natively to OpenCode V2 tools."
license: MIT
compatibility: opencode
metadata:
  source: https://github.com/obra/superpowers
  marketplace: https://github.com/obra/superpowers-marketplace
  version: "7.0.2"
---
# Superpowers (Core) — OpenCode V2 Edition

Core software development methodology from `obra/superpowers` (core plugin only — excluding unrelated marketplace plugins), harmonized with **Horus Super Agent** (`horus` DAG-Wave Orchestrator + `plan.py`) and mapped natively to **OpenCode V2** tools.

## 1. The Iron Rule (Skill Priority)
- **Process skills come BEFORE implementation skills.**
  - Building a new feature or project → run `brainstorming` first (via OpenCode's native `question` tool), then load implementation skills (`frontend-design`, `vercel-react-best-practices`, `supabase-postgres-best-practices`, `speed-engineer`, `modern-c-mastery`, `cpp20-win32-re`, etc.).
  - Fixing a bug, test failure, or slowness → run `systematic-debugging` first (find root cause before touching code), then domain skills.
  - Implementing any code → enforce `test-driven-development` (RED → GREEN → REFACTOR).
  - Before claiming anything works or passes → enforce `verification-before-completion` (fresh command output + `plan.py done`).
- **Red Flags (never rationalize away):**
  - *"I'll write the test after confirming the fix works"* → Untested fixes don't stick. Watch the test fail first.
  - *"Issue is simple, skip the process"* → Simple bugs have root causes too. Process is faster than guess-and-check.
  - *"Multiple fixes at once saves time"* → Can't isolate what worked; creates new bugs.
  - *"One more fix attempt"* (after 2+ failures) → 3+ failures = architectural flaw. Stop and escalate via `question`.

## 2. OpenCode V2 Tool Mapping
Superpowers workflows speak in abstract actions. In Horus / OpenCode V2, map them as follows:
- **Ask the user / present choices** → OpenCode native `question` tool (interactive poll with options + free-form custom input; never plain-text chat lists).
- **Invoke a skill** → OpenCode native `skill` tool.
- **Track tasks & plans** → `planning-with-evidence` (`plan.py` + `task_plan.md`) instead of ephemeral todo lists.
- **Dispatch a subagent** → `subagent` tool (`architect`, `c-engineer`, `fullstack-engineer`, `ui-gui-engineer`, `re-analyst`, `reviewer`) via `subagent-driven-dev` DAG waves.
- **Isolated branch workspace** → OpenCode Worktrees (`opencode.worktree_create`) or `git worktree add`.
- **Read / edit / run** → `read`, `glob`, `grep`, `edit`, `write`, `patch`, `shell`.

## 3. Core Superpowers Workflow Pipeline
1. **Brainstorming (`references/brainstorming.md`):** Draw out intent before coding using focused `question` polls (one round at a time), propose a concise design spec, and get sign-off before writing code.
2. **Planning (`writing-plans` + `plan.py`):** Break approved design into bite-sized 2–5 minute atomic tasks with exact file paths, frozen interfaces, and mechanical `accept:` verification commands in `task_plan.md`.
3. **Execution (`subagent-driven-dev` or inline):** Execute in parallel file-locked DAG waves (when SDD is enabled) or inline with two-stage review (`reviewer`).
4. **TDD (`references/test-driven-development.md`):** Write failing test → watch it fail (RED) → minimal code to pass (GREEN) → clean refactor (REFACTOR) → commit.
5. **Systematic Debugging (`references/systematic-debugging.md`):** Root cause investigation → pattern comparison → minimal hypothesis test → regression test + fix.
6. **Verification Before Completion (`references/verification-before-completion.md`):** No completion claim without fresh passing command output in the current turn (`plan.py done` + `plan.py verify`).
7. **Finishing a Development Branch (`references/finishing-a-development-branch.md`):** Verify full test suite is green → detect repo/worktree state → present Merge / PR / Keep / Discard choices via OpenCode `question` tool → execute choice & clean up worktree.

## Bundled Core References
Read the targeted reference before running that phase:
- `references/brainstorming.md`
- `references/test-driven-development.md`
- `references/systematic-debugging.md`
- `references/verification-before-completion.md`
- `references/finishing-a-development-branch.md`

Run `scripts/sync-skills.ps1` or `scripts/sync-skills.sh` to pull the full upstream `obra/superpowers` skill tree directly from GitHub.
