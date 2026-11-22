# Superpowers: Systematic Debugging (4-Phase Root Cause)

**Core Principle:** ALWAYS find the root cause before attempting fixes. Symptom fixes are failure.

## The 4 Phases
| Phase | Key Activities | Success Criteria |
|---|---|---|
| **1. Root Cause** | Read full error/stack trace, reproduce deterministically, check recent git diffs, trace data flow to origin | Understand WHAT failed and WHY |
| **2. Pattern** | Find working examples in the repo and compare line-by-line against the broken path | Exact behavioral difference isolated |
| **3. Hypothesis** | Form one falsifiable theory; test with the smallest diagnostic or check | Confirmed or cleanly disproved |
| **4. Implementation** | Write a failing regression test reproducing the bug → apply minimal root-cause fix → verify full suite passes | Bug resolved, zero regressions |

## Circuit Breaker (3-Failure Rule)
If 3+ fix attempts fail on the same defect: **STOP.** Do not guess a 4th patch. Question the underlying architecture/assumptions and escalate to the user via OpenCode's `question` tool with concrete options.
