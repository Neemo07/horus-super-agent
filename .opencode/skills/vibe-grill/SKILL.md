---
name: vibe-grill
description: Pre-code Socratic requirements interviewer (Grilling) — asks focused questions via OpenCode's native interactive question poll tool with engineering recommendations, then drafts PRD.md and AGENTS.md from bundled templates.
license: MIT
compatibility: opencode, claude-code, codex
metadata:
  source: abduallahJamal/vibe-engineering-playbook (full merged v1.0.0 + Horus OpenCode poll integration)
  category: requirements-discovery
  version: "1.1.0-horus"
---

# `vibe-grill` — Pre-Code Socratic Discovery (`Grilling`)

## Purpose

Prevent **Anti-Pattern B2 (Vague Prompts)** and **Anti-Pattern B4 (Prompting Before Specs)** by interviewing the user systematically **before writing a single line of application code**.

---

## Strict Interview Rules (Native OpenCode Poll Mode)

1. **Zero Code Generation:** Do not create application source files during discovery.
2. **ALWAYS Use the `question` Tool (Interactive Polls — Never Plain-Text Chat Walls):**
   - Present every discovery question through OpenCode's built-in **`question` tool** so the user can click a recommended option or click `"Type your own answer"`.
   - Ask **1 to 2 tightly related dimensions per `question` call** (never dump all 8 dimensions at once so earlier choices shape later options cleanly).
   - **Schema Guardrails:** Every question item MUST include both `header` (≤ 12 chars, e.g. `Lifecycle`, `Auth`, `Scale`, `Stack`, `Non-Goals`) AND `question` (full prompt text). Every `options[].label` MUST be ≤ 30 chars; put your engineering rationale and trade-offs in `options[].description`.
3. **Always Provide a Concrete Recommendation First:** Put your recommended default as the **first option** with `(Recommended)` in its label, explaining **why** (security, cost, complexity, maintainability) in its `description`. Keep `custom: true` (default) so the user can always write a custom answer without a fake `"Other"` choice.
4. **Cover the 8 Core Dimensions:**
   - **Lifecycle Target (`Lifecycle`):** Throwaway weekend `PoC`, personal tool (`Software for One`), or `MVP`/`Production` with real users/data?
   - **Core Problem & Audience (`Audience`):** Who uses it, and what single workflow proves value?
   - **Data Sensitivity & Compliance (`Data`):** PII, financial/medical records, multi-tenant isolation, backup/retention requirements.
   - **Authentication & Authorization (`Auth`):** Roles, session lifecycle, rate-limiting, least-privilege boundaries.
   - **Scale & Traffic Profile (`Scale`):** Expected concurrency (10 vs. 1,000+ req/s), connection pooling, caching needs.
   - **Stack & Rendering Strategy (`Stack`):** Existing stack constraints, `SSR`/`SSG`/`CSR` choice, hosting/container target.
   - **Explicit Non-Goals (`Non-Goals`):** What is strictly **out of scope** for v1? (`multiple: true` works well here!)
   - **Unhappy Paths & Edge Cases (`Edge Cases`):** Network timeouts, duplicate submissions, expired tokens, empty states, adversarial inputs.

---

## Deliverable Upon Completion

Once all 8 dimensions are clarified:
1. Present a concise **Decision Summary Table** and confirm via the **`question` tool** (`header: "Lock Specs"`, options: `Generate PRD & AGENTS (Recommended)`, `Revise Decisions`).
2. Generate two foundational files in the workspace using the bundled templates in `.opencode/skills/vibe/templates/`:
   - `AGENTS.md` (from `AGENTS.template.md` or `AGENTS.template.ar.md` if Arabic — or append project section to Horus `AGENTS.md` without overwriting Horus harness rules): Stack conventions, function-size limits, security invariants, forbidden patterns, and diff rules.
   - `PRD.md` (from `PRD.template.md`): Functional requirements, non-goals, data schema overview, and at least **15 explicit edge/unhappy-path cases**.
3. Hand off cleanly to `vibe-spec-plan`.
