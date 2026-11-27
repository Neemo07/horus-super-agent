---
name: vibe-grill
description: "Pre-code Socratic requirements interview via OpenCode question polls to draft PRD.md and project AGENTS.md."
license: MIT
compatibility: opencode, antigravity, dsh, claude-code, codex
metadata:
  source: abduallahJamal/vibe-engineering-playbook (full merged v1.0.0 + Horus OpenCode poll integration)
  category: requirements-discovery
  version: "1.2.0-horus"
---

# `vibe-grill` — Pre-Code Socratic Discovery (`Grilling`)

## Purpose

Prevent **Anti-Pattern B2 (Vague Prompts)** and **Anti-Pattern B4 (Prompting Before Specs)** by interviewing the user systematically **before writing a single line of application code**, capturing both product requirements and upfront **System Design / UI Design System** boundaries so `vibe-spec-plan` starts with zero guesswork.

---

## Strict Interview Rules (Native OpenCode Poll Mode)

1. **Zero Code Generation:** Do not create application source files during discovery.
2. **ALWAYS Use the `question` Tool (Interactive Polls — Never Plain-Text Chat Walls):**
   - On OpenCode, present every discovery question through the built-in **`question` tool** so the user can click a recommended option or click `"Type your own answer"` (on Antigravity/DSH, ask 1–2 tightly related questions per turn with your recommended default marked `(Recommended)`).
   - Ask **1 to 2 tightly related dimensions per `question` call** (never dump all 10 dimensions at once so earlier choices shape later options cleanly).
   - **Schema Guardrails:** Every question item MUST include both `header` (≤ 12 chars, e.g. `Lifecycle`, `Auth`, `Scale`, `Architecture`, `UI/UX`, `Non-Goals`) AND `question` (full prompt text). Every `options[].label` MUST be ≤ 30 chars; put your engineering rationale and trade-offs in `options[].description`.
3. **Always Provide a Concrete Recommendation First:** Put your recommended default as the **first option** with `(Recommended)` in its label, explaining **why** (security, cost, complexity, maintainability) in its `description`. Keep `custom: true` (default) so the user can always write a custom answer without a fake `"Other"` choice.
4. **Cover the 10 Core Dimensions (Product + System Design + UI):**
   - **Lifecycle Target (`Lifecycle`):** Throwaway weekend `PoC`, personal tool (`Software for One`), or `MVP`/`Production` with real users/data?
   - **Core Problem & Audience (`Audience`):** Who uses it, and what single workflow proves value?
   - **Data Sensitivity & Compliance (`Data`):** PII, financial/medical records, multi-tenant isolation, backup/retention requirements.
   - **Authentication & Authorization (`Auth`):** Roles, session lifecycle, rate-limiting, least-privilege boundaries.
   - **System Design Boundaries (`Architecture`):** Data ownership, API/contract style (REST/RPC/events), sync vs. async/queues, idempotency, and external failure modes.
   - **Scale & Traffic Profile (`Scale`):** Expected concurrency (10 vs. 1,000+ req/s), connection pooling, caching needs, and latency/perf tier.
   - **Stack & Rendering Strategy (`Stack`):** Existing stack constraints, `SSR`/`SSG`/`CSR` or desktop native choice, hosting/container target.
   - **UI & Locale System (`UI/UX`):** Design token system (Light/Dark, brand palette, density), RTL/Arabic or bilingual support, and WCAG 2.2 AA target (skip for headless/CLI/API-only projects).
   - **Explicit Non-Goals (`Non-Goals`):** What is strictly **out of scope** for v1? (`multiple: true` works well here!)
   - **Unhappy Paths & Edge Cases (`Edge Cases`):** Network timeouts, duplicate submissions, expired tokens, empty states, adversarial inputs.

---

## Deliverable Upon Completion

Once all applicable dimensions are clarified:
1. Present a concise **Decision Summary Table** and confirm via the **`question` tool** (`header: "Lock Specs"`, options: `Generate PRD & AGENTS (Recommended)`, `Revise Decisions`).
2. Generate two foundational files in the workspace using the bundled templates in `.opencode/skills/vibe/templates/`:
   - `AGENTS.md` (from `AGENTS.template.md` or `AGENTS.template.ar.md` if Arabic — or append project section to Horus `AGENTS.md` without overwriting Horus harness rules): Stack conventions, function-size limits, security invariants, forbidden patterns, and diff rules.
   - `PRD.md` (from `PRD.template.md`): Functional requirements, system-design boundaries, UI/locale expectations, non-goals, data schema overview, and at least **15 explicit edge/unhappy-path cases**.
3. Hand off cleanly to `vibe-spec-plan`.
