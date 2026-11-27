---
description: "Run OpenCodeReview (ocr) cross-model, LLM-free delegate, or GitHub PR code review with 65+ language rules"
agent: horus
---
Load `open-code-review`.

1. If given a GitHub PR number or URL, run `python3 .opencode/skills/open-code-review/scripts/review_pr.py <target>` (never bypass policy stops).
2. Otherwise run native `ocr review --audience agent` (if an OCR provider is configured) or LLM-free `ocr delegate preview` + `ocr delegate rule` (reusing the active session model with OCR's 65+ language rule packs).
3. Route large JSON/SARIF outputs through `horus-context-mode` (`ctx_search`/`ctx_execute`), verify high/critical findings against callers with `graphify query`, and present next steps via OpenCode's `question` tool (`header: "OCR Review"`).

Target / Focus: $ARGUMENTS
