# Skill Provenance (v0.3)

"verbatim" = byte-identical to the source. "full merged + Horus polls" = full upstream skill + bundled templates/handbooks upgraded with OpenCode's native `question` tool poll workflow. "offline edition" = re-authored, condensed, works with no network; replace with exact upstream using `python scripts/sync_upstream.py` (needs git + network).

| Skill | Upstream | Bundled as |
|---|---|---|
| vibe, vibe-grill, vibe-spec-plan, vibe-scoped-build, vibe-critique, vibe-test-gate + `/vibe` | abduallahJamal/vibe-engineering-playbook (v1.0.0) | **full merged + Horus polls** — complete upstream skills + all 4 templates (`.opencode/skills/vibe/templates/`) + all 8 EN/AR handbooks (`.opencode/skills/vibe/references/`) |
| speed-engineer | provided zip | verbatim |
| frontend-design | anthropics/skills | verbatim (official copy) |
| webapp-testing | anthropics/skills | offline edition; `with_server.py` and `examples/` independently implemented and tested (Windows + POSIX) |
| vercel-react-best-practices | vercel-labs/agent-skills (`react-best-practices`) | offline edition (8 categories, ~49 rule summaries); full 57-rule guide via sync or the raw AGENTS.md URL in the skill |
| supabase-postgres-best-practices | supabase/agent-skills | offline edition (8 priority categories) |
| using-superpowers, brainstorming, writing-plans, executing-plans, subagent-driven-development, dispatching-parallel-agents, test-driven-development, systematic-debugging, verification-before-completion, requesting-code-review, receiving-code-review, using-git-worktrees, finishing-a-development-branch, writing-skills | obra/superpowers (the `superpowers` plugin of obra/superpowers-marketplace) | offline edition (`brainstorming` upgraded with native OpenCode `question` polls) |
| Horus originals (9) | this project | `subagent-driven-dev` upgraded with native OpenCode `question` polls & `DECISION_OPTIONS` escalation |
