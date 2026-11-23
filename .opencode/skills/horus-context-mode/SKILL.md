---
name: horus-context-mode
description: "Keep massive logs, bulk shell outputs, and huge files out of context via SQLite FTS5 (ctx_search, ctx_execute, ctx_batch, ctx_stats)."
license: MIT
compatibility: opencode
metadata:
  source: Domush/antigravity-plugin-context-mode (adapted for Horus / OpenCode)
  version: "2.0.0-horus"
---

# Horus Context Mode ("Thinking in Code")

**Horus Context Mode** keeps massive build logs, server traces, multi-thousand-line files, and raw API JSON dumps out of your OpenCode context window. Instead of flooding the conversation with raw text, it indexes content into a local SQLite FTS5 database (`~/.horus-context-mode/context.db`) and runs short sandboxed scripts that return only the exact filtered answer.

> **Runtime Requirement:** Node.js **>= 22.5.0** (uses built-in `node:sqlite` + FTS5, zero npm dependencies). Registered as the `horus-context-mode` local MCP server in `opencode.jsonc` / `opencode.v1.json`.

## Graphify vs. Horus Context Mode (Use Both Together)
- **Use `graphify`** for **codebase architecture**: symbol relationships, call graphs, god nodes, blast radius, and cross-file dependency tracing (`graphify query`, `graphify path`, `graphify explain`).
- **Use Horus Context Mode (`ctx_*`)** for **high-volume raw data**: build/test/server logs, huge generated files, bulk shell command batches, raw API/JSON payloads, and JIT full-text/trigram search inside large files or directories.

## When to Use Horus Context Mode

| Task | High-Bloat Approach | Horus Context Mode (Zero Bloat) |
| :--- | :--- | :--- |
| **Searching large logs, traces, or huge files** | Unbounded `read` or `cat` / `Get-Content` | `ctx_search(queries: ["FATAL", "error"], path: "logs/app.log", reverse: true)` |
| **Filtering build/test output or huge JSON** | Dumping 5,000 lines to stdout | `ctx_execute(language: "javascript", code: "...", intent: "Summarize failing tests")` |
| **Running multi-command diagnostics** | 6 separate `shell` calls | `ctx_batch(commands: [...], queries: ["error", "failed"])` |
| **Checking token savings & DB health** | Guessing context usage | `ctx_stats()` / `ctx_doctor()` |
| **Recovering indexed session pointers** | Re-reading raw outputs | `ctx_resume()` |

## MCP Tools Reference

1. **`ctx_execute`** — Run a short sandboxed script (`javascript`, `nodejs`, `python`, `shell`, `powershell`, `cmd`) to filter/aggregate large files or API responses. Full output is indexed into SQLite FTS5; only the compact result returns to context.
2. **`ctx_search`** — Reciprocal Rank Fusion (Porter BM25 + Trigram) search across indexed chunks or any `path` (file, directory, or URL) auto-indexed Just-In-Time based on mtime. Pass `"reverse": true` for tail-first log inspection (newest errors first).
3. **`ctx_batch`** — Run multiple shell commands in one call, index all combined output, and return only snippets matching `queries`.
4. **`ctx_resume`** — Retrieve current session state, active indexed sources, and compaction pointers.
5. **`ctx_stats`** — Print Horus Context Mode token-savings report (`raw bytes` vs `returned bytes`, savings %, active cutoff, exempt categories).
6. **`ctx_doctor`** — Verify SQLite FTS5 health, schema integrity, and active Node/OS runtimes.
7. **`ctx_purge`** — Clear indexed sources for `"session"`, `"worktree"`, or `"all"`.

## Behavioral Rules
- **Zero raw log dumps:** Never run unbounded `cat`, `Get-Content`, `type`, unpaged `git log`, or raw `curl`/`wget` to stdout on large files. Pipe to `head`/`Select-Object -First` or route through `ctx_execute` / `ctx_search`.
- **Tail-first logs:** Always pass `"reverse": true` to `ctx_search` when diagnosing chronological logs or crash traces.
- **Standalone dashboard (optional):** Inspect live token savings and indexed chunks at `http://127.0.0.1:4177` by running:
  ```bash
  node .opencode/context-mode/dashboard/server.mjs
  ```
