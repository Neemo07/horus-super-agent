---
name: vibe-spec-plan
description: System design and Plan Mode skill — converts PRD.md into an approved phased IMPLEMENTATION_PLAN.md (and Horus task_plan.md) with architectural boundaries, security controls, and dependency rules.
license: MIT
compatibility: opencode, claude-code, codex
metadata:
  source: abduallahJamal/vibe-engineering-playbook (full merged v1.0.0 + Horus OpenCode poll integration)
  category: architecture-planning
  version: "1.1.0-horus"
---

# `vibe-spec-plan` — Architecture & Plan Mode Gate

## Purpose

Eliminate **Mega-Prompt Drift (B1)**, **Supply-Chain Bloat (D5)**, and **Infrastructure Blindness (F3)** by producing a human-approved `IMPLEMENTATION_PLAN.md` (and synchronized `task_plan.md` under Horus `plan.py`) before implementation begins.

---

## Mandatory Planning Checklist

Read `PRD.md`, `AGENTS.md` / `CLAUDE.md`, and `.opencode/skills/vibe/templates/IMPLEMENTATION_PLAN.template.md`, then design the system across four pillars:

### 1. Architecture & State Boundaries
- Module decomposition (clear separation between routing/controllers, domain logic, data access, and UI).
- Rendering and state model (`SSR` / `SSG` / `CSR`), avoiding hidden client-side request storms (N+1 fetches per view).
- Database access strategy: mandatory **Connection Pooling**, thread/async safety, migrations, and zero raw `DROP`/`DELETE` paths exposed to automation.
- Size performance tier (`S` / `M` / `L`) with `speed-engineer` before freezing schemas and endpoints.

### 2. Security & Input Controls
- Dual validation: client-side UX validation + **mandatory server-side schema validation**.
- Secret management: `.env` + `.gitignore` + `.env.example` (zero hardcoded keys or credentials).
- Auth/RBAC matrix: explicit role checks per endpoint; rate limiting on authentication and expensive routes.

### 3. Dependency & Asset Policy
- List every external dependency to be installed and **justify why native code (~20 lines) is insufficient**.
- Pin exact package versions; decide explicitly which fonts/icons/scripts are self-hosted vs. external CDN.

### 4. Vertical-Slice Task Breakdown (`IMPLEMENTATION_PLAN.md` + `task_plan.md`)
Break execution into small, sequential checkpoints:
1. Project skeleton, linting/formatting, & environment configuration
2. Data schema, connection pool, & migrations
3. Core domain/API slice + server-side validation + unit tests
4. Authentication, authorization, & rate-limiting slice
5. UI integration (desktop + mobile responsive states + empty/error states)
6. Unhappy-path, security, & network-tab verification

Under **Horus**, translate every checkpoint into mechanical `plan.py` tasks (`- [ ] T1.1 Title | accept: <checkable cmd or file>`) with disjoint `OWNS_FILES` locks in `.horus/STATE.md`.

---

## Gate Rule (Interactive Poll)

Present `IMPLEMENTATION_PLAN.md` and **stop for explicit approval via OpenCode's `question` tool** (`header: "Plan Gate"`, options: `Approve & Start T1 (Recommended)`, `Revise Architecture`, `Trim or Add Scope`) before executing Task 1.
