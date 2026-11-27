---
name: horus-context-mode
description: "Keep massive logs, shell outputs, and huge files out of context via SQLite FTS5 (ctx_search, ctx_execute, ctx_batch)."
license: MIT
compatibility: opencode, antigravity, dsh
metadata:
  source: Domush/antigravity-plugin-context-mode (adapted for Horus / OpenCode)
  version: "2.1.0-horus"
---

# Horus Context Mode ("Thinking in Code")

**Horus Context Mode** keeps massive build logs, server traces, multi-thousand-line files, and raw API JSON dumps out of your context window. Instead of flooding the conversation with raw text, it indexes content into a local SQLite FTS5 database (`~/.horus-context-mode/context.db`) and runs short sandboxed scripts that return only the exact filtered answer.

> **Runtime & Tri-Harness Concurrency:** Requires Node.js **>= 22.5.0** (built-in `node:sqlite` + FTS5, zero npm dependencies). Opens `~/.horus-context-mode/context.db` with `PRAGMA journal_mode = WAL; PRAGMA busy_timeout = 5000;` so **OpenCode**, **Google Antigravity**, and **DeepSeek Harness (`dsh`)** can share it concurrently without lock corruption.

## 1. Horus 4-Layer Memory Boundary (Zero Overlap)
- **`graphify`:** codebase AST, symbol callers, god nodes, blast radius (`graphify query/path/explain`).
- **`horus-context-mode` (`ctx_*`):** high-volume raw data — build/test/sanitizer logs, huge files, bulk shell outputs, API JSON payloads.
- **`planning-with-evidence` (`plan.py`):** current repo execution plan, SHA-256 proofs, and `HANDOFF.md`.
- **`horus-memory` (`memory_*`):** cross-session, cross-project durable Markdown wiki and handoffs.

## 2. Routing Threshold & Usage Matrix
**Rule of thumb:** Any file, log, or command output expected to exceed **~200 lines or ~16 KB** MUST route through `ctx_search`, `ctx_execute`, or `ctx_batch` instead of raw `read`/`cat`.

| Task | High-Bloat Approach | Horus Context Mode (Zero Bloat) |
| :--- | :--- | :--- |
| **Searching large logs, traces, or huge files** | Unbounded `read` or `cat` / `Get-Content` | `ctx_search(queries: ["FATAL", "error"], path: "logs/app.log", reverse: true)` |
| **Filtering build/test output or huge JSON** | Dumping 5,000 lines to stdout | `ctx_execute(language: "javascript", code: "...", intent: "Summarize failing tests")` |
| **Running multi-command diagnostics** | 6 separate `shell` calls | `ctx_batch(commands: [...], queries: ["error", "failed"])` |
| **Checking token savings & DB health** | Guessing context usage | `ctx_stats()` / `ctx_doctor()` |
| **Recovering indexed session pointers** | Re-reading raw outputs | `ctx_resume()` |

## 3. MCP Tools Reference
1. **`ctx_execute`** — Run a short sandboxed script (`javascript`, `nodejs`, `python`, `shell`, `powershell`, `cmd`) to filter/aggregate large files or API responses. Full output is indexed into SQLite FTS5; only the compact result returns to context.
2. **`ctx_search`** — Reciprocal Rank Fusion (Porter BM25 + Trigram) search across indexed chunks or any `path` (file, directory, or URL) auto-indexed Just-In-Time based on mtime. Pass `"reverse": true` for tail-first log inspection (newest errors first).
3. **`ctx_batch`** — Run multiple shell commands in one call, index all combined output, and return only snippets matching `queries`.
4. **`ctx_resume`** — Retrieve current session state, active indexed sources, and compaction pointers.
5. **`ctx_stats`** — Print Horus Context Mode token-savings report (`raw bytes` vs `returned bytes`, savings %, active cutoff, exempt categories).
6. **`ctx_doctor`** — Verify SQLite FTS5 health, schema integrity, and active Node/OS runtimes.
7. **`ctx_purge`** — Clear indexed sources for `"session"`, `"worktree"`, or `"all"`.

## 4. Behavioral Rules
- **Zero raw log dumps:** Never run unbounded `cat`, `Get-Content`, `type`, unpaged `git log`, or raw `curl`/`wget` to stdout on large files. Pipe to `head`/`Select-Object -First` or route through `ctx_execute` / `ctx_search`.
- **Tail-first logs:** Always pass `"reverse": true` to `ctx_search` when diagnosing chronological logs or crash traces.
- **Standalone dashboard (optional):** Inspect live token savings and indexed chunks at `http://127.0.0.1:4177` by running:
  ```bash
  node .opencode/context-mode/dashboard/server.mjs
  ```
