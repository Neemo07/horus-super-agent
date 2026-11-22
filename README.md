<div align="center">

# Horus Super Agent

**A DAG-wave orchestrator and 31-skill harness for [OpenCode](https://opencode.ai).**

Specs before code, file-locked parallel subagents, and proof-gated task closure —
with every decision surfaced as a native clickable poll instead of a wall of chat questions.

[![Version](https://img.shields.io/badge/version-0.3.7-00d4aa?style=flat-square)](CHANGELOG.md)
[![OpenCode](https://img.shields.io/badge/OpenCode-V1%20%7C%20V2-6e56cf?style=flat-square)](https://opencode.ai)
[![Skills](https://img.shields.io/badge/skills-31-3b82f6?style=flat-square)](SKILLS.md)
[![Subagents](https://img.shields.io/badge/subagents-6-8b5cf6?style=flat-square)](#the-subagents)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=flat-square)](#quick-start)
[![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)](LICENSE)

</div>

---

## Why this exists

Most agent setups fail in three predictable ways: they start writing code before the
requirements exist, they claim work is done without proof, and they burn their context
window re-reading the same files.

Horus is a harness that makes those failures structurally hard:

| Failure mode | How Horus blocks it |
| :--- | :--- |
| **Code before specs** | Kickoff gate + `vibe-grill` interview produces `PRD.md` and a phased plan before any edit |
| **Hand-ticked "done"** | Tasks close only when `plan.py done --run "<cmd>"` exits 0 and writes a record to `evidence/` |
| **Context window drift** | `graphify-out/graph.json` AST graph + `HANDOFF.md` briefs instead of bulk file reads |
| **Parallel agents overwriting each other** | Every wave task declares `Owns Files`; only strictly disjoint sets run concurrently |
| **Silent disagreement** | Subagents can't prompt you — they return `DECISION_OPTIONS` and the orchestrator turns them into one poll |
| **Sycophantic review** | `reviewer` is read-only and returns `PASS`/`FAIL` with `file:line` findings and zero praise |

---

## How it works

```mermaid
flowchart TD
    U([Request]) --> H["horus<br/><i>primary orchestrator</i>"]
    H <-->|"question tool"| P(["Native poll cards"])
    H --> G{Kickoff gate}

    G -->|Production / MVP| V["vibe-grill<br/>PRD.md + AGENTS.md"]
    G -->|Feature on existing repo| B[brainstorming]
    G -->|Small task| W

    V --> S["vibe-spec-plan<br/>IMPLEMENTATION_PLAN.md"]
    B --> S
    S --> W["DAG wave scheduler<br/>plan.py start"]

    W --> A[architect]
    W --> CE[c-engineer]
    W --> WE[web-engineer]
    W --> UI[ui-gui-engineer]
    W --> RE[re-analyst]

    A --> R{{reviewer<br/>read-only}}
    CE --> R
    WE --> R
    UI --> R
    RE --> R

    R -->|"FAIL / max 3 retries"| W
    R -->|PASS| E[("plan.py done --run<br/>evidence/ proof")]
    E --> H
```

### Adaptive pipeline routing

The orchestrator picks the smallest pipeline that can actually satisfy the request:

| Pipeline | Trigger | Sequence |
| :--- | :--- | :--- |
| `TRIVIAL` | ≤ 1 file touched | worker → verify |
| `STANDARD` | Multi-file feature | `architect` → worker wave → `reviewer` |
| `REVERSE-ENGINEERING` | Binary / legacy port | `re-analyst` (REA spec) → `c-engineer` → `reviewer` |
| `WEB` | Web product | `architect` → `web-engineer` wave → Playwright E2E → `reviewer` → `vibe-test-gate` |
| `CORE + UI` | Native app | `architect` freezes contract → parallel `c-engineer` + `ui-gui-engineer` → integration build → `reviewer` |

### Retry escalation

A failing task gets three escalating attempts, then a circuit breaker:

1. Re-dispatch with only `BLOCKERS`/`MAJORS` quoted at `file:line`.
2. Refresh the Graphify slice, attach the exact failing stderr, re-dispatch.
3. `plan.py block <id> "<reason>"` and a `Blocked` poll — *Expand Scope*, *Alternative Approach*, or *Keep Blocked & Handoff*.

---

## Quick start

**Requirements:** OpenCode (V1 or V2), Python 3.8+ for the plan/validation scripts,
and PowerShell 5.1+ or bash.

### Install into a single repo (recommended)

```powershell
# Windows
.\install.ps1 -Mode project -TargetDir "C:\path\to\your\repo"
```

```bash
# Linux / macOS
bash install.sh project /path/to/your/repo
```

### Install globally for every OpenCode project

```powershell
.\install.ps1 -Mode global -ForceConfig
```

```bash
bash install.sh global --force-config
```

### Upgrade an existing install

`-ForceConfig` / `--force-config` overwrites `AGENTS.md` and `opencode.jsonc`,
saving a `.bak` of each first. Without the flag, existing config files are left untouched
and only agents, skills, and commands are refreshed.

```powershell
.\install.ps1 -Mode project -TargetDir "C:\path\to\your\repo" -ForceConfig
```

### Verify the install

```bash
python scripts/validate_horus.py
```

```
HORUS VALIDATION PASSED (project): 7 agents, 31 skills, 6 commands, 4 Vibe templates, 8 bilingual Vibe handbooks, 8 Graphify references.
```

The validator checks config parsing, `question` permissions on the primary agent,
`question`/`subagent` denial on every worker, absence of hardcoded `model:` fields,
skill frontmatter, required commands, merged Vibe assets, and Python syntax.

### Optional companions

```bash
uv tool install --upgrade "graphifyy[mcp]"  # local AST knowledge graph + graphify-mcp server
npx -y rea-agents@latest setup          # REA binary / PE analysis toolkit
pip install playwright && python -m playwright install chromium   # webapp-testing
```

Both MCP servers ship commented out in `opencode.jsonc` — uncomment once installed.

---

## What's inside

```
horus-super-agent/
├─ AGENTS.md                  # harness rules: signal-only output, evidence gates, skill routing
├─ opencode.jsonc             # OpenCode V2 config (permissions array)
├─ opencode.v1.json           # OpenCode V1 config (permission map)
├─ install.ps1 / install.sh   # project-local and global installers
├─ .opencode/
│  ├─ agents/                 # horus + 6 subagents
│  ├─ commands/               # 6 slash commands
│  └─ skills/                 # 31 skills
│     └─ vibe/                # 4 templates + 8 EN/AR handbooks
└─ scripts/
   ├─ validate_horus.py       # integrity validator
   ├─ sync_upstream.py        # replace offline editions with verbatim upstream
   └─ migrate-opencode-db.py  # repair a V2→V1 opencode.db schema mismatch
```

> **Troubleshooting OpenCode itself?** `scripts/migrate-opencode-db.py` (driven by
> `finish-db-migration.ps1`) moves a locked `opencode.db` aside, builds a fresh
> V1-schema database, and restores projects, sessions, messages, and parts from the
> old one. It always backs up first and supports `--dry-run`.

### The subagents

| Agent | Role | Writes? |
| :--- | :--- | :--- |
| `horus` | Primary orchestrator: polls, waves, gates, escalations | Coordinates |
| `architect` | Maps the codebase, freezes contracts, produces the DAG plan | Read-only |
| `c-engineer` | Modern C17/C23 and C++20/Win32 systems work | Yes |
| `ui-gui-engineer` | Win32/Direct2D, ImGui, GTK4, SDL3, Clay, and web UI craft | Yes |
| `web-engineer` | React/Next.js, Supabase/Postgres, performance, browser-verified delivery | Yes |
| `re-analyst` | REA/Ghidra/IDA binary analysis into evidence-backed specs | Read-only |
| `reviewer` | Spec, security, memory-safety, ABI, file-lock, and proof audit | Read-only |

Only `horus` may call the `question` tool. Workers that need a decision return
`STATUS: NEEDS_DECISION` with `DECISION_OPTIONS`, so you always get one clean poll.

### Slash commands

| Command | Purpose |
| :--- | :--- |
| `/horus-init` | Kickoff wizard: mode, lifecycle tier, subagent models, Graphify index, `plan.py init` |
| `/horus-status` | Progress, `plan.py verify` audit, active wave, git tree — zero fluff |
| `/horus-resume` | Cold-start or post-compaction recovery from `HANDOFF.md` and `task_plan.md` |
| `/horus-review` | Adversarial read-only review plus anti-test-theater audit on the current diff |
| `/vibe` | Enter the 7-stage Vibe Engineering workflow |
| `/graphify` | Official Graphify v0.9.115 knowledge graph build, query, path, explain, update, wiki & MCP |

### Evidence gates (`plan.py`)

```bash
python .opencode/skills/planning-with-evidence/scripts/plan.py init
python .opencode/skills/planning-with-evidence/scripts/plan.py status
python .opencode/skills/planning-with-evidence/scripts/plan.py next
python .opencode/skills/planning-with-evidence/scripts/plan.py start  T1.2
python .opencode/skills/planning-with-evidence/scripts/plan.py done   T1.2 --run "pytest -q"
python .opencode/skills/planning-with-evidence/scripts/plan.py block  T1.2 "missing API key"
python .opencode/skills/planning-with-evidence/scripts/plan.py verify --rerun
python .opencode/skills/planning-with-evidence/scripts/plan.py handoff --note "next: wire the parser"
```

Tasks are written as `- [ ] T1.1 Title | accept: <checkable command or file>`.
`verify` flags any `[x]` with no matching evidence record as `UNPROVEN`, which makes
editing a checkbox by hand useless.

---

## The skills

31 skills, grouped by purpose. Full provenance and upstream attribution in [SKILLS.md](SKILLS.md).

<details>
<summary><b>Orchestration & evidence (9 Horus originals)</b></summary>

| Skill | Use it for |
| :--- | :--- |
| `subagent-driven-dev` | DAG waves, file locks, Dispatch/Result envelopes, smart retries |
| `planning-with-evidence` | `plan.py` progress, proof records, `HANDOFF.md` |
| `anti-hallucination-harness` | Evidence-backed claims, minimal output, honest blockers |
| `graphify` | Official Graphify v0.9.115 OpenCode skill + 8 references (AST graph, query/path/explain/section, wiki, MCP) |
| `reverse-engineer-anything` | Binary, bundle, and archive inspection via REA |
| `cpp20-win32-re` | PE32/PE32+ analysis into clean C++20 `_WIN64` |
| `modern-c-mastery` | C11/17/23 UB elimination, arenas, sanitizers |
| `native-gui-architecture` | DPI, 120 fps rendering, threading, dark mode |
| `ui-ux-design-systems` | Spatial grids, OKLCH tokens, WCAG/APCA contrast |

</details>

<details>
<summary><b>Vibe Engineering (6 skills + 4 templates + 8 handbooks)</b></summary>

| Skill | Stage |
| :--- | :--- |
| `vibe` | Master router across all 7 stages |
| `vibe-grill` | Socratic requirements interview → `PRD.md` |
| `vibe-spec-plan` | Edge-case matrix → phased `IMPLEMENTATION_PLAN.md` |
| `vibe-scoped-build` | Single-task diffs, root-cause fixes, clean checkpoints |
| `vibe-critique` | Anti-sycophancy review with confidence scores |
| `vibe-test-gate` | Anti-test-theater audit + 16-point launch gate |

Templates: `PRD`, `IMPLEMENTATION_PLAN`, `AGENTS` (EN and AR).
Handbooks: `workflow-7-stages`, `checklists`, `anti-patterns`, `prompt-blueprints` (EN and AR).

</details>

<details>
<summary><b>Web, data, MCP, design & documents (10 skills)</b></summary>

| Skill | Use it for |
| :--- | :--- |
| `speed-engineer` | Indexes, N+1, pagination, caching, skeleton states |
| `vercel-react-best-practices` | React/Next.js waterfalls and bundle size (70 rules) |
| `supabase-postgres-best-practices` | Schema, RLS, indexing, connection management (31 rules) |
| `frontend-design` | Distinctive web visual direction & typography |
| `webapp-testing` | Playwright verification, screenshots, console logs |
| `mcp-builder` | Building high-quality TypeScript & Python MCP servers |
| `pdf` / `docx` / `xlsx` / `pptx` | Full document, spreadsheet, presentation & PDF engineering |

</details>

<details>
<summary><b>Engineering discipline (6 full Superpowers v7.0.2 skills + references/scripts)</b></summary>

`brainstorming`, `test-driven-development`, `systematic-debugging`,
`using-git-worktrees`, `finishing-a-development-branch`, `writing-skills`

</details>

---

## Configuration

`opencode.jsonc` sets `horus` as the default agent and allows the `question` tool
globally, while still prompting before `git push` and `rm -rf`:

```jsonc
{
  "default_agent": "horus",
  "instructions": ["AGENTS.md"],
  "permissions": [
    { "action": "question", "resource": "*", "effect": "allow" },
    { "action": "shell", "resource": "git push *", "effect": "ask" },
    { "action": "shell", "resource": "rm -rf *", "effect": "ask" }
  ]
}
```

No agent ships a hardcoded `model:`. Models are chosen per session — either inherited
or assigned per subagent through a kickoff poll — so the harness never fights your
provider setup.

### OpenCode V2 vs V1

- **V2** (default): `opencode.jsonc` and `.opencode/agents/*.md` use the `permissions` array.
- **V1**: copy `opencode.v1.json` over `opencode.json` (it already sets `"question": "allow"`).
  Skills and commands are identical in both.

---

## Contributing

- **Adding a skill:** follow `writing-skills`, keep frontmatter `name:` equal to the directory name, then run `python scripts/validate_horus.py`.
- **Replacing offline editions:** `python scripts/sync_upstream.py --dry-run` to preview, `--only <group>` to scope. Backups and commit pins land in `SOURCES.lock.json`.
- **Changing harness rules:** edit `AGENTS.md`, then `CHANGELOG.md`, then validate.

## Credits

Built on [OpenCode](https://opencode.ai) and shaped by
[`dsh-superagent-prototype`](https://github.com/deepseek-ai/dsh-superagent-prototype),
[vibe-engineering-playbook](https://github.com/abduallahJamal/vibe-engineering-playbook),
[superpowers](https://github.com/obra/superpowers),
[graphify](https://github.com/Graphify-Labs/graphify),
[rea](https://github.com/morluto/rea),
[anthropics/skills](https://github.com/anthropics/skills),
[vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills), and
[supabase/agent-skills](https://github.com/supabase/agent-skills).

## License

[MIT](LICENSE)
