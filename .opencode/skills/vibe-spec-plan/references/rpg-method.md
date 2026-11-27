# Repository Planning Graph (RPG) Method for Complex Systems

Adapted from TaskMasterProMax's RPG methodology for Horus `vibe-spec-plan` and `plan.py` DAG waves. Use this for multi-module systems, greenfield architectures, or large refactors where implicit dependencies would cause parallel subagents to collide.

## 1. Dual-Semantics (Separate WHAT from HOW)
- **Functional Decomposition (WHAT):** Group capabilities into domains → concrete features with explicit inputs, outputs, and invariants (zero file paths yet).
- **Structural Decomposition (HOW):** Map each capability domain to an exact directory/module tree (`src/<domain>/...`), public exports, and frozen interfaces (`.horus/STATE.md`).

## 2. Explicit Topological Dependency Graph (Zero Implicit Coupling)
Organize modules into strict buildable phases with zero circular dependencies:
- **Phase 0 — Foundation:** shared types, error taxonomy, config loader, logger (Depends on: `[]`).
- **Phase 1 — Data & Storage:** schemas, validators, migrations, repositories (Depends on: `[Phase 0]`).
- **Phase 2 — Core Domain:** business rules, state machines, pipelines (Depends on: `[Phase 0, Phase 1]`).
- **Phase 3 — Interfaces & UI:** API routes, CLI/MCP handlers, UI screens (Depends on: `[Phase 0..2]`).

## 3. Progressive Refinement into `task_plan.md`
1. Every capability becomes a phase; every module/vertical slice becomes a task (`- [ ] T1.1 ... | depends: ... | accept: <cmd>`).
2. Assign strictly **disjoint `Owns Files`** locks per wave in `.horus/STATE.md` so parallel subagents never touch the same file.
3. Score each task's complexity (`1–10`): any task scoring **≥ 6** MUST be expanded into atomic subtasks before dispatch.
