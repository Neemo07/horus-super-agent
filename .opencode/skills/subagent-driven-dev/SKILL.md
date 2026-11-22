---
name: subagent-driven-dev
description: "Next-gen DAG-Wave Subagent Orchestrator protocol for OpenCode integrated with native question polls and planning-with-evidence (plan.py): in-session interactive kickoff gate, parallel wave scheduling with file-ownership locks, structured Dispatch/Result envelopes, escalating smart retries, and HANDOFF.md recovery."
license: MIT
compatibility: opencode
---
# Next-Gen Subagent Orchestrator Protocol (DAG-Wave SDD + Evidence Gate)

Turns `horus` (Horus Super Agent) into a strict, zero-rot, parallel-capable AI Orchestrator over isolated OpenCode subagents (`architect`, `fullstack-engineer`, `c-engineer`, `ui-gui-engineer`, `re-analyst`, `reviewer`), mechanically backed by `planning-with-evidence` (`plan.py`) and interactive OpenCode `question` polls.

## 1. Phase 0: Mandatory In-Session Kickoff Gate (Native `question` Tool)
Before starting a project or multi-task feature:
1. Invoke OpenCode's native `question` tool (NEVER a plain-text chat questionnaire):
   - **Round 1:** Execution Mode (`SDD Parallel Waves` vs `Single-Agent Direct`), Project Track (`Full-Stack Web`, `Systems / Native C/C++`, `Reverse Engineering`, `Hybrid`), and Superpowers discipline level.
   - **Round 2 (if SDD enabled):** Ask which `provider/model` (from `opencode models`, or `inherit`) to assign to active subagents (`architect`, `fullstack-engineer`, `c-engineer`, `ui-gui-engineer`, `re-analyst`, `reviewer`).
2. Patch `model:` in `.opencode/agents/<name>.md` for any custom assignments (omit `model:` for `inherit`).
3. Run `plan.py init` to scaffold `task_plan.md`, `findings.md`, `progress.md`, and `evidence/`, and create `.horus/STATE.md`.

## 2. Unified Workspace State
- **`task_plan.md` / `findings.md` / `progress.md` / `evidence/` / `HANDOFF.md`**: Managed by `plan.py` (`planning-with-evidence`). Holds the Goal, Phases, Tasks (`- [ ] T1.1 Title | accept: ...`), append-only findings, computed progress bar, and disk proof logs.
- **`.horus/STATE.md` (Keep <= 120 lines)**: Orchestrator routing & file-lock table:
```markdown
# Orchestrator State
- SDD Mode: enabled | disabled
- Project Track: fullstack-web | systems-native | reverse-engineering | hybrid
- Performance Tier: S | M | L (from speed-engineer)
- Subagent Models: architect=<id>, fullstack-engineer=<id>, c-engineer=<id>, ui-gui-engineer=<id>, re-analyst=<id>, reviewer=<id>
- Build Command: `<cmd>`
- Test / Verify Command: `<cmd>`
- Graphify Status: indexed | pending
- Active Wave: W1
- Frozen Contracts & Invariants:
  - <header/ABI/schema/API/token invariants>

## DAG & File-Ownership Matrix
| ID | Wave | Agent | Depends On | Owns Files | Verify Cmd |
|----|------|-------|------------|------------|------------|
| T1.1 | W1 | architect | - | (read-only) | contracts frozen |
| T2.1 | W2 | fullstack-engineer | T1.1 | supabase/migrations/*, src/lib/api/* | npm test |
| T2.2 | W2 | ui-gui-engineer | T1.1 | src/components/*, src/app/page.tsx | npx tsc --noEmit |
```

## 3. DAG Wave Scheduling & File-Ownership Locking
1. **Ready Frontier:** Select `[ ]` tasks in `task_plan.md` whose `Depends On` tasks are proven `[x]`.
2. **Disjoint Write-Lock Check:**
   - Two writer tasks (`fullstack-engineer`, `c-engineer`, `ui-gui-engineer`) may run **in parallel in the same wave** ONLY if their `Owns Files` sets have **empty intersection**.
   - Overlapping writers MUST serialize across waves. Read-only agents (`architect`, `re-analyst`, `reviewer`) run concurrently without write locks.
3. **Start & Dispatch:** Run `plan.py start <id>` for each selected task, then launch all wave subagents concurrently.

## 4. Structured Dispatch Packet (Orchestrator → Subagent)
Never forward conversation history. Send ONLY this compact packet:
```markdown
TASK_ID: T2.1
GOAL: <1-2 sentences>
OWNED_FILES: <exact list — worker MUST NOT edit outside this list or touch task_plan.md>
REQUIRED_SKILLS: <e.g., supabase-postgres-best-practices, speed-engineer, superpowers>
GRAPHIFY_SLICE: <targeted symbols, callers/callees, file:line refs from graphify query/path>
CONTRACTS_AND_INVARIANTS: <relevant bullets from STATE.md / findings.md>
ACCEPTANCE_CRITERIA:
- <binary check matching task_plan.md accept:>
VERIFY_CMD: `<exact build + test + Playwright command>`
RETRY_DEFECTS: <none, or exact reviewer BLOCKERS/MAJORS on retry>
```

## 5. Two-Stage Review Gate + Mechanical `plan.py done` Closure
When a worker returns its **Result Envelope**:
- If `STATUS: NEEDS_DECISION` or `BLOCKED`: inspect immediately; expand `OWNED_FILES` if safe or present `DECISION_OPTIONS` to the user via OpenCode's native `question` tool.
- If `STATUS: DONE`: dispatch `reviewer` (read-only) with the Dispatch Packet + Worker Envelope.
  - **`VERDICT: PASS`** → Run `plan.py done <id> --run "<verify_cmd>"` (or `--file <path>`). Only exit code 0 flips `[x]` and records proof in `evidence/`. Append `NEW_INVARIANTS` to `findings.md` / `.horus/STATE.md`.
  - **`VERDICT: FAIL`** (or `plan.py done` fails) → **Escalating Smart Retry (max 3 attempts):**
    - **Retry 1:** Re-dispatch worker with ONLY the reviewer's `BLOCKERS` & `MAJORS` (`file:line`).
    - **Retry 2:** Refresh Graphify slice + attach exact failing stderr / `evidence/<id>-NNN.log` + re-dispatch.
    - **Retry 3 (Circuit Breaker):** Run `plan.py block <id> "<exact failure>"`, stop spinning, and invoke OpenCode's native `question` tool with 2–3 concrete recovery options.

## 6. Wave-End Integration Gate & Cold-Start Handoff
1. After every task in the wave is proven `[x]`, run the integrated workspace build/test/Playwright/sanitizer suite and `graphify . --update`.
2. Before claiming the project finished, run `plan.py verify` (or `verify --rerun`).
3. Before pausing, compacting, or ending a session, run `plan.py handoff --note "<active wave & next step>"`.
4. On resume: read `HANDOFF.md`, `task_plan.md`, tail of `findings.md`, `progress.md`, and `.horus/STATE.md` → run `plan.py verify` + `git status --short` → redo anything `UNPROVEN` → run `plan.py next`.
