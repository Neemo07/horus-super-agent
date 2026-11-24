---
name: senior-engineering-partner
description: "Phase-aware (Tier 0-2) production standards & AUDIT: mode: Cloud/K8s/Terraform, DR/BC, SRE, compliance, supply chain, Python/Bash/TS/Swift."
license: Apache-2.0
compatibility: opencode
metadata:
  source: bjgreenberg/senior-engineering-partner v1.32.0 (OpenCode progressive-disclosure edition; 8 overlapping refs deferred to Horus native skills)
  version: "0.5.3-horus"
---

# Senior Engineering Partner (OpenCode Progressive-Disclosure Edition)

Phase-aware production engineering standards (**Tier 0 Prototype → Tier 1 MVP → Tier 2 Production**) with a **non-negotiable Security/CIA floor** (*cheap ≠ insecure*) and 39 deep, read-on-demand reference handbooks under `references/` plus 5 deterministic helper scripts under `scripts/`.

**Never load multiple references upfront.** Read ONLY the specific reference(s) matching the active task, and pair large audits with `graphify query` (AST topology) and `ctx_search` (`horus-context-mode`).

---

## 1. Modes & Horus Routing (Zero Overlap)
Leading trigger words switch behavior (or invoke `/partner` to pick via OpenCode's native `question` tool):

| Trigger | Behavior | Horus Integration |
| :--- | :--- | :--- |
| **`AUDIT:`** | **Report-first codebase/subsystem auditor.** Deliver a severity-ranked findings report with `file:line` evidence, verified strengths, and concrete fixes. **Change nothing until the user picks fixes** via `question`. | Read `references/audit-report-format.md`; run `scripts/audit.sh`, `scripts/actions-lint.sh`, `scripts/leakage-guard.sh`. |
| **`REVIEW:`** | Strict senior review (security, edge cases, perf, maintainability), then deliver the refactored fix. | Pairs with Horus `reviewer` + `vibe-critique` + `scripts/self-review.md`. |
| **`MVP:` / `PROTOTYPE:`** | Lean-but-safe builder at Tier 0/1: defer heavy Tier-2 gates as explicit `TODO`s with promotion triggers, **never relax the Security/CIA floor**. | Pairs with `vibe-grill` / `vibe-spec-plan`. |
| **`DEBUG:`** | Read actual logs first (subsystem-scoped + unfiltered), reproduce, bisect, fix root cause, prove with red-first regression test. | Delegates to Horus `systematic-debugging` + `engineering-craft/references/diagnosing-bugs` + `references/logging-and-monitoring.md`. |
| **`EXPLAIN:`** | Patient mentor: step-by-step teaching calibrated to the user's level. | Pairs with `engineering-craft/references/teach`. |
| *(default)* | Collaborative pair programmer: production-ready code, tests, and same-commit doc/diagram updates. | Follows Horus `AGENTS.md` + `plan.py` evidence gates. |

### Zero-Overlap Boundary with Existing Horus Skills
Do **not** duplicate Horus's native skills — delegate to them directly:
- **Workflow / Spec / Multi-Agent:** `AGENTS.md`, `vibe`, `subagent-driven-dev`, `planning-with-evidence`, `horus-foundry`
- **Debugging / TDD / Skill Authoring:** `systematic-debugging`, `test-driven-development`, `writing-skills`, `engineering-craft`
- **Postgres / Supabase / Frontend Security / UI & A11y:** `supabase-postgres-best-practices`, `security-audit`, `ui-ux-design-systems`, `frontend-design`, `design-engineering`

---

## 2. Phase-Aware Rigor Ladder & Constant Security Floor
- **Constant Floor (every tier — NEVER ADR-overridable):** no hardcoded secrets (per-workload credentials in a secret manager), validate & canonicalize inputs at trust boundaries, zero command/SQL/expression injection, isolated dev environment (never dev against prod, keep `.git` out of file-sync folders), authn on anything exposed, vetted FOSS deps, and a verified backup/restore story.
- **Tier 0 (Prototype / Spike):** Throwaway, never real user/tenant data. Floor + `.gitignore` + minimal README.
- **Tier 1 (MVP / Early Product):** Real users, small scale. Floor + critical-path tests, CI (lint + test + secret-scan), pinned/locked deps, structured JSON logging, backup story.
- **Tier 2 (Production / Commercial / Multi-Tenant):** Full strict posture — merge-blocking SAST/typecheck/audit gates, tenant-isolation tests, threat models, DR restore drills, SLO burn-rate alerting, compliance.
- **Promotion triggers:** real customer/tenant data · money · multi-tenant isolation · regulated/PII data · 2nd contributor · public internet exposure.
- **Environment Profile:** Optional per-user overrides live in `references/my-environment.md` (uncommitted; copy from `references/my-environment.template.md`). Shipped defaults (1Password, GitHub, Cloud Run, POSIX/Bash) are **example bindings, not mandates**.

---

## 3. On-Demand Reference Catalog (`references/`)

### Cloud, Infrastructure, SRE & Ops (10)
| Topic | Reference |
| :--- | :--- |
| Docker digest-pins, multi-stage non-root, K8s `securityContext` & `NetworkPolicy` | `references/containers-and-orchestration.md` |
| Terraform modules, locked remote state, OIDC deployer, drift detection | `references/iac-terraform.md` |
| GCP Cloud Run, GCS, BigQuery, Secret Manager, Workload Identity | `references/gcp.md` |
| RED/USE/cost metrics, SLO burn-rate alerts, DORA, SEV1 incident response, RUM | `references/observability-and-incident-response.md` |
| 3-2-1-1-0 immutable backups (Bucket Lock), PITR, scheduled restore drills | `references/disaster-recovery.md` |
| BIA, RTO/RPO, provider-outage runbooks, solo-operator bus-factor-1 | `references/business-continuity.md` |
| Timeouts, backoff+jitter, circuit breakers, bulkheads, degraded modes, kill-switches | `references/resilience-engineering.md` |
| Stateless scale, queues + DLQ, transactional outbox, DB pool ceilings | `references/scalability-and-system-design.md` |
| JSON structured logs + correlation ID, CWE-117 sanitization, reading logs before healthy | `references/logging-and-monitoring.md` |
| Tenant-scoped cache keys, invalidation, cross-tenant cache isolation | `references/caching.md` |

### Language & Platform Toolchains (7)
| Topic | Reference |
| :--- | :--- |
| Python `TypedDict` (no `dict[str, Any]`), whole-tree `mypy --strict`/`ruff`, single-file vs package | `references/python-typing-and-packaging.md` |
| FastAPI/Uvicorn/psycopg, lifespan, RLS `Depends`, non-blocking async, `SIGTERM` | `references/python-web-apis.md` |
| Bash `set -euo pipefail` gaps, `local` exit masking, atomic `mv`, `curl -f`, BATS | `references/bash-scripting.md` |
| TypeScript `strict` + `noUncheckedIndexedAccess`, runtime schemas, `no-floating-promises`, Node `SIGTERM` | `references/javascript-and-typescript.md` |
| Swift 6 concurrency, XcodeGen `project.yml`, `CKSyncEngine` hard rules, Keychain/ATS/PrivacyInfo | `references/swift-apple-development.md` |
| macOS LaunchAgent `.app` bundles, TCC/FDA, compiled Mach-O launcher | `references/macos-app-bundles.md` |
| Google Apps Script `clasp`, minimal `oauthScopes`, `PropertiesService`, `LockService`, 6-min wall | `references/google-apps-script.md` |

### Governance, Security, AI Apps & Supply Chain (12)
| Topic | Reference |
| :--- | :--- |
| NIST CSF 2.0 + SSDF 800-218, SOC 2, Well-Architected, crypto-agility & post-quantum (FIPS 203–205) | `references/compliance.md` |
| GDPR/UK-GDPR/CCPA as code: DSAR, verified erasure cascade, retention, DPIA | `references/data-protection.md` |
| In-PR STRIDE threat models, RFC 7807 errors, idempotency keys, cursor pagination, signed webhooks | `references/threat-modeling-and-api-design.md` |
| OWASP Agentic Top 10 (`ASI01`–`ASI10`), CSA MAESTRO, least agency, memory poisoning | `references/agentic-ai-security.md` |
| LLM-app patterns, stopping criteria, token/cost brakes, RAG retriever evals | `references/llm-apps.md` |
| Hostile-file sandboxing, two-zone prompt-injection fencing, RAG tenant isolation | `references/secure-data-processing.md` |
| Zero-downtime secret rotation overlap, KMS key-version re-wrap, per-workload keys | `references/secrets-and-key-rotation.md` |
| Agent action identity, session-id trailers, hash-chained off-host action logs | `references/action-identity-and-audit.md` |
| FOSS adoption vetting (OpenSSF Scorecard, license/CVE/contract test, cooldown lane) | `references/foss-adoption.md` |
| Lockstep manifests (Brewfile/npm/pip), KEV/EPSS daily re-scan SLAs | `references/package-managers.md` |
| GitHub Actions least-priv, SHA pins, `${{ }}` expression-injection guard, SBOM/SLSA | `references/github-actions.md` |
| Team repo hygiene: rulesets, required security gates, CODEOWNERS, PR review | `references/github-teams.md` |

### Quality Gates, Audit, Docs & Dev Isolation (8 + 5 Scripts)
| Topic | Reference / Script |
| :--- | :--- |
| `AUDIT:` report schema, severity taxonomy, verified-strengths-first format | `references/audit-report-format.md` |
| Enforced merge-gate taxonomy, monitor→comment→block ladder, fuzzing, frontend tests | `references/testing.md` |
| Testing single-file scripts with module-level side effects (`conftest.py` argv-patch) | `references/testing-single-file.md` |
| Cognitive complexity & AST duplication committed-threshold gates | `references/maintainability-metrics.md` |
| Diagrams-as-code (Mermaid-first), same-commit updates, `docs-render` gate | `references/diagrams-and-visual-docs.md` |
| Distilling team conventions into checkable floor-vs-ADR standards | `references/standards-authoring.md` |
| Environment isolation (no-prod-dev, git-out-of-file-sync, sandboxing) & IDE hygiene | `references/dev-environment-isolation.md`, `references/dev-environments.md` |
| Deterministic helper scripts & self-review checklist | `scripts/audit.sh`, `scripts/actions-lint.sh`, `scripts/leakage-guard.sh`, `scripts/render-diagrams.sh`, `scripts/self-review.md` |
