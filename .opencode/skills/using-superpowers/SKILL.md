---
name: using-superpowers
description: "Use when starting any conversation - establishes how to find and use skills, requiring a skill check before any response or action"
license: MIT
compatibility: opencode
metadata:
  source: obra/superpowers (superpowers plugin of obra/superpowers-marketplace)
  edition: condensed-offline
---
> Provenance: offline condensed edition re-authored from the `superpowers` plugin (MIT). Run `python scripts/sync_upstream.py --only superpowers` for the verbatim upstream skill.

# Using Superpowers

If a skill might apply (even a 1% chance), load it before responding or acting. Skills exist because the shortcut feels fine and is not.

## Order
1. User instructions and AGENTS.md always win over skills.
2. Process skills first (`brainstorming`, `systematic-debugging`), then implementation skills (`test-driven-development`, stack skills).
3. Rigid skills (TDD, debugging, verification) are followed exactly. Flexible skills (patterns) are adapted.

## Rationalizations that mean STOP and load the skill
"This is simple" - "I need context first" - "Let me explore first" - "I remember this skill" - "The skill is overkill" - "I'll just do this one thing first". Simple tasks become complex; the check costs seconds.

## Under Horus
Skill discovery is silent: no "I will use skill X" narration. `plan.py` plans and `plan.py done --run` evidence closure replace markdown checklists and todo-list ticking.
