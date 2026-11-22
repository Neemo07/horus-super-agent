# Skill Provenance (v0.3.7 — 31 focused skills)

"verbatim" = byte-identical to the source. "full merged + Horus polls" = full upstream skill + bundled templates/handbooks upgraded with OpenCode's native `question` tool poll workflow. "offline edition" = re-authored, condensed, works with no network; replace with exact upstream using `python scripts/sync_upstream.py` (needs git + network).

| Skill | Upstream | Bundled as |
|---|---|---|
| vibe, vibe-grill, vibe-spec-plan, vibe-scoped-build, vibe-critique, vibe-test-gate + `/vibe` | abduallahJamal/vibe-engineering-playbook (v1.0.0) | **full merged + Horus polls** — complete upstream skills + all 4 templates (`.opencode/skills/vibe/templates/`) + all 8 EN/AR handbooks (`.opencode/skills/vibe/references/`) |
| speed-engineer | provided zip | verbatim |
| frontend-design, webapp-testing, mcp-builder, pdf, docx, xlsx, pptx | anthropics/skills | **full upstream editions** (all bundled scripts, schemas & references; tightened frontmatter descriptions for lean catalog) |
| vercel-react-best-practices | vercel-labs/agent-skills (`react-best-practices`, v1.0.0) | **verbatim full edition** — 70 rules across 8 categories (`rules/*.md`), compiled `AGENTS.md`, and `metadata.json` |
| supabase-postgres-best-practices | supabase/agent-skills (v1.1.1) | **full upstream edition** — 31 rule references across 8 categories (`references/*.md`), tightened frontmatter description for catalog economy |
| brainstorming, test-driven-development, systematic-debugging, using-git-worktrees, finishing-a-development-branch, writing-skills | obra/superpowers (v7.0.2) | **full upstream v7.0.2 + Horus integration** — complete skills + companion references/scripts (`writing-good-tests.md`, `root-cause-tracing.md`, `defense-in-depth.md`, `find-polluter.sh`, `visual-companion.md`, `writing-skills/references/`, `render-graphs.js`), adapted for Horus native `question` polls, bare OpenCode skill IDs, and signal-only output |
| `graphify` + `/graphify` | Graphify-Labs/graphify (v0.9.115 / `graphifyy`) | **verbatim official OpenCode edition** — `skill-opencode.md` + all 8 `references/` handbooks |
| Horus originals (8) | this project | `subagent-driven-dev` upgraded with native OpenCode `question` polls & `DECISION_OPTIONS` escalation |
