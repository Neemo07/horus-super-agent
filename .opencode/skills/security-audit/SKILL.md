---
name: security-audit
description: "Defensive AppSec & hardening audit: OWASP/API/Auth/RLS, C/C++ mitigations & libFuzzer, CI/CD & supply-chain CWE remediation."
license: MIT
compatibility: opencode
metadata:
  version: "0.4.7-horus"
---

# Horus Defensive Security & Hardening Audit

Evidence-backed, **strictly defensive** security auditing for your own repositories, APIs, native C/C++ binaries, containers, and CI/CD pipelines. Every finding cites exact `file:line`, CWE ID, blast radius, and a concrete remediation patch.

## 1. Scope & Authorization Gate
- Audit **only** code, configs, and local test environments owned by the user or explicitly authorized for defensive review.
- Never generate weaponized exploit payloads, evasion/obfuscation code, phishing lures, or unauthorized network scans. Focus on **root-cause vulnerability identification, defensive reproduction tests (unit/fuzz tests), and hardening fixes**.

## 2. Audit Domains

### A. Web, API & Authentication Hardening
- **Access Control (CWE-639 / CWE-862):** Verify server-side ownership/RBAC checks and Postgres RLS policies on every endpoint and mutation (zero client-trusted roles or IDs).
- **Injection & Deserialization (CWE-89 / CWE-78 / CWE-502):** Enforce parameterized SQL queries, shell-free `execFile`/argv arrays, strict schema validation (Zod/Pydantic), and safe JSON parsing.
- **Auth, JWT & OAuth2 (CWE-287 / CWE-347):** Verify explicit JWT algorithm allowlists (reject `none` and key-confusion), short-lived access tokens + refresh rotation, PKCE + `state` validation on OAuth flows, and `HttpOnly; Secure; SameSite` cookies.
- **SSRF, Uploads & Concurrency (CWE-918 / CWE-434 / CWE-362):** Restrict outbound fetches to allowlisted hosts/private-IP blocks, validate upload MIME + magic bytes + size limits outside webroot, and guard financial/quota mutations with DB transactions/idempotency keys.

### B. C / C++20 / Win32 Memory Safety & Defensive Fuzzing
- **Memory & Arithmetic (CWE-119 / CWE-190 / CWE-416):** Audit buffer bounds, signed/unsigned conversions, x64 pointer width (`uintptr_t`/`size_t`), `NULL`/error-path `HANDLE` cleanup, and TOCTOU file races.
- **Compiler & Linker Mitigations:** Verify MSVC (`/W4 /WX /GS /guard:cf /DYNAMICBASE /NXCOMPAT /HIGHENTROPYVA`) or Clang/GCC (`-Wall -Wextra -Werror -fstack-protector-strong -D_FORTIFY_SOURCE=3 -fPIE -Wl,-z,relro,-z,now`).
- **Defensive Fuzzing:** Write targeted `libFuzzer` / `AFL++` / sanitizer (`-fsanitize=address,undefined`) harnesses for local parsers and protocol decoders to eliminate crashes before release.

### C. CI/CD, Supply Chain, Containers & Crypto
- **Secrets & Pipelines (CWE-798):** Scan for hardcoded keys/tokens, unpinned GitHub Actions (pin to full commit SHAs), excessive `GITHUB_TOKEN` permissions, and unsafe `pull_request_target` script injection.
- **Dependencies:** Verify lockfiles are committed, private package scopes are protected against dependency confusion, and `npm audit` / `pip-audit` / `cargo audit` pass.
- **Containers & Cloud:** Verify non-root `USER`, minimal base images, dropped Linux capabilities, read-only rootfs where possible, TLS 1.2+/1.3 only, and modern AEAD ciphers (AES-GCM / ChaCha20-Poly1305) + Argon2id/scrypt for passwords.

## 3. Output Format & OpenCode Interactive Flow
Use `graphify query` (to trace trust boundaries and callers) and `ctx_search` (for large configs/logs), then output:
1. **Severity-Ranked Findings Table:** `CRITICAL` / `HIGH` / `MEDIUM` / `LOW` | `CWE` | `file:line` | Concrete Fix.
2. **Hardening Checklist:** compiler/header/CI/RLS controls verified vs missing.
3. **Interactive Next Step (primary `horus` only):** invoke OpenCode's native **`question` tool** (`header: "Sec Audit"`, options: `Fix Critical/High Now (Recommended)`, `Add Regression Tests`, `Export Security Report`).
