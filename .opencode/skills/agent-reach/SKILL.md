---
name: agent-reach
description: "Read-only multi-platform web/content CLI & MCP (YouTube, GitHub, Reddit, X, Bilibili, Xiaohongshu, LinkedIn, web)."
license: MIT
compatibility: opencode, antigravity, dsh
metadata:
  source: Panniantong/Agent-Reach v1.6.1 (adapted for Horus signal-only output, question polls, Context Mode & tri-harness)
  version: "1.6.1-horus"
---

# Agent Reach (Read-Only Multi-Platform Content & Web CLI)

One read-only JSON CLI (`agent-reach`) and optional MCP server for searching and reading YouTube (subtitles/transcripts), GitHub, Reddit, X/Twitter, Bilibili, Xiaohongshu, V2EX, Xueqiu, LinkedIn, Boss Zhipin, Instagram, Facebook, Xiaoyuzhou podcasts, and anonymous public web fallback. **Strictly read-only** — never posts, comments, likes, messages, logs in for the user, or asks for passwords.

## 1. Route Selection & Horus Discipline
1. **Check for mounted `agent-reach` MCP tools first** (`search`, `read`, `creator_inspect`, `people_resolve`, `trend_scan`): if mounted and covering the target platform, call MCP directly without reading `references/*.md` or shelling out.
2. **Use native web/search tools first for public content:** only fall back to `agent-reach` CLI when built-in search/fetch is unavailable, blocked, or misses body text, comments, or subtitle tracks.
3. **Silent discovery (Horus signal-only):** never announce *"using the agent-reach skill"* — execute directly and report only verified content or blockers.
4. **Zero-bloat large outputs (`horus-context-mode`):** when `horus-context-mode` is active, pipe large transcripts, threads, or JSON dumps through `ctx_execute` or index via `ctx_search` instead of dumping raw payloads into chat context.
5. **Consent via native `question` tool:** before running `agent-reach add <channel>`, `agent-reach update`, `agent-reach configure`, `agent-reach login <channel>`, or `agent-reach uninstall`, ask using OpenCode's native **`question` tool** (`header: "Reach"`, concise labels ≤ 30 chars, `custom: true` — or native confirmation UI on Antigravity/DSH).

```bash
agent-reach channels                           # list actions and params per channel
agent-reach <channel> <action> [args]          # e.g. agent-reach youtube subtitle <url>
agent-reach read <url>                         # auto-detect channel from URL
agent-reach doctor --text                      # local status check (offline)
```

## 2. Install (One-Time, Optional Companion)
```bash
uv tool install "git+https://github.com/Panniantong/Agent-Reach.git"
# or: pip install "git+https://github.com/Panniantong/Agent-Reach.git"
agent-reach doctor --text
```

## 3. Error Handling (`ok: false` → `error.code`)
- `NEED_SETUP` — ask user via `question` before running `agent-reach add <channel>` or `agent-reach configure <key>`.
- `NEED_LOGIN` — keep already-gathered public results, read `references/sessions.md`, and let the user run `agent-reach login <channel>` themselves. Never ask for passwords or print cookies.
- `UPSTREAM_BROKEN` — report which platform is unavailable without retrying in a loop; ask user before running `agent-reach update` once.
- `TIMEOUT` — run `agent-reach doctor --text`; do not loop retries.
- `RATE_LIMITED` / `PLATFORM_BLOCKED` / `BUSY` — stop immediately; never switch accounts, profiles, or backends to evade rate limits or captchas.
- `NOT_FOUND` / `BAD_INPUT` — verify URL/ID or run `agent-reach channels`.

## 4. Progressive-Disclosure References (`references/`)
Read ONLY when needed:
- **`references/capabilities.md`** — declared per-platform read/search/subtitle boundaries (public vs. Reach vs. locally verified).
- **`references/sessions.md`** — dedicated headless browser lifecycle, safe single-site cookie reuse, login/logout/remove rules.
- **`references/maintenance.md`** — `doctor`, `check`, `update`, `configure`, port-9222 conflict resolution, and `uninstall --dry-run`.
---

## Horus Super-Upgrade (Tri-Harness Consent & Evidence Grounding)
- **Zero-Bloat Paging:** Never dump raw scraped threads, transcripts, or search JSON straight into chat; filter and summarize via `horus-context-mode` (`ctx_execute` / `ctx_search`).
- **Tri-Harness Consent Gate:** Before any authenticated session, cookie import, browser login, or external write/post action, require explicit user consent via OpenCode's native `question` tool (or an explicit confirmation prompt on Antigravity/DSH).
- **Strict Attribution:** Tag every retrieved external claim with its exact observed source URL and timestamp; mark unreachable/paywalled sources honestly without guessing.
