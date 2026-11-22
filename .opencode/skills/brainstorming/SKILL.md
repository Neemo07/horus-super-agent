---
name: brainstorming
description: "You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation using OpenCode interactive question polls"
license: MIT
compatibility: opencode
metadata:
  source: obra/superpowers (superpowers plugin of obra/superpowers-marketplace)
  edition: condensed-offline-horus-poll
---
> Provenance: offline condensed edition re-authored from the `superpowers` plugin (MIT), upgraded for Horus native OpenCode `question` polls. Run `python scripts/sync_upstream.py --only superpowers` for the verbatim upstream skill.

# Brainstorming Ideas Into Designs

Turn an idea into an approved design through structured interactive polls before any code.

## Process
1. **Understand context:** read the project state (files, docs, recent commits, `graphify-out/GRAPH_REPORT.md` if present) first.
2. **Ask 1–2 focused questions at a time via OpenCode's `question` tool** (never dump plain-text chat question lists). Put the recommended choice first with `(Recommended)` (label ≤ 30 chars, `header` ≤ 12 chars, `custom: true` so the user can always write their own answer). Cover purpose, constraints, success criteria, and non-goals.
3. **Propose 2–3 approaches via `question` poll** with trade-offs in each option's `description`; lead with your recommendation.
4. **Present the design in short sections (200–300 words)**: architecture, components, data flow, error handling, testing. Confirm via `question` (`header: "Design"`, options: `Approve Section (Recommended)`, `Revise Design`).
5. **Write it down:** save the validated design to `docs/plans/YYYY-MM-DD-<topic>-design.md` and commit it.
6. **Hand off:** only when the user approves, move to `writing-plans` / `vibe-spec-plan` (under Horus: tasks in `task_plan.md` via `plan.py`).

## Principles
YAGNI ruthlessly; use native OpenCode `question` polls for every choice; explore alternatives before settling; validate incrementally; be ready to go back and clarify. No implementation, no scaffolding, no "quick spike" before approval.
