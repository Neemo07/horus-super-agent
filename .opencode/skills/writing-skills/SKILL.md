---
name: writing-skills
description: "Use when creating new skills, editing existing skills, or verifying skills work before deployment"
license: MIT
compatibility: opencode
metadata:
  source: obra/superpowers (superpowers plugin of obra/superpowers-marketplace)
  edition: condensed-offline
---
> Provenance: offline condensed edition re-authored from the `superpowers` plugin (MIT). Run `python scripts/sync_upstream.py --only superpowers` for the verbatim upstream skill.

# Writing Skills

Writing skills is test-driven development applied to process documentation.

## RED - GREEN - REFACTOR
1. **RED:** run a pressure scenario with a subagent **without** the skill; record the exact rationalizations and failures.
2. **GREEN:** write the minimal skill that addresses those specific failures; re-run with the skill; it must comply.
3. **REFACTOR:** find new loopholes, add explicit counters, re-test until bulletproof.

## Structure
`skills/<name>/SKILL.md` with frontmatter `name` (lowercase, hyphens, matches the directory) and `description`. The description states **when to use** (triggers and symptoms), never a summary of the workflow (agents follow the summary and skip the body). Body: overview, when to use / not to use, quick reference, common mistakes. Move heavy reference into separate files and link them.

## Rules
Keep it token-efficient (frequently loaded skills under about 200 words of core guidance); one excellent example beats many; no narrative storytelling; flowcharts only for non-obvious decisions; rigid discipline skills need an explicit rationalization table; do not ship an untested skill.
