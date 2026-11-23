---
name: subagent-driven-dev
description: "DAG-wave OpenCode orchestrator: kickoff poll, file-locked parallel waves, Dispatch/Result envelopes, smart retries, plan.py closure."
license: MIT
compatibility: opencode
---
# Next-Gen Subagent Orchestrator Protocol (DAG-Wave SDD + Evidence Gate + Interactive Polls)

Turns `horus` (Horus Super Agent) into a strict, zero-rot, parallel-capable AI Orchestrator over isolated OpenCode subagents (`architect`, `c-engineer`, `ui-gui-engineer`, `web-engineer`, `re-analyst`, `reviewer`), mechanically backed by `planning-with-evidence` (`plan.py`) and driven by OpenCode's native **`question` tool** for all human decisions.

## 1. Phase 0: Mandatory In-Session Kickoff Gate (Interactive Poll)
Before starting a project or multi-task feature, invoke OpenCode's built-in **`question` tool** (never plain chat lists) with:
- **Tab 1 (`Mode`):** `SDD Wave Mode (Recommended)` vs `Single-Agent Mode`
- **Tab 2 (`Lifecycle`):** `Production / MVP (Recommended)` vs `Existing Repo Task` vs `Prototype / PoC`
- **Tab 3 (`Models`):** `Inherit session (Recommended)` vs `Custom per subagent`

If `Custom per subagent` is chosen:
1. Run `opencode models` to list valid `provider/model` IDs.
2. Call `question` again (one tab per active subagent: `architect`, `c-engineer`, `ui-gui-engineer`, `web-engineer`, `re-analyst`, `reviewer`) with top available options + `Inherit session` (user can always click `"Type your own answer"` for any exact `provider/model` ID).
3. Save the custom model map in `.horus/STATE.md` (gitignored) and only patch `model:` in `.opencode/agents/<name>.md` for the active session when required (omit `model:` for `inherit`; never commit local `model:` overrides).
4. Run `plan.py init` to scaffold `task_plan.md`, `findings.md`, `progress.md`, and `evidence/`, and create `.horus/STATE.md`.

## 2. Unified Workspace State
- **`task_plan.md` / `findings.md` / `progress.md` / `evidence/` / `HANDOFF.md`**: Managed by `plan.py` (`planning-with-evidence`). Holds the Goal, Phases, Tasks (`- [ ] T1.1 Title | accept: ...`), append-only findings, computed progress bar, and disk proof logs.
- **`.horus/STATE.md` (Keep <= 120 lines)**: Orchestrator routing & file-lock table:
```markdown
# Orchestrator State
- SDD Mode: enabled | disabled
- Lifecycle Tier: production | existing-repo | poc
- Subagent Models: architect=<id>, c-engineer=<id>, ui-gui-engineer=<id>, web-engineer=<id>, re-analyst=<id>, reviewer=<id>
- Build Command: `<cmd>`
- Test / Sanitizer Command: `<cmd>`
- Graphify Status: indexed | pending
- Active Wave: W1
- Frozen Contracts & Invariants:
  - <header/ABI/token/wire-protocol invariants>

## DAG & File-Ownership Matrix
| ID | Wave | Agent | Depends On | Owns Files | Verify Cmd |
|----|------|-------|------------|------------|------------|
| T1.1 | W1 | re-analyst | - | (read-only) | REA evidence |
| T2.1 | W2 | c-engineer | T1.1 | src/parser.cpp, include/parser.hpp | ctest -R parser |
| T2.2 | W2 | ui-gui-engineer | T1.1 | src/ui/panel.cpp | cmake --build build |
| T2.3 | W2 | web-engineer | T1.1 | app/orders/**, supabase/migrations/0005_orders.sql | npm test && python <with_server.py> ... e2e |
```

## 3. DAG Wave Scheduling & File-Ownership Locking
1. **Ready Frontier:** Select `[ ]` tasks in `task_plan.md` whose `Depends On` tasks are proven `[x]`.
2. **Disjoint Write-Lock Check:**
   - Two writer tasks (`c-engineer`, `ui-gui-engineer`, `web-engineer`) may run **in parallel in the same wave** ONLY if their `Owns Files` sets have **empty intersection**.
   - Overlapping writers MUST serialize across waves. Read-only agents (`architect`, `re-analyst`, `reviewer`) run concurrently without write locks.
3. **Start & Dispatch:** Run `plan.py start <id>` for each selected task, then launch all wave subagents concurrently.

## 4. Structured Dispatch Packet (Orchestrator → Subagent)
Never forward conversation history. Send ONLY this compact packet:
```markdown
TASK_ID: T2.1
GOAL: <1-2 sentences>
OWNED_FILES: <exact list — worker MUST NOT edit outside this list or touch task_plan.md>
GRAPHIFY_SLICE: <targeted symbols, callers/callees, file:line refs from graphify query/path>
CONTRACTS_AND_INVARIANTS: <relevant bullets from STATE.md / findings.md>
ACCEPTANCE_CRITERIA:
- <binary check matching task_plan.md accept:>
VERIFY_CMD: `<exact build + test command>`
RETRY_DEFECTS: <none, or exact reviewer BLOCKERS/MAJORS on retry>
```

## 5. Two-Stage Review Gate + Mechanical `plan.py done` Closure
When a worker returns its **Result Envelope**:
- If `STATUS: NEEDS_DECISION` or `BLOCKED`: inspect immediately; turn the worker's `DECISION_OPTIONS` directly into an OpenCode **`question` tool** poll (each option label ≤ 30 chars, recommended first, `custom: true`) so the user picks or writes their own answer.
- If `STATUS: DONE`: dispatch `reviewer` (read-only) with the Dispatch Packet + Worker Envelope.
  - **`VERDICT: PASS`** → Run `plan.py done <id> --run "<verify_cmd>"` (or `--file <path>`). Only exit code 0 flips `[x]` and records proof in `evidence/`. Append `NEW_INVARIANTS` to `findings.md` / `.horus/STATE.md`.
  - **`VERDICT: FAIL`** (or `plan.py done` fails) → **Escalating Smart Retry (max 3 attempts):**
    - **Retry 1:** Re-dispatch worker with ONLY the reviewer's `BLOCKERS` & `MAJORS` (`file:line`).
    - **Retry 2:** Refresh Graphify slice + attach exact failing stderr / `evidence/<id>-NNN.log` + re-dispatch.
    - **Retry 3 (Circuit Breaker):** Run `plan.py block <id> "<exact failure>"`, stop spinning, and invoke the **`question` tool** (`header: "Blocked"`, 2–3 concrete recovery options + built-in custom answer).

## 6. Wave-End Integration Gate & Cold-Start Handoff
1. After every task in the wave is proven `[x]`, run the integrated workspace build/test/sanitizer suite and `graphify update .`.
2. Before claiming the project finished, run `plan.py verify` (or `verify --rerun`).
3. Before pausing, compacting, or ending a session, run `plan.py handoff --note "<active wave & next step>"`.
4. On resume: read `HANDOFF.md`, `task_plan.md`, tail of `findings.md`, `progress.md`, and `.horus/STATE.md` → run `plan.py verify` + `git status --short` → redo anything `UNPROVEN` → run `plan.py next`.
