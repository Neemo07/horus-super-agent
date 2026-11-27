---
name: modern-web-guidance
description: "Modern HTML/CSS/JS platform APIs, Baseline fallbacks & legacy-scan via modern-web-guidance CLI (CSS, CWV, a11y)."
license: Apache-2.0
compatibility: opencode, antigravity, dsh
metadata:
  source: GoogleChrome/modern-web-guidance (adapted & upgraded for Horus / OpenCode / Antigravity / DSH)
  version: "0.8.6-horus"
---

# Modern Web Guidance (Native Browser APIs, Baseline & Legacy Modernization)

Use **first** on HTML, CSS, and client-side JS/DOM work so Horus prefers native, accessible, browser-optimized platform APIs (with responsible Baseline fallbacks) over legacy JS boilerplate or heavy third-party libraries.

> **Skip for:** backend SQL/ORMs/API routes, CI/CD/Docker/Git/Python/C++, or trivial copy/rename edits.

## 1. Zero-Overlap Horus Skill Routing
| Need | Use |
| :--- | :--- |
| **Native HTML/CSS/DOM/JS browser APIs, Baseline support, fallbacks & `legacy-scan`** | **`modern-web-guidance` (this skill)** |
| React / Next.js RSC, bundle, hydration, server/client boundaries | `vercel-react-best-practices` |
| OKLCH design tokens, 4/8px grid, WCAG/RTL system audit/docs | `ui-ux-design-systems` |
| Physics springs, choreography, Figma MCP, landing-page craft | `design-engineering` |
| Benchmarking, profiling & backend/system optimization | `speed-engineer` |
| AppSec, OWASP, RLS, C/C++ memory safety & CI/CD hardening | `security-audit` |

## 2. Primary CLI Workflow (`npx` / `pnpx` + Zero-Bloat Context Mode)
Prefer `pnpx` if `pnpm` is installed (on Windows use `npx.cmd`; if offline use `npx --offline`; in read-only sandboxes set `NPM_CONFIG_CACHE=/tmp/npm-cache`):
1. **Search (2–5 word generic English query — omit framework/app names; split compound topics):**
   ```bash
   npx -y modern-web-guidance@latest search "light dismiss dialog"
   ```
   - Name implied UI primitives (`"confirmation modal dialog"`, not `"confirm delete"`).
   - If results are empty/weak, rephrase once with the concrete HTML/CSS/UI noun before falling back to `list`.
2. **Retrieve full guide(s) by comma-separated IDs:**
   ```bash
   npx -y modern-web-guidance@latest retrieve "light-dismiss-a-dialog,dialog"
   ```
   - Route large guide outputs (>9.5 KB) or temp files through **`horus-context-mode`** (`ctx_search` / targeted line reads) — never `cat` huge guides into context.
3. **Offline Fallback:** If network/npx is unavailable, read `references/platform-cheatsheet.md` directly.

## 3. Baseline Browser Support & Fallback Policy
- **Widely Available (Baseline High):** Safe to use directly without fallbacks.
- **Newly Available / Limited:** MUST apply the guide's lightweight fallback or feature detection (`@supports`, `'popover' in HTMLElement.prototype`) unless the project's `AGENTS.md` defines a custom Browser Support policy (e.g. `Baseline 2025`, Electron/Tauri runtime).
- **Framework Adaptation:** Adapt vanilla HTML/CSS/JS guides without dropping the native feature (use `useId()` for unique `anchor-name`/IDs, guard `window`/`HTMLElement` in SSR, keep `@starting-style` and `:root` unscoped, invoke `showModal()`/`moveBefore()` via refs).

## 4. Codebase Modernization (`legacy-scan` — Only for Broad Audits)
Do **not** run `legacy-scan` on scoped single-feature tasks. When asked to audit or modernize legacy web patterns across a repo, load `references/legacy-modernization.md`:
1. Run `npx -y modern-web-guidance@latest legacy-scan <path> --json` (route JSON through `ctx_execute`/`ctx_search`).
2. Filter every finding against its `keepWhen` / `dropWhen` rubric (drop intentional fallbacks, vendor code, lookalikes).
3. Present verified findings via OpenCode's **`question` tool** (`header: "Modernize"`, options: `Modernize All Verified (Recommended)`, `Modernize High-Impact Only`, `Report Only`) — or concise text confirmation on Antigravity/DSH — before editing.
4. Retrieve each target guide, apply minimal replacements, verify in a real browser via **`webapp-testing`** (modern path + fallback + zero console errors), and close via **`plan.py done --run`**.
