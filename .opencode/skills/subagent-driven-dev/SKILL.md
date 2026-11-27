---
name: subagent-driven-dev
description: "DAG-wave orchestrator: kickoff poll, file-locked parallel waves, Dispatch/Result envelopes, smart retries, plan.py."
license: MIT
compatibility: opencode, antigravity, dsh
metadata:
  version: "0.8.0-horus"
---
# Next-Gen Subagent Orchestrator Protocol (DAG-Wave SDD + Evidence Gate + Interactive Polls)

Turns `horus` (Horus Super Agent) into a strict, zero-rot, parallel-capable AI Orchestrator over isolated subagents (`architect`, `c-engineer`, `ui-gui-engineer`, `web-engineer`, `re-analyst`, `reviewer`), mechanically backed by `planning-with-evidence` (`plan.py`) and driven by OpenCode's native **`question` tool** (or Antigravity/DSH native confirmation UI) for human decisions.

## 1. Phase 0: Smart Kickoff Gate (Act When Clear, Poll When Greenfield / Ambiguous)
- On clear, scoped tasks in an existing repo, pre-research in parallel and execute directly without bureaucratic kickoff polls.
- On a **new project** or **multi-phase build** (with no active `.horus/STATE.md`), invoke the **`question` tool** with:
  - **Tab 1 (`Mode`):** `SDD Wave Mode (Recommended)` vs `Single-Agent Mode`
  - **Tab 2 (`Lifecycle`):** `Production / MVP (Recommended)` vs `Existing Repo Task` vs `Prototype / PoC`
  - **Tab 3 (`Models`):** `Inherit session (Recommended)` vs `Custom per subagent`

If `Custom per subagent` is chosen:
1. Run `opencode models` to list valid `provider/model` IDs.
2. Call `question` again (one tab per active subagent) with top available options + `Inherit session`.
3. **OpenCode `variant` Preservation Rule:** Subagents without a pinned `model:` inherit both parent model and parent `high` reasoning variant automatically. Whenever pinning a custom `model:` for a session in `.horus/STATE.md` / frontmatter, **ALWAYS pair it with `variant: high` (or chosen effort tier)** so OpenCode never silently downgrades that subagent to `medium` (never commit local `model:`/`variant:` edits).
4. Run `plan.py init` to scaffold `task_plan.md`, `findings.md`, `progress.md`, and `evidence/`, and create `.horus/STATE.md`.

## 2. Unified Workspace State & Memory Isolation
- **`task_plan.md` / `findings.md` / `progress.md` / `evidence/` / `HANDOFF.md`**: Managed by `plan.py`.
- **`horus-memory` Subagent Safety:** `ai-memory`'s OpenCode V2 plugin explicitly skips `parentID` child sessions, so parallel DAG subagents never steal root handoffs or get duplicate system injections; `horus` owns cross-session `memory_query` and `memory_write_page`.
- **`horus-context-mode` Discipline:** Route huge build/test logs through `ctx_search`/`ctx_execute` so orchestrator context stays razor-thin.
- **`.horus/STATE.md` (Keep ≤ 120 lines):**
```markdown
# Orchestrator State
- SDD Mode: enabled | disabled
- Lifecycle Tier: production | existing-repo | poc
- Subagent Models: architect=<id> (variant: high), c-engineer=inherit, ...
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
```

## 3. DAG Wave Scheduling & File-Ownership Locking
1. **Ready Frontier:** Select `[ ]` tasks in `task_plan.md` whose `Depends On` tasks are proven `[x]`.
2. **Disjoint Write-Lock Check:**
   - Two writer tasks (`c-engineer`, `ui-gui-engineer`, `web-engineer`) run **in parallel in the same wave** ONLY if their `Owns Files` sets have **empty intersection**.
   - Overlapping writers serialize across waves. Read-only agents (`architect`, `re-analyst`, `reviewer`) run concurrently without write locks.
3. **Start & Dispatch:** Run `plan.py start <id>` for each task, then launch all wave subagents concurrently.

## 4. Structured Dispatch Packet (Includes Reasoning Amplifier Fields)
Never forward conversation history. Send ONLY this compact packet so even smaller/weaker worker models stay grounded:
```markdown
TASK_ID: T2.1
GOAL: <1-2 sentences>
OWNED_FILES: <exact list — worker MUST NOT edit outside this list or touch task_plan.md>
GRAPHIFY_SLICE: <targeted symbols, callers/callees, file:line refs from graphify query/path>
INVARIANTS: <non-negotiable contracts, ABI/security/edge-case invariants from STATE.md>
ACCEPTANCE_CRITERIA:
- <binary check matching task_plan.md accept:>
VERIFY_CMD: `<exact build + test command>`
RETRY_DEFECTS: <none, or exact reviewer BLOCKERS/MAJORS on retry>
```

## 5. Two-Stage Review Gate + Mechanical `plan.py done` Closure
When a worker returns its **Result Envelope**:
- `STATUS: NEEDS_DECISION` / `BLOCKED` → turn `DECISION_OPTIONS` directly into a **`question` tool** poll (labels ≤ 30 chars, recommended first, `custom: true`).
- `STATUS: DONE` → dispatch `reviewer` (read-only) with the Dispatch Packet + Worker Envelope.
  - **`VERDICT: PASS`** → Run `plan.py done <id> --run "<verify_cmd>"` (or `--file <path>`). Only exit code 0 flips `[x]` and records proof in `evidence/`. Append `NEW_INVARIANTS` to `findings.md` / `.horus/STATE.md`.
  - **`VERDICT: FAIL`** (or `plan.py done` fails) → **Escalating Smart Retry (max 3 attempts):**
    - **Retry 1:** Re-dispatch worker with ONLY `BLOCKERS` & `MAJORS` (`file:line`).
    - **Retry 2:** Refresh Graphify slice + attach exact failing stderr / `evidence/<id>-NNN.log` + require 2 competing hypotheses before editing + re-dispatch.
    - **Retry 3 (Circuit Breaker):** Run `plan.py block <id> "<exact failure>"`, stop spinning, and call **`question`** (`header: "Blocked"`, 2–3 concrete recovery options).

## 6. Wave-End Integration Gate & Cold-Start Handoff
1. After every task in the wave is proven `[x]`, run the integrated workspace build/test/sanitizer suite and `graphify update .`.
2. Before claiming finished, run `plan.py verify` (or `verify --rerun`).
3. Before pausing, compacting, or ending a session, run `plan.py handoff --note "<active wave & next step>"`.
4. On resume: read `HANDOFF.md`, `task_plan.md`, tail of `findings.md`, `progress.md`, and `.horus/STATE.md` in parallel → run `plan.py verify` + `git status --short` → redo anything `UNPROVEN` → run `plan.py next`.
