---
name: vibe-test-gate
description: "Anti-test-theater mutation audit and 16-point Pre-Launch Production Gate before shipping MVP/Production builds."
license: MIT
compatibility: opencode, antigravity, dsh, claude-code, codex
metadata:
  source: abduallahJamal/vibe-engineering-playbook (full merged v1.0.0 + Horus integration)
  category: testing-and-release-gate
  version: "1.2.0-horus"
---

# `vibe-test-gate` — Test-Theater Audit & Production Launch Gate

## Purpose

Defeat **Green-Check Test Theater (F4)** and **Happy-Path-Only Testing (F1)** before any deployment reaches real users.

Full bilingual checklists reference: `.opencode/skills/vibe/references/checklists.en.md` (Arabic: `checklists.ar.md`).

---

## Part 1 — Anti-Test-Theater Audit Protocol

Inspect every test file created or modified and produce a verification table answering:
1. **External Behavior Proven:** Describe in one plain human sentence what observable user/API behavior the test proves (not internal mock wiring).
2. **Mutation / Sabotage Check:** Would this test **still pass** if the production function body were commented out or replaced with a static return value? If yes, flag it immediately as **`FAKE / TAUTOLOGICAL TEST`** and rewrite it.
3. **Assertion Integrity:** Flag tests with zero assertions, catch-all `try/except: pass`, or mocks that mock the system under test itself.
4. **Fail-Then-Pass (`Red -> Green`) Proof:** Every bugfix must include a test demonstrated to fail before the fix and pass after the fix.

---

## Part 2 — Deterministic Proof Matrix & Unhappy-Path Coverage

Route verbose test/build/scanner logs through `horus-context-mode` (`ctx_execute` / `ctx_search`) and run real commands for every applicable surface:
- **Unit, Integration & Unhappy-Path Suite:** Empty, malformed, oversized, boundary, and Unicode/RTL inputs; unauthenticated, expired-session, and horizontal/vertical privilege escalation (`User A` → `User B`); upstream timeout, DB pool exhaustion, network interruption; prompt-injection payloads on any LLM surface.
- **Native C/C++ Surfaces:** Sanitizer build (`-fsanitize=address,undefined` or MSVC `/fsanitize=address`) + `libFuzzer` smoke run on hostile-input parsers.
- **Web / UI Surfaces:** Playwright E2E (`webapp-testing`) verifying interactive states, Light/Dark theme, RTL (`dir="rtl"`) when applicable, keyboard-only navigation, and zero console/network error storms.
- **Evidence Ledger Closure:** Run `python <plan.py> verify --rerun` to mechanically confirm all `[x]` tasks still pass on the final commit.

---

## Part 3 — 16-Point Pre-Launch Production Gate

Before approving a production release, verify every item (`PASS` / `FAIL` / `N/A` with real observed command/file evidence):

> **Zero-Waiver Security Floor:** On `MVP / Production` builds, items **#1, #2, #3, #6, and #14** can NEVER be deferred to post-v1.

1. Static security scan (SAST) & dependency vulnerability audit clean.
2. Auth lifecycle verified end-to-end (signup, login, password reset, session expiry, RBAC, rate limits).
3. Server-side validation enforced on all write/query endpoints; zero secrets in source or git history.
4. Unhappy-path & edge-case suite passing.
5. Concurrency & connection pooling verified under realistic load.
6. Prompt-injection guardrails tested (if AI features exist).
7. Cross-browser & mobile responsive verification completed.
8. Automated backups configured, **restore-tested**, and `DROP`/`DELETE` guarded by manual confirmation.
9. Error monitoring, alerting, and 2 AM incident runbook documented.
10. All placeholder text/mock data/dummy images replaced; zero broken links.
11. Dependencies version-pinned; external CDN fallbacks or local hosting verified.
12. Client network tab audited (zero redundant request storms per view).
13. Independent review completed (reviewer ≠ author model).
14. IAM/access policies written from scratch with least privilege (never copy-pasted across prompts/tools).
15. Legal, privacy, accessibility, and UI originality checks completed.
16. Repository documentation (`README`, setup, architecture decisions) ready for the next engineer to onboard within one hour.

After presenting the gate table, if any item is `FAIL`, invoke OpenCode's **`question` tool** (`header: "Launch Gate"`, options: `Fix Blockers Now (Recommended)`, `Defer Non-Security to Post-v1`, `Re-run Full Audit`) — or request explicit text sign-off on Antigravity/DSH — so the user explicitly decides how to proceed.
