---
description: Check ai-memory health (`ai-memory doctor`), query cross-session/cross-project wiki memory, manage cross-agent handoffs, or check cross-repo inbox (`horus-memory`).
---

Load and follow the `horus-memory` skill immediately:

1. If `$ARGUMENTS` is empty, run `ai-memory --version` and `ai-memory doctor` (report terse health status; if not installed, show the 2-step install commands from `horus-memory`), then invoke OpenCode's native `question` tool (`header: "Memory"`, options: `Query Project Memory (Recommended)`, `Check Pending Handoffs`, `Check Cross-Repo Inbox`, `Lint / Maintain Wiki`).
2. If `$ARGUMENTS` specifies a query, handoff, page write, inbox check, or lint request, read ONLY the matching handbook under `.opencode/skills/horus-memory/references/` and execute via `memory_*` MCP tools (or `ai-memory call <tool> '<json>'` fallback).

Arguments:
$ARGUMENTS
