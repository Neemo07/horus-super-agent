---
description: Run the official Graphify v0.9.115 knowledge graph workflow (/graphify build, query, path, explain, update, wiki, or MCP).
---

Load and follow the `graphify` skill (`.opencode/skills/graphify/SKILL.md` and its bundled `references/`) immediately.

- If `graphify-out/graph.json` already exists and the request is a codebase question, run `graphify query "<question>"` (or `graphify path` / `graphify explain` / `graphify section`) directly before grepping or reading raw files.
- For fast zero-token local AST indexing, run `graphify extract . --code-only`; after code edits, run `graphify update .`.
- For full semantic + doc/media builds or flags (`--wiki`, `--obsidian`, `--no-viz`, `--mode deep`, `--watch`), follow the exact steps in the `graphify` skill.

Arguments:
$ARGUMENTS
