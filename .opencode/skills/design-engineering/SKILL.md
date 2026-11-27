---
name: design-engineering
description: "23-playbook UI craft, motion, Stageshow, Figma MCP & landing-page suite: springs, gestures, break-ui, tokens, Swift."
license: MIT
compatibility: opencode, antigravity, dsh
metadata:
  source: emilkowalski/skills + Benjitaylor/skills (stageshow) + elayadesign/ai-design-skills (figma-designer, landing-page-design)
  version: "0.7.4-horus"
---

# Design Engineering Playbook Suite (Progressive Disclosure Router)

All 23 full Design Engineering playbooks (20 Emil Kowalski craft playbooks + Benji Taylor's Stageshow faux-product-UI kit + Elaya Design's `figma-designer` & `landing-page-design`) and 2 quick-reference cheatsheets live under `.opencode/skills/design-engineering/references/`. **Never load all playbooks at once** — read ONLY the specific playbook(s) matching the user's task, then execute cleanly following Horus `AGENTS.md`.

> **Quick Cheatsheets (always fast to skim first):**
> - `references/ui-cheatsheet.md` — concise UI craft & polish rules
> - `references/performance-cheatsheet.md` — composite-only motion & frame-budget rules

## Trigger → Playbook Routing Table

### Motion & Animation
| Need | Read Playbook (`references/<path>`) |
| :--- | :--- |
| Build a web animation from scratch (springs, easing, timing) | `animate/SKILL.md` (+ `animate/RECIPES.md`) |
| Coordinate multiple elements moving together (stagger, shared layout) | `choreograph/SKILL.md` (+ `choreograph/RECIPES.md`) |
| Keep web animations at 60/120fps (composite-only, frame budget) | `animation-performance/SKILL.md` |
| Translate a vague motion description into exact CSS/Motion terms | `animation-vocabulary/SKILL.md` |
| Build 1:1 interruptible drag, swipe, and sheet gestures | `gestures/SKILL.md` |
| Audit & plan motion improvements across a codebase | `improve-animations/SKILL.md` (+ `AUDIT.md`, `PLAN-TEMPLATE.md`) |
| Review animation code against high craft standards | `review-animations/SKILL.md` (+ `STANDARDS.md`) |
| Find places that should animate (and reject ones that shouldn't) | `find-animation-opportunities/SKILL.md` |
| Strip unnecessary/annoying animations (e.g. keyboard-triggered lag) | `remove-animations/SKILL.md` |

### UI Craft, Stress-Testing & Prototyping
| Need | Read Playbook (`references/<path>`) |
| :--- | :--- |
| Core design-engineering craft philosophy & UI polish | `emil-design-eng/SKILL.md` |
| Stress-test UI with worst-case data (long strings, RTL, overflow, empty) | `break-ui/SKILL.md` (+ `break-ui/CATALOG.md`) |
| Build multiple genuinely different UI variants behind a switcher | `ui-prototype/SKILL.md` (+ `ui-prototype/PICKER.md`) |
| Build faux product UI, marketing hero demos, cursor walkthroughs & bento shots (React/CSS) | `stageshow/SKILL.md` (+ `stageshow/kit/`, `examples/`, `references/`, `scripts/film.mjs`) |
| Design inside Figma via Figma MCP (two-layer Light/Dark tokens, auto layout, 25-state buttons, Foundations frame) | `figma-designer/SKILL.md` |
| Build a high-converting landing/marketing page from scratch (intake, 12-section structure, copy, SEO/AEO, tagline reveal) | `landing-page-design/SKILL.md` |
| Turn session design corrections into durable `DESIGN.md` rules | `learn-taste/SKILL.md` |
| Choose the right frontend primitive/toast/drawer/combobox library | `pick-ui-library/SKILL.md` |
| Wire up and customize Sonner toasts cleanly | `ask-sonner/SKILL.md` (+ `ask-sonner/API.md`) |

### Apple, Mobile & Native
| Need | Read Playbook (`references/<path>`) |
| :--- | :--- |
| Apple HIG fluid/physical motion & interface craft on the web | `apple-design/SKILL.md` |
| Make a web app feel genuinely native on mobile (CSS, viewport, touch) | `mobile-native/SKILL.md` |
| Build animations in React Native & Expo (Reanimated) | `animate-expo/SKILL.md` (+ `animate-expo/RECIPES.md`) |
| Write modern Swift (value types, Swift 6 concurrency, SwiftUI) | `write-swift/SKILL.md` |
| Unsure which playbook fits | `ask-emil/SKILL.md` (or ask via OpenCode `question` tool) |

## OpenCode & Horus Integration Rules
- **Interactive Choices:** If the user invokes `/design` without a clear goal (and you are primary `horus`), call OpenCode's native **`question` tool** (`header: "Design"`, concise labels ≤ 30 chars, `custom: true`) to pick the workflow instead of dumping a text menu.
- **Pair with Horus Tools:** Use `graphify query` to find affected UI components first, `ui-ux-design-systems` for OKLCH tokens/accessibility, and `webapp-testing` (Playwright) to visually verify rendered animations and `break-ui` edge cases.
- **Durable Taste (`DESIGN.md`):** When running `learn-taste`, ensure `AGENTS.md` references `DESIGN.md` so future Horus sessions inherit the user's design rules automatically.
---

## Horus Super-Upgrade (Design-System & Verification Bridge)
- **Clear Skill Routing:** Pair `design-engineering` (springs, choreography, Figma MCP sync, landing-page craft) with `ui-ux-design-systems` (OKLCH two-layer tokens, WCAG 2.2 AA, `dir="rtl"` logical CSS) and `native-gui-architecture` (Win32/Direct2D/Qt/ImGui desktop).
- **Motion & A11y Non-Negotiables:** Honor `@media (prefers-reduced-motion: reduce)` on every animation, avoid physical `left`/`right` layout assumptions when RTL applies, and verify rendered motion/layout in a real browser via `webapp-testing` before closing UI waves.
