---
name: vercel-react-best-practices
description: React and Next.js performance optimization guidelines from Vercel Engineering. Use when writing, reviewing, or refactoring React or Next.js code - components, pages, data fetching, bundle size, re-renders, hydration, or any performance work. Rules are prioritized by impact (waterfalls and bundle size first).
license: MIT
compatibility: opencode
metadata:
  source: vercel-labs/agent-skills (skills/react-best-practices)
  edition: condensed-offline
---
# Vercel React Best Practices

> Provenance: offline condensed edition covering the 8 upstream categories. Rule IDs follow the upstream prefixes (`async-`, `bundle-`, `server-`, `client-`, `rerender-`, `rendering-`, `js-`, `advanced-`) but wording is re-authored. For the complete rule set with incorrect/correct code, run `python scripts/sync_upstream.py --only vercel-react-best-practices`, or fetch the guide (about 80 KB, 57 rules):
> `https://raw.githubusercontent.com/vercel-labs/agent-skills/main/skills/react-best-practices/AGENTS.md`
> single rule: `https://raw.githubusercontent.com/vercel-labs/agent-skills/main/skills/react-best-practices/rules/{rule-id}.md`

## How to use
1. Fix in priority order. CRITICAL categories move the needle most; do not micro-optimise (`js-`) while a waterfall (`async-`) exists.
2. Measure first when possible (Network tab waterfall, bundle analyzer, React Profiler). Cite `file:line` for each finding.
3. Keep behaviour identical. Optimisations must not change data, ordering or permissions.
4. In review mode, output: `# | Category | Rule ID | file:line | Impact | Fix`.

## Priority and rules
### 1. Eliminating waterfalls - CRITICAL (`async-`)
- `async-parallel`: independent awaits run with `Promise.all`, never sequentially.
- `async-defer-await`: move `await` into the branch that actually uses the value.
- `async-dependencies`: for partial dependencies start promises early, await late.
- `async-api-routes`: start independent work at the top of route handlers, await at the end.
- `async-suspense-boundaries`: stream slow sections behind `<Suspense>` instead of blocking the page.

### 2. Bundle size - CRITICAL (`bundle-`)
- `bundle-barrel-imports`: import from the concrete module, not a barrel `index` (or use `optimizePackageImports`).
- `bundle-dynamic-imports`: `next/dynamic` / `lazy` for heavy, below-the-fold or interaction-only components.
- `bundle-defer-third-party`: load analytics, chat, tag managers after hydration.
- `bundle-conditional`: load code only when the feature flag/route is active.
- `bundle-preload`: preload on hover/focus intent for likely next navigations.

### 3. Server-side performance - HIGH (`server-`)
- `server-auth-actions`: authenticate and authorise inside every Server Action like an API route.
- `server-cache-react`: `React.cache()` for per-request dedup of DB/fetch calls.
- `server-cache-lru`: cross-request LRU cache for hot, non-user-specific data.
- `server-dedup-props`: do not pass the same large data as props and again via fetch.
- `server-serialization`: pass only needed fields across the server/client boundary.
- `server-parallel-fetching`: restructure components so sibling fetches run in parallel.
- `server-after-nonblocking`: logging/analytics via `after()` so they do not block the response.

### 4. Client-side data fetching - MEDIUM-HIGH (`client-`)
- `client-swr-dedup`: use SWR/TanStack Query for request dedup, caching and revalidation.
- `client-event-listeners`: one shared global listener instead of one per component instance.
- `client-passive-event-listeners`: `{ passive: true }` for scroll/touch listeners.
- `client-localstorage-schema`: version and validate localStorage payloads; guard reads with try/catch.

### 5. Re-render optimization - MEDIUM (`rerender-`)
- `rerender-defer-reads`: do not subscribe to state (e.g. search params) only used in callbacks.
- `rerender-memo`: extract expensive subtrees into `memo` components.
- `rerender-dependencies`: use primitive dependencies in effects/memos.
- `rerender-derived-state` / `rerender-derived-state-no-effect`: compute during render, not in `useEffect` + `setState`.
- `rerender-functional-setstate`: `setX(prev => ...)` for stable callbacks.
- `rerender-lazy-state-init`: `useState(() => expensive())`.
- `rerender-move-effect-to-event`: side effects belong in event handlers when triggered by user action.
- `rerender-transitions`: `startTransition` for non-urgent updates.
- `rerender-use-ref-transient-values`: `useRef` for frequently changing values that do not affect rendering.

### 6. Rendering performance - MEDIUM (`rendering-`)
- `rendering-content-visibility`: `content-visibility: auto` for long off-screen lists.
- `rendering-hoist-jsx`: hoist static JSX out of components.
- `rendering-hydration-no-flicker`: inline script for client-only values (theme) to avoid flash.
- `rendering-hydration-suppress-warning`: `suppressHydrationWarning` only for known benign mismatches.
- `rendering-conditional-render`: use ternaries, not `&&`, when the left side can be `0`/`NaN`.
- `rendering-animate-svg-wrapper`: animate a wrapper `<div>`, not the SVG element.
- `rendering-svg-precision`: reduce SVG coordinate precision.
- `rendering-activity`: `<Activity>` to preserve state of hidden UI.
- `rendering-usetransition-loading`: `useTransition` instead of manual loading flags.

### 7. JavaScript micro-optimisations - LOW-MEDIUM (`js-`)
- `js-index-maps` / `js-set-map-lookups`: build `Map`/`Set` for repeated lookups instead of `find`/`includes` in loops.
- `js-combine-iterations`: one pass instead of chained `filter().map().filter()`.
- `js-early-exit`: return early; `js-length-check-first`: compare lengths before deep array compare.
- `js-hoist-regexp`: create RegExp once, outside loops/renders.
- `js-cache-function-results` / `js-cache-property-access` / `js-cache-storage`: memoise repeated work; read `localStorage`/cookies once.
- `js-batch-dom-css`: batch style/layout reads and writes (no layout thrashing).
- `js-tosorted-immutable`: `toSorted()` instead of mutating `sort()`; `js-min-max-loop`: loop for min/max, not sort.

### 8. Advanced patterns - LOW (`advanced-`)
- `advanced-event-handler-refs`: store handlers in refs for stable subscriptions.
- `advanced-init-once`: app-wide init once per load, not once per mount.
- `advanced-use-latest`: `useLatest` ref pattern for latest callback without re-subscribing.

## Pairing
- Data/DB and caching concerns: `speed-engineer`. Supabase queries: `supabase-postgres-best-practices`.
- Visual quality: `frontend-design`, `ui-ux-design-systems`. E2E verification: `webapp-testing`.
