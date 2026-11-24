---
description: "Senior Engineering Partner: AUDIT: report-first audit, Tier 0-2 rigor ladder, Cloud/K8s/Terraform/SRE/DR/compliance & toolchain standards."
agent: horus
---
Load the `senior-engineering-partner` skill.

Arguments: $ARGUMENTS

- If arguments start with a mode trigger (`AUDIT:`, `REVIEW:`, `MVP:`, `PROTOTYPE:`, `DEBUG:`, `EXPLAIN:`) or name a specific domain (e.g., `terraform`, `docker`, `dr`, `fastapi`, `bash`, `swift`, `compliance`, `github-actions`, `llm-apps`), read ONLY the matching reference handbook(s) under `.opencode/skills/senior-engineering-partner/references/` and execute directly.
- If no arguments are given, invoke OpenCode's native `question` tool (`header: "Partner"`, concise labels ≤ 30 chars, `custom: true`) to let the user pick the mode (`AUDIT: Codebase Report (Recommended)`, `Cloud / K8s / Terraform / SRE`, `Compliance / Privacy / Supply Chain`, `Python / Bash / TS / Swift Standards`) before loading any reference file.
- For `AUDIT:` mode, never modify files until the user reviews the severity-ranked report and selects fixes via `question`.
