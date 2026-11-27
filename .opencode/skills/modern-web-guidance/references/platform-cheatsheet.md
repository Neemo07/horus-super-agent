# Modern Web Platform Cheatsheet (Offline Reference — 17 Disciplines)

Quick offline lookup of high-impact native browser APIs curated from `GoogleChrome/modern-web-guidance` (255+ guides). Always verify exact edge cases via `npx -y modern-web-guidance@latest retrieve "<id>"` when online.

## HTML, Top Layer & Interactive UI
- **Modals & Light Dismiss:** Native `<dialog>` + `showModal()` + `closedby="any"` (fallback: backdrop click handler); `overscroll-behavior: contain` prevents background scroll bleed.
- **Popovers & Tooltips:** Native `popover="auto"|"manual"|"hint"` + `popovertarget` + `commandfor`/`command` invokers; pair with **CSS Anchor Positioning** (`anchor-name`, `position-anchor`, `position-try-fallbacks: flip-block`) for viewport-aware dropdowns/tooltips with zero Popper.js.
- **State-Preserving DOM Moves:** `parent.moveBefore(node, ref)` moves iframes/videos/focus without resetting state (feature-detect, fallback `insertBefore`).
- **Searchable Hidden Content:** `hidden="until-found"` + `beforematch` event lets browser Ctrl+F expand collapsed accordions/sections automatically.

## CSS Layout, Color, Motion & Forms
- **Intrinsic & Size-Aware Layout:** Container queries (`@container`), `subgrid`, `:has()` parent/sibling styling, `text-wrap: balance` / `pretty`, logical properties (`margin-inline`, `padding-block`) for first-class RTL.
- **Animate Intrinsic Sizes & Entry/Exit:** `interpolate-size: allow-keywords` / `calc-size()` for animating `height: auto`; `@starting-style` + `transition-behavior: allow-discrete` for pure-CSS top-layer entry/exit animations.
- **Scroll-Driven Animations:** `animation-timeline: scroll()` / `view()` + `scroll-state()` container queries for sticky headers, scroll progress bars, and parallax with zero JS scroll listeners.
- **Theming & Contrast:** `color-scheme: light dark`, `light-dark(lightVal, darkVal)`, `oklch()`, `scrollbar-color` / `scrollbar-width` (respecting forced-colors/high-contrast).
- **Modern Forms:** `field-sizing: content` (auto-growing inputs/textareas), `:user-valid` / `:user-invalid` (validate only after interaction), `appearance: base-select` (customizable `<select>`), proper `autocomplete` tokens for address/payment/sign-in/OTP (`one-time-code`), and IME-safe Enter handling (`!event.isComposing`).

## JavaScript, Performance (CWV) & Security
- **Modern JS:** `AbortSignal.timeout()`, `Promise.withResolvers()`, `Object.groupBy()`, `structuredClone()`, non-mutating array methods (`toSorted`, `toReversed`, `with`), `element.replaceChildren()`, `Error(msg, { cause })`, `Temporal` (when Baseline/polyfilled).
- **Core Web Vitals (LCP / INP / CLS):** `fetchpriority="high"` on LCP image (never lazy-load LCP!), `content-visibility: auto` + `contain-intrinsic-size`, `scheduler.yield()` to break up long tasks, `scrollend` event, Speculation Rules (`<script type="speculationrules">`), View Transitions (`document.startViewTransition` / `@view-transition { navigation: auto; }`).
- **Security, Auth & Emerging:** Passkeys (`navigator.credentials.create/get` with `mediation: "conditional"`), `Trusted Types` + `Sanitizer API` for untrusted HTML, Subresource Integrity (`integrity` + `crossorigin`), Web Crypto (AES-GCM, ECDSA/Ed25519), Chrome Built-in AI (`Translator`, `LanguageDetector`, `Summarizer`, `LanguageModel`), and WebMCP (`navigator.modelContext`).
