# Legacy Web Modernization & Baseline Fallback Playbook

Use this playbook **only** during broad codebase modernization audits (e.g., `/modernize`) — never during scoped single-feature edits.

## 1. 4-Step `legacy-scan` Workflow
1. **Scan (Zero-Bloat):**
   ```bash
   npx -y modern-web-guidance@latest legacy-scan <target-path> --json
   ```
   Route large JSON outputs through `horus-context-mode` (`ctx_execute` / `ctx_search`). Note that `legacy-scan` covers ~20% of the 255+ guide corpus (deterministic rules only).
2. **Verify Against `keepWhen` / `dropWhen`:**
   - **Drop false positives:** intentional browser fallbacks, polyfills, third-party/vendor bundles, or lookalike helper functions.
   - **Keep verified wins:** legacy JS modals/tooltips/accordions, `innerHTML` clearing (`replaceChildren`), manual `Promise` deferral (`Promise.withResolvers`), mutating `.sort()` clones (`toSorted`), missing `isComposing` IME checks, or unoptimized LCP images.
3. **Confirm Before Editing:** Present a severity/impact-ranked summary table (`file:line`, legacy pattern, modern replacement, Baseline status) and get user approval via OpenCode's `question` tool (`header: "Modernize"`) or concise text confirmation on Antigravity/DSH.
4. **Modernize & Prove:**
   - Call `npx -y modern-web-guidance@latest retrieve "<guide-id>"` for each approved finding.
   - Apply minimal replacements while preserving required fallbacks for non-Widely-Available features.
   - Verify rendered behavior in a real browser (`webapp-testing`) + re-run `legacy-scan` on modified files + close via `plan.py done --run`.

## 2. Browser Support Policy Template (for Project `AGENTS.md`)
```markdown
## Browser Support Policy
- Target: Baseline Widely Available (or `Baseline 2025` / Chromium-only Electron).
- Newly Available features: allowed only with lightweight feature-detected fallbacks (<= 20 lines, zero new npm dependencies).
```

## 3. Framework Adaptation Guardrails (React / Vue / Angular / SSR)
- **TypeScript attributes:** Cast newly shipped HTML attributes cleanly (`{...({ popover: 'hint', closedby: 'any' } as any)}`) rather than dropping native behavior.
- **SSR safety:** Guard `window`, `document`, and `HTMLElement` in client effects; load optional polyfills dynamically (`import('<pkg>')`) — never copy from `node_modules`.
- **Scoped CSS & IDs:** Generate unique per-instance IDs/`anchor-name`s (`useId()`), and keep `@starting-style` and `:root` rules unscoped.
