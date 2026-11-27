---
name: ui-ux-design-systems
description: "Design system tokens (OKLCH, 4/8px grid, WCAG/APCA) plus Audit, Document, and Extend modes for desktop and web UI."
license: MIT
compatibility: opencode, antigravity, dsh
metadata:
  version: "0.8.2-horus"
---
# High-Craft UI / UX Design Systems (Architecture, Audit, Docs & Extend)

Design, audit, document, and extend interfaces with the precision of top-tier native tools (Linear, Figma, Ableton, Raycast) — never generic boilerplate.

> **Skill Routing Boundary:** Use `ui-ux-design-systems` for token architecture, layout/grid, WCAG/RTL accessibility, and system Audit/Docs/Extend; pair with `design-engineering` for physics-based motion/springs, Figma MCP token sync, or landing-page conversion; pair with `native-gui-architecture` for Win32/Direct2D/Qt/ImGui desktop surfaces.

## 1. Visual Hierarchy, Spatial Grid & RTL Logical Layout
- **Single Focal Point per View:** Every screen has one primary action and one primary information hierarchy. Demote secondary controls via weight, contrast, or disclosure rather than cluttering toolbars.
- **Strict 4px / 8px Spatial Grid:** Spacing tokens (`4, 8, 12, 16, 24, 32, 48, 64`). Align baselines and edges across columns. Inner padding must be `<=` outer gap (law of proximity).
- **Information Density:** Match density to the user's domain — compact, scannable rows with tabular numerals (`font-variant-numeric: tabular-nums`) for pro/engineering tools; generous breathing room for editorial/onboarding screens.
- **Logical CSS & First-Class RTL (`dir="rtl"`):** Use logical properties (`margin-inline`, `padding-block`, `inset-inline-start`, `border-start-start-radius`, `text-align: start`) instead of physical `left`/`right` so Arabic/Hebrew/bilingual layouts mirror cleanly with zero layout breakage.

## 2. Two-Layer Semantic Color & Contrast System
- **Build in OKLCH (two layers: primitive `--raw-*` → semantic `--bg-*`/`--text-*`/`--border-*`), never raw hex soup:**
  - Surface tiers: `bg-canvas` → `bg-surface` → `bg-elevated` (subtle 3–6% lightness steps in dark mode; crisp 1px low-alpha borders `rgba(255,255,255,0.08)` instead of heavy drop shadows).
  - Text tiers: `text-primary` (>= 7:1 contrast), `text-secondary` (>= 4.5:1), `text-muted` (non-essential metadata only).
  - Theme parity: support `@media (prefers-color-scheme)` + explicit `[data-theme="light"|"dark"]` toggle without flash of unstyled theme (FOUC).
  - One disciplined **accent color** for primary actions/focus; semantic status colors (`success`, `warning`, `danger`, `info`) reserved strictly for meaning.
- **Accessibility Non-Negotiables:** WCAG 2.2 AA minimum (4.5:1 body text, 3:1 large text & UI controls), visible `:focus-visible` ring (`>= 2px` offset) on every interactive element, minimum 36–44px hit targets on touch/clickable controls.

## 3. Fluid Typography & Micro-Interactions
- **Fluid Type Scale (`clamp()`):** Cap at 4–5 distinct sizes per view with clear weight contrast (`600` headings, `400/500` body/labels) and fluid display sizing (`clamp(min, vw, max)`). Tight line-height (`1.15–1.25`) for headings, `1.45–1.55` for body prose.
- **Snappy Motion:** Fast, purposeful transitions (`120–180ms` `cubic-bezier(0.2, 0, 0, 1)` for state changes; `0ms` for hover color shifts on high-density tables). Always honor `@media (prefers-reduced-motion: reduce)`.
- **Complete Interactive States:** Every interactive component MUST specify and implement: `default`, `hover`, `active`, `focus-visible`, `disabled`, `loading`, and `error`.

## 4. Anti-AI-Slop Checklist (Reject Immediately)
- Generic purple/blue gradient hero cards or glowing neon borders on utility apps.
- Cards nested inside cards inside cards (use subtle hairlines and whitespace instead).
- Unaligned icons/text, inconsistent border radii, or placeholder Lorem Ipsum.
- Dead controls, fake progress bars, or unstyled browser default scrollbars/inputs.

---

## 5. Operational Modes (Audit, Document & Extend)

Pick the mode that matches the task (if unclear and running as primary `horus`, ask via OpenCode's native `question` tool with `header: "DS Mode"`, options: `Audit System (Recommended)`, `Document Component`, `Extend Pattern`).

### A. Audit Mode (Evidence-Backed `file:line` Scan)
Use `graphify query` (for component usage/blast radius) and `ctx_search` / `grep` to scan for:
1. **Hardcoded values:** raw `#hex`/`rgb()`/`px` colors, spacing, radii, z-index, or font sizes bypassing semantic tokens.
2. **Naming drift:** inconsistent token or prop names (e.g. `primary` vs `brand`, `sm` vs `small`, mixed camel/kebab tokens).
3. **Component duplication:** duplicate or near-duplicate buttons, modals, inputs, badges, or tables across folders.
4. **Missing states & RTL leaks:** interactive controls missing `hover`/`active`/`focus-visible`/`disabled`/`loading`/`error`/`empty` states, or physical `margin-left`/`right` breaking `dir="rtl"`.
5. **A11y gaps:** contrast below WCAG 2.2 AA, missing `aria-label`/roles, broken keyboard focus order/Escape handling, or hit targets `< 36px`.

**Output format:** terse severity-ranked table (`BLOCKER` / `MAJOR` / `MINOR`) with exact `file:line` and concrete token/primitive replacement. If running as `horus`, offer next steps via `question` (`header: "DS Audit"`, options: `Fix Blockers (Recommended)`, `Generate Docs`, `Write Migration Plan`).

### B. Documentation Mode (Component Spec)
For each documented component, produce:
- **Props & Variants Table:** prop name, type, default, and visual/behavioral effect.
- **State Matrix:** exact behavior and token bindings for `default`, `hover`, `active`, `focus-visible`, `disabled`, `error`, and `loading`.
- **A11y Contract:** semantic HTML element / ARIA `role`, keyboard shortcuts (`Tab`, `Enter`/`Space`, `Escape`, Arrow keys), focus management, and screen-reader announcements.
- **Do / Don't Examples:** 2–3 concrete code/usage pairs showing intended vs. anti-pattern usage.

### C. Extend Mode (New Pattern Design)
When designing a new component or pattern:
1. **Reuse first:** inspect existing tokens and primitives via `graphify query` / `grep` — compose from existing primitives instead of inventing parallel abstractions.
2. **Token compliance:** bind strictly to existing OKLCH color, 4/8px spacing, radius, and typography tokens (add new tokens only when a genuine semantic gap exists).
3. **Edge-case coverage:** specify dark/light parity, responsive breakpoints, RTL (`dir="rtl"`) mirroring, and all 7 interactive states.
4. **Trade-offs & verification:** record key API trade-offs in `findings.md`, and verify rendered web components in a real browser via `webapp-testing` (Playwright) before marking done.
