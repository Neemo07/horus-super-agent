---
name: writing-plans
description: "Use when you have a spec or requirements for a multi-step task, before touching code"
license: MIT
compatibility: opencode
metadata:
  source: obra/superpowers (superpowers plugin of obra/superpowers-marketplace)
  edition: condensed-offline
---
> Provenance: offline condensed edition re-authored from the `superpowers` plugin (MIT). Run `python scripts/sync_upstream.py --only superpowers` for the verbatim upstream skill.

# Writing Plans

Write the plan as if for an engineer with zero context and doubtful taste: exact files, exact code, exact commands, tiny steps.

## Granularity
Each step is 2-5 minutes: write the failing test -> run it and see it fail -> write minimal code -> run and see it pass -> commit. DRY, YAGNI, TDD, frequent commits.

## Plan header
```
# <Feature> Implementation Plan
**Goal:** one sentence
**Architecture:** 2-3 sentences
**Tech stack:** key libraries and versions
```

## Task template
```
### Task N: <component>
**Files:** Create `path/new.ext` - Modify `path/old.ext:120-140` - Test `tests/path/test.ext`
1. Write the failing test (full code)
2. Run: `<exact command>`  Expected: FAIL with "<message>"
3. Implement minimal code (full code)
4. Run: `<exact command>`  Expected: PASS
5. Commit: `git commit -m "feat: ..."`
```
Reference relevant skills by name in the task. Save to `docs/plans/YYYY-MM-DD-<feature>.md`.

## Under Horus
Express each task as a `plan.py` line: `- [ ] T1.1 Title | accept: <exact command>` and record `OWNED_FILES` and dependencies in `.horus/STATE.md`; the long-form steps live in `docs/plans/`.
