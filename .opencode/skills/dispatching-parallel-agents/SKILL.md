---
name: dispatching-parallel-agents
description: "Use when facing 2 or more independent tasks that can be worked on without shared state or sequential dependencies"
license: MIT
compatibility: opencode
metadata:
  source: obra/superpowers (superpowers plugin of obra/superpowers-marketplace)
  edition: condensed-offline
---
> Provenance: offline condensed edition re-authored from the `superpowers` plugin (MIT). Run `python scripts/sync_upstream.py --only superpowers` for the verbatim upstream skill.

# Dispatching Parallel Agents

One agent per independent problem domain, working concurrently.

## Use when
Several failures with different root causes (different test files, subsystems); problems understandable in isolation; no shared state between investigations.
## Do not use when
Failures are related (fixing one may fix others); you need whole-system understanding first; agents would edit the same files; the work is exploratory.

## Pattern
1. Group problems by domain.
2. Write a focused prompt per agent: **scope** (one file/subsystem), **goal**, **constraints** (do not touch other code), **expected output** (summary of root cause and changes).
3. Dispatch all at once.
4. Review each summary, check for conflicts, run the full suite, integrate.

Good prompts are specific, self-contained, and state the output format. Avoid "fix all the tests", missing error messages, and unbounded scope.
