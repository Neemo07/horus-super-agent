---
description: "Modernize legacy HTML/CSS/JS patterns using Modern Web Guidance (legacy-scan, Baseline fallbacks, Playwright proof)"
agent: horus
---
Load `modern-web-guidance` and `references/legacy-modernization.md`.

Run `npx -y modern-web-guidance@latest legacy-scan <target> --json` (routed through `ctx_execute`/`ctx_search`), filter false positives against `keepWhen`/`dropWhen`, present verified findings via OpenCode's `question` tool (`header: "Modernize"`), and apply approved modernizations with Baseline fallbacks and `webapp-testing` browser proof.

Target / Scope: $ARGUMENTS
