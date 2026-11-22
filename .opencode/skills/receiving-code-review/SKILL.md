---
name: receiving-code-review
description: "Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requires technical rigor and verification, not performative agreement"
license: MIT
compatibility: opencode
metadata:
  source: obra/superpowers (superpowers plugin of obra/superpowers-marketplace)
  edition: condensed-offline
---
> Provenance: offline condensed edition re-authored from the `superpowers` plugin (MIT). Run `python scripts/sync_upstream.py --only superpowers` for the verbatim upstream skill.

# Receiving Code Review

Technical evaluation, not social performance.

1. **Read** all feedback without reacting.
2. **Understand:** restate the requirement; if any item is unclear, ask about it **before implementing anything** (items may be related).
3. **Verify** each suggestion against the codebase: is it correct here, does it break something, is there a reason the current code exists, does it apply to this stack?
4. **Evaluate:** push back with evidence when the suggestion is wrong, violates YAGNI (grep for real usage before "implementing it properly"), or conflicts with prior decisions.
5. **Implement one item at a time**, in order: blocking issues, simple fixes, complex fixes; test each.

Never reply with "You're absolutely right!" or gratitude theater; state the fix or the technical objection. Acknowledge a wrong pushback factually and move on.
