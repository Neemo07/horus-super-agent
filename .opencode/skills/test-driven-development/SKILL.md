---
name: test-driven-development
description: "Use when implementing any feature or bugfix, before writing implementation code"
license: MIT
compatibility: opencode
metadata:
  source: obra/superpowers (superpowers plugin of obra/superpowers-marketplace)
  edition: condensed-offline
---
> Provenance: offline condensed edition re-authored from the `superpowers` plugin (MIT). Run `python scripts/sync_upstream.py --only superpowers` for the verbatim upstream skill.

# Test-Driven Development

**Iron law: no production code without a failing test first.** Wrote code before the test? Delete it and start over from the test.

## Red - Green - Refactor
1. **RED:** write one minimal test for one behaviour (clear name, real code, no mock of the unit under test). Run it. Confirm it **fails for the right reason** (feature missing, not a typo).
2. **GREEN:** write the simplest code that passes. No extra features.
3. **Verify green:** run the full suite; all pass, output clean.
4. **REFACTOR:** remove duplication, improve names; tests stay green.
5. Repeat for the next behaviour.

## Bug fixes
Reproduce with a failing test first; the test proves the fix and prevents regression.

## Rationalizations (all wrong)
"Too simple to test" - "I'll add tests after" (they pass immediately and prove nothing) - "I already manually tested" - "Deleting working code is wasteful" - "TDD slows me down".

## Checklist before done
Every new function has a test; each test was seen failing first; failures were for the expected reason; minimal code; all tests pass; edge cases and errors covered; no mocks unless unavoidable. Exceptions (throwaway prototypes, generated code, config) need the user's explicit OK.
