---
name: systematic-debugging
description: "Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes"
license: MIT
compatibility: opencode
metadata:
  source: obra/superpowers (superpowers plugin of obra/superpowers-marketplace)
  edition: condensed-offline
---
> Provenance: offline condensed edition re-authored from the `superpowers` plugin (MIT). Run `python scripts/sync_upstream.py --only superpowers` for the verbatim upstream skill.

# Systematic Debugging

**Iron law: no fixes without root-cause investigation first.** Symptom patches create new bugs.

## Phase 1 - Root cause
Read the error completely (stack trace, line numbers). Reproduce it reliably. Check recent changes. In multi-component systems add diagnostics at each boundary to see where data breaks. Trace bad values backwards to their source.
## Phase 2 - Pattern analysis
Find similar working code; list every difference between working and broken; understand dependencies and assumptions.
## Phase 3 - Hypothesis and test
State one hypothesis ("X is the cause because Y"). Change one variable at a time. If it fails, form a new hypothesis; do not stack fixes.
## Phase 4 - Implementation
Create a failing test (`test-driven-development`), apply one fix at the root cause, verify the test and the suite.

## Escalation
After **3 failed fixes** stop: the architecture or an assumption is likely wrong. Discuss with the user before attempt 4.

## Red flags
"Quick fix for now", "just try changing X", "it's probably Y", proposing a fix before tracing data flow, fixing several things at once.
