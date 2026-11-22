---
name: ui-ux-design-systems
description: "High-craft UI/UX design system engineering for desktop and web apps: visual hierarchy, 4/8px spatial grids, OKLCH semantic tokens, WCAG/APCA contrast, micro-interactions, and anti-AI-slop standards."
license: MIT
compatibility: opencode
---
# High-Craft UI / UX Design Systems

Design interfaces with the precision of top-tier native tools (Linear, Figma, Ableton, Raycast) — never generic boilerplate.

## 1. Visual Hierarchy & Layout Discipline
- **Single Focal Point per View:** Every screen has one primary action and one primary information hierarchy. Demote secondary controls via weight, contrast, or disclosure rather than cluttering toolbars.
- **Strict 4px / 8px Spatial Grid:** Spacing tokens (`4, 8, 12, 16, 24, 32, 48, 64`). Align baselines and edges across columns. Inner padding must be `<=` outer gap (law of proximity).
- **Information Density:** Match density to the user's domain — compact, scannable rows with tabular numerals (`font-variant-numeric: tabular-nums`) for pro/engineering tools; generous breathing room for editorial/onboarding screens.

## 2. Semantic Color & Contrast System
- **Build in OKLCH (or HSL with perceptual verification), never raw hex soup:**
  - Surface tiers: `bg-canvas` → `bg-surface` → `bg-elevated` (subtle 3–6% lightness steps in dark mode; crisp 1px low-alpha borders `rgba(255,255,255,0.08)` instead of heavy drop shadows).
  - Text tiers: `text-primary` (>= 7:1 contrast), `text-secondary` (>= 4.5:1), `text-muted` (non-essential metadata only).
  - One disciplined **accent color** for primary actions/focus; semantic status colors (`success`, `warning`, `danger`, `info`) reserved strictly for meaning.
- **Accessibility Non-Negotiables:** WCAG 2.1 AA minimum (4.5:1 body text, 3:1 large text & UI controls), visible `:focus-visible` ring on every interactive element, minimum 36–44px hit targets on touch/clickable controls.

## 3. Typography & Micro-Interactions
- **Type Scale:** Cap at 4–5 distinct sizes per view with clear weight contrast (`600` headings, `400/500` body/labels). Tight line-height (`1.15–1.25`) for headings, `1.45–1.55` for body prose.
- **Snappy Motion:** Fast, purposeful transitions (`120–180ms` `cubic-bezier(0.2, 0, 0, 1)` for state changes; `0ms` for hover color shifts on high-density tables). Respect `prefers-reduced-motion`.
- **Complete Interactive States:** Every interactive component MUST specify and implement: `default`, `hover`, `active`, `focus-visible`, `disabled`, `loading`, and `error`.

## 4. Anti-AI-Slop Checklist (Reject Immediately)
- Generic purple/blue gradient hero cards or glowing neon borders on utility apps.
- Cards nested inside cards inside cards (use subtle hairlines and whitespace instead).
- Unaligned icons/text, inconsistent border radii, or placeholder Lorem Ipsum.
- Dead controls, fake progress bars, or unstyled browser default scrollbars/inputs.
