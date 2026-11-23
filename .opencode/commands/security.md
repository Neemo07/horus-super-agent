---
description: Run a defensive AppSec, memory-safety, CI/CD, and configuration hardening audit (`security-audit` skill) with CWE-grounded `file:line` remediation steps.
---

Load and follow the `security-audit` skill immediately:

1. If `$ARGUMENTS` specifies a target area (e.g. `auth`, `api`, `c++`, `ci`, `containers`, or specific files), audit those targets using `graphify query` + targeted reads and produce a severity-ranked (`CRITICAL`/`HIGH`/`MEDIUM`/`LOW`) CWE-grounded remediation report.
2. If `$ARGUMENTS` is empty, invoke OpenCode's native `question` tool (`header: "Sec Scope"`, options: `Full Repo Audit (Recommended)`, `Web / API / Auth`, `C/C++ Memory & Mitigations`, `CI/CD & Supply Chain`) before scanning.
3. After reporting findings, offer remediation via `question` (`header: "Sec Audit"`).

Target / scope:
$ARGUMENTS
