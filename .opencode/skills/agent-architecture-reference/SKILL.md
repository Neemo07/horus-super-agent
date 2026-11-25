---
name: agent-architecture-reference
description: "17-chapter EN/ZH coding-agent harness architecture reference (query loop, tools, plugins, compaction, swarms; query via ctx_search)."
license: MIT
compatibility: opencode, antigravity, dsh
metadata:
  source: claude-reviews-claude (17-chapter EN/ZH architectural deep-dive, adapted for OpenCode & Horus)
  version: "0.4.8-horus"
---

# Coding-Agent Architecture Reference (17 Chapters — EN / ZH)

A progressive-disclosure architectural reference covering production coding-agent harness internals (derived from the 17-chapter EN/ZH deep-dive in `references/en/` and `references/zh-CN/`).

> **Context-Window Discipline (Horus Context Mode):** Chapters are 16–44 KB each. Never bulk-read multiple chapters into context. Prefer `ctx_search(queries: ["..."], path: ".opencode/skills/agent-architecture-reference/references/en/<file>.md")` or targeted `read` line slices on the exact chapter you need. Match the user's language (`references/en/` for English, `references/zh-CN/` for Chinese).

## Chapter Routing Table

| # | Topic | Reference File (`references/<lang>/...`) |
| :--- | :--- | :--- |
| 00 | System Overview & Subsystem Map | `00-overview.md` |
| 01 | Query Engine & Streaming Turn Loop | `01-query-engine.md` |
| 02 | Tool System, Schemas & Dispatch | `02-tool-system.md` |
| 03 | Coordinator & Multi-Step Orchestration | `03-coordinator.md` |
| 04 | Plugin System & Extension Lifecycle | `04-plugin-system.md` |
| 05 | Hook System & Interception Points | `05-hook-system.md` |
| 06 | Shell / Bash Execution Engine & Safety | `06-bash-engine.md` |
| 07 | Permission Pipeline & Policy Evaluation | `07-permission-pipeline.md` |
| 08 | Agent Swarms & Subagent Isolation | `08-agent-swarms.md` |
| 09 | Session Persistence & Storage | `09-session-persistence.md` |
| 10 | Context Assembly & Prompt Caching | `10-context-assembly.md` |
| 11 | Compaction System & Long-Context Recovery | `11-compact-system.md` |
| 12 | Startup Bootstrap & Initialization | `12-startup-bootstrap.md` |
| 13 | Bridge System & External Transports | `13-bridge-system.md` |
| 14a | UI State Management | `14-ui-state-management.md` |
| 14b | UI State & Terminal Rendering | `14-ui-state-rendering.md` |
| 15 | Services & LLM API Layer | `15-services-api-layer.md` |
| 16 | Infrastructure & Configuration | `16-infrastructure-config.md` |
| 17 | Telemetry, Privacy & Operations | `17-telemetry-privacy-operations.md` |

## When to Use in OpenCode / Horus
- Designing or extending OpenCode plugins, MCP servers, permission pipelines, compaction strategies, or multi-agent orchestrators (like Horus itself).
- Comparing architectural trade-offs (e.g., prompt-cache prefix stability, subagent isolation, tool-call sandboxing, session resume) and grounding recommendations in concrete chapter sections.
