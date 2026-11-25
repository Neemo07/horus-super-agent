---
name: engineering-craft
description: "18-playbook senior engineering suite: deep modules, domain modeling, wayfinder, tickets, PRs, triage, retros, bug diagnosis, pre-commit."
license: MIT
compatibility: opencode, antigravity, dsh
metadata:
  source: mattpocock/skills (curated 18 non-overlapping playbooks, adapted for OpenCode & Horus)
  version: "0.4.6-horus"
---

# Engineering Craft Playbook Suite (Progressive Disclosure Router)

18 curated senior-engineering playbooks (54 files) live under `.opencode/skills/engineering-craft/references/`. **Never load all playbooks at once** — read ONLY the specific playbook(s) matching the task, then execute following Horus `AGENTS.md`.

## Trigger → Playbook Routing Table

### Architecture & Domain Modeling
| Need | Read Playbook (`references/<path>`) |
| :--- | :--- |
| Deep-module architecture vocabulary & boundary design | `codebase-design/SKILL.md` |
| Scan a codebase for deepening opportunities + visual HTML report | `improve-codebase-architecture/SKILL.md` |
| Build/sharpen ubiquitous domain language, invariants & bounded contexts | `domain-modeling/SKILL.md` |
| Enforce TypeScript deep-module boundaries with `dependency-cruiser` | `setup-ts-deep-modules/SKILL.md` |

### Multi-Session Planning, Specs, PRs & Triage
| Need | Read Playbook (`references/<path>`) |
| :--- | :--- |
| Plan a huge multi-session initiative as a shared dependency map | `wayfinder/SKILL.md` |
| Turn a conversation into a structured technical spec | `to-spec/SKILL.md` |
| Break a plan/spec into tracer-bullet vertical-slice tickets | `to-tickets/SKILL.md` |
| Write a clear, high-signal Pull Request body | `pr/SKILL.md` |
| Triage issues & external PRs through a structured state machine | `triage/SKILL.md` |
| Run a session retrospective to harden `AGENTS.md` & workflows | `retro/SKILL.md` |
| Generate an interactive shell wizard for human-only setup steps | `wizard/SKILL.md` |

### Diagnosis, Prototyping, Teaching & Agent Docs
| Need | Read Playbook (`references/<path>`) |
| :--- | :--- |
| Hypothesis-driven diagnosis loop for hard bugs & perf regressions | `diagnosing-bugs/SKILL.md` |
| Build a throwaway technical prototype to settle a design question | `tech-prototype/SKILL.md` |
| Primary-source technical research brief | `research/SKILL.md` |
| Write crisp `AGENTS.md`, skills, and instructions for coding agents | `writing-for-agents/SKILL.md` |
| Set up Husky + lint-staged + typecheck + test pre-commit hooks | `setup-pre-commit/SKILL.md` |
| Teach a new concept interactively grounded in the current workspace | `teach/SKILL.md` |
| Turn an open multi-stakeholder decision into a structured questionnaire | `to-questionnaire/SKILL.md` |

## OpenCode & Horus Integration Rules
- **Interactive Choices:** If invoked via `/craft` without a specific target (and running as primary `horus`), call OpenCode's native **`question` tool** (`header: "Craft"`, concise labels ≤ 30 chars, `custom: true`) to pick the playbook first.
- **No Duplication:** Use Horus's own `vibe-grill` / `brainstorming` for discovery, `reviewer` + `vibe-critique` for code review, `test-driven-development` for TDD, and `plan.py` for executable proof-gated task tracking — `engineering-craft` complements them without replacing them.
- **Graphify & Context Mode First:** Pair `improve-codebase-architecture`, `domain-modeling`, and `diagnosing-bugs` with `graphify query` (AST coupling/god nodes) and `ctx_search` (large logs/traces).
