# TaskMasterProMax Bridge: Complexity Scoring, Tags, Portfolio & Optional MCP

Zero-bloat integration of TaskMasterProMax's strongest planning capabilities directly into Horus's `planning-with-evidence` workflow (compatible with OpenCode, Google Antigravity, and DeepSeek Harness).

## 1. Complexity Scoring (1–10) & Dynamic Subtask Expansion
Before dispatching Wave 1 on any non-trivial plan, score every task `1–10`:
- **1–3 (Simple):** 1 file, deterministic proof → dispatch directly.
- **4–5 (Moderate):** 2–3 files, clear contract → dispatch with 4-Line Pre-Edit Contract.
- **6–10 (Complex / High-Risk):** cross-module, concurrency, security, or schema migration → **MUST expand into 2–5 atomic subtasks** (e.g. `T2.1a`, `T2.1b`) with explicit `depends:` and `| accept:` proofs before executing.

## 2. Dependency Cycle Validation & Tag/Branch Isolation
- Verify every `depends:` edge in `task_plan.md` points to an existing task ID and forms a strict DAG (zero self-loops or cycles).
- Keep one active feature/branch per tag or worktree (`horus/<branch>`) so parallel features never mix unrelated tasks.

## 3. Multi-Project Local Portfolio Dashboard (`/portfolio`)
Launch the zero-dependency, loopback-only, CSP-hardened Node 22+ portfolio console (upgraded from TaskMasterProMax to read **Horus `task_plan.md` + `.horus/plan_state.json` `[PROVEN]`/`[UNPROVEN]` badges**, **TaskMasterProMax `.taskmaster/tasks/tasks.json`**, and **`.todo.md`**):
```bash
node .opencode/dashboard/server.mjs              # http://127.0.0.1:8917/ (saves to ~/.horus-portfolio/portfolio.json)
node .opencode/dashboard/demo.mjs --simulate     # Try 3 synthetic projects live
```

## 4. Optional TaskMasterProMax MCP / CLI Interop (Disabled by Default)
Horus already provides mechanical SHA-256 proofs (`plan.py`) and zero-bloat orchestration, so TaskMasterProMax's 36-tool MCP is **disabled by default** in `opencode.jsonc`. If you build TaskMasterProMax locally (`npm ci && npm run build`) and want its `.taskmaster/tasks/tasks.json` MCP tools in OpenCode:
1. Set `"enabled": true` on `"taskmaster-promax"` in `opencode.jsonc` and point its command to `["node", "/abs/path/to/taskmaster-promax/dist/mcp-server.js"]`.
2. Keep `plan.py done --run` as the mechanical proof gate (TaskMasterProMax `done` status alone does not run or hash acceptance tests).
