---
name: open-code-review
description: "Cross-model AI code review via OCR CLI (native, LLM-free delegate, GitHub PRs, 65+ language rules, SARIF, V1/V2)."
license: Apache-2.0
compatibility: opencode, antigravity, dsh
metadata:
  source: alibaba/open-code-review (unified native + delegate + PR + OpenCode V1/V2 plugin for Horus)
  version: "0.8.8-horus"
---

# Open Code Review (`ocr` — Native, Delegate & GitHub PR Pipeline)

Unifies Alibaba's **OpenCodeReview (`ocr`)** native cross-model review, LLM-free delegation mode (65+ built-in language rule packs), GitHub PR review (`scripts/review_pr.py`), SARIF/viewer output, and optional OpenCode V1/V2 plugin into one zero-bloat Horus skill.

> **Install CLI:** `npm install -g @alibaba-group/open-code-review` (or GitHub release binary).

## 1. Zero-Overlap Horus Skill Routing
| Need | Use |
| :--- | :--- |
| **External cross-model CLI review (`ocr`), 65+ language rule packs, GitHub PR `review_pr.py`, SARIF/viewer** | **`open-code-review` (this skill)** |
| In-session adversarial spec-compliance review (no external CLI) | `vibe-critique` / `/horus-review` |
| Deep OWASP/CWE/RLS/C++ memory/fuzzing security audit | `security-audit` |
| Multi-domain architectural/SRE/K8s audit report | `senior-engineering-partner` (`AUDIT:`) |

## 2. Choose Mode Automatically
1. **GitHub PR (`#number` or PR URL):** Read `references/native-and-pr.md` and run `python3 .opencode/skills/open-code-review/scripts/review_pr.py <id-or-url>` (requires `gh` auth; never bypass policy stops).
2. **Native Independent-Model Mode (OCR provider configured — true reviewer ≠ author):** Read `references/native-and-pr.md` and run:
   ```bash
   ocr review --audience agent --background "<concise business context>"
   ```
   *(Workspace changes by default; add `--from <base> --to <ref>` for branches, `-c <sha>` for one commit, `--format json` or `--format sarif` for structured output, `--preview` for dry-run.)*
3. **LLM-Free Delegation Mode (no separate OCR API key — reuses Horus's active model + OCR's 65+ language rules):** Read `references/delegate-mode.md` and run `ocr delegate preview --format json` → `ocr delegate rule --format json <files...>` → `git --no-pager diff`.

## 3. Zero-Bloat Triage, Evidence & Tri-Harness Gate
- **Context Mode discipline:** Route large JSON/SARIF review outputs or rule payloads through **`horus-context-mode`** (`ctx_search` / `ctx_execute`) instead of dumping raw JSON into chat.
- **Verify before fixing:** Cross-check reported high/critical findings against real callers with **`graphify query`** and drop false positives honestly. **Never auto-edit code unless the user asked to fix.**
- **Interactive Next Step (primary `horus` only):** Present severity-ranked verified findings (`file:line`, severity, root cause) and invoke OpenCode's native **`question` tool** (`header: "OCR Review"`, options: `Fix Critical/High (Recommended)`, `Open OCR Viewer / SARIF`, `Report Only`) — or concise text confirmation on Antigravity/DSH. Close any applied fixes via **`plan.py done --run`**.

## 4. Optional Native OpenCode V1/V2 Plugin (`ocr_review` & `ocr_health`)
The official dual OpenCode V1/V2 plugin is bundled at `references/opencode-plugin/open-code-review.ts` (not auto-enabled so OpenCode never errors if `@opencode-ai/plugin` isn't installed). Copy it to `.opencode/plugins/` (or `~/.config/opencode/plugins/`) and install `@opencode-ai/plugin` (V1) or `@opencode-ai/plugin @opencode/plugin@beta` (V2) if you want native `ocr_review` / `ocr_health` tools.
