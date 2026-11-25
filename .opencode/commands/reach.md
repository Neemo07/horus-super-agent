---
description: "Read-only multi-platform content & web reader via Agent Reach CLI/MCP (YouTube subtitles, GitHub, Reddit, X, Bilibili, Xiaohongshu, LinkedIn, V2EX, web)."
agent: horus
---
Load the `agent-reach` skill silently.

Arguments: $ARGUMENTS

- If arguments include a URL or platform command (e.g., `read <url>`, `youtube subtitle <url>`, `reddit search "..."`, `doctor`, `channels`), route directly (preferring mounted `agent-reach` MCP tools if present, otherwise `agent-reach` CLI). Route large transcripts or JSON responses through `horus-context-mode` (`ctx_execute` / `ctx_search`) when active.
- If no arguments are given, call OpenCode's native `question` tool (`header: "Reach"`, concise labels ≤ 30 chars, `custom: true`: `Read URL / Transcript (Recommended)`, `Search Platform`, `Check Status (doctor)`, `List Channels & Actions`) before running commands.
- Always confirm via `question` before installing channels (`add`), logging in (`login`), updating (`update`), or uninstalling (`uninstall`). Never post/write or ask for passwords.
