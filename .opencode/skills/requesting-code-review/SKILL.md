---
name: requesting-code-review
description: "Use when completing tasks, implementing major features, or before merging to verify work meets requirements"
license: MIT
compatibility: opencode
metadata:
  source: obra/superpowers (superpowers plugin of obra/superpowers-marketplace)
  edition: condensed-offline
---
> Provenance: offline condensed edition re-authored from the `superpowers` plugin (MIT). Run `python scripts/sync_upstream.py --only superpowers` for the verbatim upstream skill.

# Requesting Code Review

Review early and often: after each task in subagent-driven work, after a major feature, before merge.

1. Get the range: `BASE=$(git merge-base HEAD origin/main)`, `HEAD=$(git rev-parse HEAD)`.
2. Dispatch a reviewer subagent with: what was implemented, the plan/requirements, base and head SHAs, a short description. Give it the diff, not your session history.
3. Act on feedback: fix **Critical** immediately, fix **Important** before proceeding, note **Minor** for later. Push back with technical reasoning if the reviewer is wrong.

Reviewer output: strengths, issues by severity (Critical / Important / Minor) with `file:line` and fix, assessment (ready to merge or not).
Never skip review because the change is "simple"; never proceed with unfixed Critical issues. Under Horus use the read-only `reviewer` agent.
