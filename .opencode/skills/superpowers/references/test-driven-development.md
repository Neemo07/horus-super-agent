# Superpowers: Test-Driven Development (RED → GREEN → REFACTOR)

**Core Principle:** If you didn't watch the test fail first, you don't know if it tests the right thing.

## The Cycle
1. **RED:** Write one minimal, clear test that expresses the exact required behavior (one concept per test — if the test name has "and", split it).
2. **Watch it fail:** Run the test command and verify it fails for the *expected* reason (missing feature/bug, not syntax or import error).
3. **GREEN:** Write the smallest, cleanest production code that makes the test pass. No speculative extras.
4. **Watch it pass:** Run the test suite and verify all tests pass with zero warnings.
5. **REFACTOR:** Clean duplication, sharpen naming, and re-run tests to confirm green.

## When Stuck
| Problem | Solution |
|---|---|
| Don't know how to test | Write the wished-for API and assertion first |
| Test too complicated | Design is too complicated — simplify the interface |
| Must mock everything | Code is too coupled — use dependency injection / pure functions |
| Test setup huge | Extract small test helpers; if still huge, simplify design |
