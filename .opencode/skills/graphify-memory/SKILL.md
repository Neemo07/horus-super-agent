---
name: graphify-memory
description: "Use for codebase architecture mapping, dependency tracing, blast-radius checks, and long-context project memory via Graphify (Graphify-Labs/graphify). Always check graphify-out/graph.json first before broad grepping."
license: Apache-2.0
compatibility: opencode
metadata:
  source: https://github.com/Graphify-Labs/graphify
---
# Graphify Knowledge Graph Memory (Zero Context Drift)

Graphify turns any codebase (code via local deterministic tree-sitter AST, plus optional docs/specs) into a persistent, queryable knowledge graph in `graphify-out/` with zero vector store and zero LLM cost for code files.

## Fast Path (Always Check First)
1. Check if `graphify-out/graph.json` exists in the project root.
2. If it exists, **query the graph before reading or grepping files**:
   - Broad context (BFS): `graphify query "<question>" --budget 1500`
   - Trace execution/data flow (DFS): `graphify query "<question>" --dfs --budget 1500`
   - Shortest dependency path: `graphify path "<SymbolA>" "<SymbolB>"`
   - Deep node explanation: `graphify explain "<Symbol>"`
   - Architecture overview: read `graphify-out/GRAPH_REPORT.md` (focus on **God Nodes** and **Surprising Connections**).
3. Cite `source_location` from the graph output, then `read` only the exact target lines to verify before editing.

## Building & Keeping the Graph Fresh
- **Install (if missing):** `uv tool install --upgrade graphifyy` (or `pip install graphifyy`).
- **Initial build (code-only AST = fast, local, 0 LLM tokens):**
  ```bash
  graphify . --no-viz
  ```
- **Incremental update after each wave / structural edit:**
  ```bash
  graphify . --update
  ```
- **Background auto-rebuild while coding (no LLM needed):**
  ```bash
  graphify . --watch
  ```
- **MCP Server mode (optional in `opencode.jsonc`):**
  ```bash
  graphify --mcp
  ```

## Honesty & Anti-Hallucination Rules
- Respect Graphify edge provenance:
  - `EXTRACTED` = explicit in AST/source (hard fact).
  - `INFERRED` = resolved across boundaries (verify in source before editing).
  - `AMBIGUOUS` = uncertain (must read source file to confirm).
- Never invent a node, edge, or call path not present in `graphify-out/graph.json` or verified via `read`.
- Never run HTML visualization on graphs > 5,000 nodes without warning the user.
- Remind the user once if `graphify-out/` is untracked in Git (suggest adding to `.gitignore` unless sharing the graph).
