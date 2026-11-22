---
name: vibe-grill
description: Pre-code Socratic requirements interviewer (Grilling) — asks one focused question at a time with engineering recommendations via OpenCode's native question tool, then drafts PRD.md and AGENTS.md.
license: MIT
compatibility: opencode, claude-code, codex
metadata:
  category: requirements-discovery
  version: "1.0.0"
  source: https://github.com/abduallahJamal/vibe-engineering-playbook
---

# `vibe-grill` — Pre-Code Socratic Discovery (`Grilling`)

## Purpose

Prevent **Anti-Pattern B2 (Vague Prompts)** and **Anti-Pattern B4 (Prompting Before Specs)** by interviewing the user systematically **before writing a single line of application code**.

---

## Strict Interview Rules

1. **Zero Code Generation:** Do not create application source files during discovery.
2. **One Question at a Time — via OpenCode's Native `question` Tool:** Never dump a 15-question questionnaire in chat. Ask **one high-leverage question per turn** using OpenCode's native `question` tool (with a short `header`, concise prompt, and 2–4 concrete `options` with your recommended choice clearly marked; OpenCode automatically includes a free-form custom answer input).
3. **Always Provide a Concrete Recommendation:** Mark your recommended option and state **why** (trade-offs in security, cost, complexity, and maintainability).
4. **Cover the 8 Core Dimensions:**
   - **Lifecycle Target:** Throwaway weekend `PoC`, personal tool (`Software for One`), or `MVP`/`Production` with real users/data?
   - **Core Problem & Audience:** Who uses it, and what single workflow proves value?
   - **Data Sensitivity & Compliance:** PII, financial/medical records, multi-tenant isolation, backup/retention requirements.
   - **Authentication & Authorization:** Roles, session lifecycle, rate-limiting, least-privilege boundaries.
   - **Scale & Traffic Profile:** Expected concurrency (10 vs. 1,000+ req/s), connection pooling, caching needs.
   - **Stack & Rendering Strategy:** Existing stack constraints, `SSR`/`SSG`/`CSR` choice, hosting/container target.
   - **Explicit Non-Goals:** What is strictly **out of scope** for v1?
   - **Unhappy Paths & Edge Cases:** Network timeouts, duplicate submissions, expired tokens, empty states, adversarial inputs.

---

## Deliverable Upon Completion

Once all dimensions are clarified:
1. Present a concise **Decision Summary Table** and confirm via OpenCode's native `question` tool (`Approve & generate PRD.md` / `Revise decisions`).
2. Generate two foundational files in the workspace (using `.opencode/skills/vibe/templates/PRD.template.md` when helpful):
   - `AGENTS.md` (or update existing project rules without removing Horus harness rules): Stack conventions, function-size limits, security invariants, forbidden patterns, and diff rules.
   - `PRD.md`: Functional requirements, non-goals, data schema overview, and at least **15 explicit edge/unhappy-path cases**.
