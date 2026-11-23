---
description: Inspect Horus Context Mode token savings (`ctx_stats`), run database diagnostics (`ctx_doctor`), or run a JIT FTS5 search (`ctx_search`) without bloating the OpenCode context window.
---

Load and follow the `horus-context-mode` skill immediately:

1. If `$ARGUMENTS` is empty or asks for status/health, call `ctx_stats` and `ctx_doctor` via the `horus-context-mode` MCP server and report the terse savings summary + health status.
2. If `$ARGUMENTS` specifies a file, log, or query, run `ctx_search` (with `"reverse": true` for logs) or `ctx_execute` to return only the compact filtered findings.
3. If `$ARGUMENTS` asks for the dashboard, print the standalone launch command: `node .opencode/context-mode/dashboard/server.mjs` (or `node ~/.config/opencode/context-mode/dashboard/server.mjs` for global installs).

Arguments:
$ARGUMENTS
