---
name: vercel-react-best-practices
description: "React and Next.js performance optimization guidelines from Vercel Engineering. This skill should be used when writing, reviewing, or refactoring React/Next.js code to ensure optimal performance patterns. Triggers on tasks involving React components, Next.js pages, data fetching, bundle optimization, or performance improvements."
license: MIT
compatibility: opencode
metadata:
  author: vercel
  version: "1.0.0"
  source: https://github.com/vercel-labs/agent-skills
---
# Vercel React Best Practices

Comprehensive performance optimization guide for React and Next.js applications, maintained by Vercel Engineering. Contains 70 rules across 8 categories, prioritized by impact to guide automated refactoring and code generation.

## When to Apply

Reference these guidelines when:
- Writing new React components or Next.js pages
- Implementing data fetching (client or server-side)
- Reviewing code for performance issues
- Refactoring existing React/Next.js code
- Optimizing bundle size or load times

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|---|---|---|---|
| 1 | Eliminating Waterfalls | CRITICAL | `async-` |
| 2 | Bundle Size Optimization | CRITICAL | `bundle-` |
| 3 | Server-Side Performance | HIGH | `server-` |
| 4 | Client-Side Data Fetching | MEDIUM-HIGH | `client-` |
| 5 | Re-render Optimization | MEDIUM | `rerender-` |
| 6 | Rendering Performance | MEDIUM | `rendering-` |
| 7 | JavaScript Performance | LOW-MEDIUM | `js-` |
| 8 | Advanced Patterns | LOW | `advanced-` |

## Quick Reference

### 1. Eliminating Waterfalls (CRITICAL)
- `async-cheap-condition-before-await` — Check cheap sync conditions before awaiting flags or remote values
- `async-defer-await` — Move `await` into branches where actually used
- `async-parallel` — Use `Promise.all()` for independent operations
- `async-dependencies` — Use `better-all` for partial dependencies
- `async-api-routes` — Start promises early, await late in API routes
- `async-suspense-boundaries` — Use `<Suspense>` to stream content

### 2. Bundle Size Optimization (CRITICAL)
- `bundle-barrel-imports` — Import directly, avoid barrel files (`index.ts` re-exports)
- `bundle-analyzable-paths` — Prefer statically analyzable import and file-system paths to avoid broad bundles and traces
- `bundle-dynamic-imports` — Use `next/dynamic` for heavy components
- `bundle-defer-third-party` — Load analytics/logging after hydration
- `bundle-conditional` — Load modules only when feature is activated
- `bundle-preload` — Preload on hover/focus for perceived speed

### 3. Server-Side Performance (HIGH)
- `server-auth-actions` — Authenticate Server Actions like API routes
- `server-cache-react` — Use `React.cache()` for per-request deduplication
- `server-cache-lru` — Use LRU cache for cross-request caching
- `server-dedup-props` — Avoid duplicate serialization in RSC props
- `server-hoist-static-io` — Hoist static I/O (fonts, logos) to module level
- `server-no-shared-module-state` — Avoid module-level mutable request state in RSC/SSR
- `server-serialization` — Minimize data passed to client components
- `server-parallel-fetching` — Restructure components to parallelize fetches
- `server-parallel-nested-fetching` — Chain nested fetches per item in `Promise.all`
- `server-after-nonblocking` — Use `after()` for non-blocking operations

### 4. Client-Side Data Fetching (MEDIUM-HIGH)
- `client-swr-dedup` — Use SWR / TanStack Query for automatic request deduplication
- `client-event-listeners` — Deduplicate global event listeners
- `client-passive-event-listeners` — Use `{ passive: true }` listeners for scroll/touch
- `client-localstorage-schema` — Version and minimize `localStorage` data

### 5. Re-render Optimization (MEDIUM)
- `rerender-defer-reads` — Don't subscribe to state only used in callbacks
- `rerender-memo` — Extract expensive work into memoized components
- `rerender-memo-with-default-value` — Hoist default non-primitive props (`[]`, `{}`) outside render
- `rerender-dependencies` — Use primitive dependencies in effects
- `rerender-derived-state` — Subscribe to derived booleans, not raw values
- `rerender-derived-state-no-effect` — Derive state during render, not in `useEffect`
- `rerender-functional-setstate` — Use functional `setState(prev => ...)` for stable callbacks
- `rerender-lazy-state-init` — Pass initializer function to `useState(() => ...)` for expensive values
- `rerender-simple-expression-in-memo` — Avoid `useMemo` for simple primitives
- `rerender-split-combined-hooks` — Split hooks with independent dependencies
- `rerender-move-effect-to-event` — Put interaction logic in event handlers, not effects
- `rerender-transitions` — Use `startTransition` for non-urgent updates
- `rerender-use-deferred-value` — Defer expensive renders to keep input responsive
- `rerender-use-ref-transient-values` — Use refs for transient frequent values
- `rerender-no-inline-components` — Never define components inside components

### 6. Rendering Performance (MEDIUM)
- `rendering-animate-svg-wrapper` — Animate `div` wrapper, not SVG element directly
- `rendering-content-visibility` — Use `content-visibility: auto` for long lists
- `rendering-hoist-jsx` — Extract static JSX outside components
- `rendering-svg-precision` — Reduce SVG coordinate precision
- `rendering-hydration-no-flicker` — Use inline script for client-only theme/init data
- `rendering-hydration-suppress-warning` — Suppress expected hydration mismatches narrowly
- `rendering-activity` — Use `<Activity>` component for show/hide preservation
- `rendering-conditional-render` — Use ternary (`cond ? <A /> : null`), not `&&` with numbers/empty strings
- `rendering-usetransition-loading` — Prefer `useTransition` for loading state
- `rendering-resource-hints` — Use React DOM resource hints (`preload`, `preconnect`)
- `rendering-script-defer-async` — Use `defer` or `async` on script tags

### 7. JavaScript Performance (LOW-MEDIUM)
- `js-batch-dom-css` — Group CSS changes via classes or `cssText`
- `js-index-maps` — Build `Map` for repeated lookups instead of `.find()` in loops
- `js-cache-property-access` — Cache object properties in hot loops
- `js-cache-function-results` — Cache pure function results in module-level `Map`
- `js-cache-storage` — Cache `localStorage`/`sessionStorage` reads in memory
- `js-combine-iterations` — Combine multiple `.filter().map()` into one pass
- `js-length-check-first` — Check array length before expensive comparison
- `js-early-exit` — Return early from functions
- `js-hoist-regexp` — Hoist `RegExp` creation outside loops/renders
- `js-min-max-loop` — Use a loop for min/max instead of sorting
- `js-set-map-lookups` — Use `Set`/`Map` for $O(1)$ membership/key lookups
- `js-tosorted-immutable` — Use `.toSorted()` for immutability
- `js-flatmap-filter` — Use `.flatMap()` to map and filter in one pass
- `js-request-idle-callback` — Defer non-critical work to browser idle time

### 8. Advanced Patterns (LOW)
- `advanced-effect-event-deps` — Don't put `useEffectEvent` results in effect dependency arrays
- `advanced-event-handler-refs` — Store event handlers in refs when stability is required
- `advanced-init-once` — Initialize app-level singletons once per app load
- `advanced-use-latest` — Use `useLatest` pattern for stable callback refs

## Full Upstream Rules Sync

Run `scripts/sync-skills.ps1` (Windows) or `scripts/sync-skills.sh` (Linux/macOS) to pull the full individual `rules/*.md` and compiled `AGENTS.md` files from `https://github.com/vercel-labs/agent-skills`.
