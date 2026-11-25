# Horus Super Agent

A single-source agent harness that installs a 41-skill orchestrator into OpenCode, Google Antigravity, or DeepSeek Harness Desktop App.

Horus adds evidence-gated planning, file-locked parallel subagents, and read-only review on top of an existing coding agent. It ships as Markdown rules, skills, agents, commands, and small standard-library scripts — no build step and no runtime dependencies for the core harness.

[![CI](https://github.com/Neemo07/horus-super-agent/actions/workflows/ci.yml/badge.svg)](.github/workflows/ci.yml)
[![Version](https://img.shields.io/badge/version-0.7.1-00d4aa)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-22c55e)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-41-3b82f6)](SKILLS.md)
[![Harnesses](https://img.shields.io/badge/harnesses-OpenCode%20%7C%20Antigravity%20%7C%20DSH-6e56cf)](#getting-started)

## Contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Getting started](#getting-started)
- [Usage](#usage)
- [Project structure](#project-structure)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Features

- **One source tree, three harnesses.** `.opencode/` is canonical; adapters generate Antigravity workflows/rules and DSH command playbooks plus a Cordis MCP patch.
- **41 progressive-disclosure skills** covering orchestration, planning, code/DAG design, web, documents, security, reverse engineering, and four distinct memory/context layers. Provenance is in [SKILLS.md](SKILLS.md).
- **7 agents, primary `horus` + 6 subagents.** Only `horus` may call the `question` tool; subagents deny `question` and `subagent` in frontmatter.
- **14 slash commands**, including `/vibe`, `/graphify`, `/horus-context`, `/horus-memory`, `/horus-foundry`, `/horus-todo`, `/design`, `/craft`, `/partner`, and `/security`.
- **Evidence-gated execution** through `plan.py`: a task closes only when `plan.py done <id> --run "<cmd>"` produces a passing evidence record.
- **Horus Context Mode MCP server**: SQLite FTS5 (BM25 + Trigram RRF) search and a sandboxed `ctx_execute` for large logs and bulk data.
- **Multi-runner Foundry**: parallel background workers driven by Linear, with one git worktree per ticket, via `--runner opencode|antigravity|dsh`.
- **`.todo.md` workflow**: git-tracked checklist, AI requirement analysis, and promotion into `task_plan.md`.
- **Integrity validator** for all three harness layouts, including a 150-character skill-description cap and zero duplicate reference-playbook names.

<!-- TODO: add screenshot -->

## Tech stack

| Component | Implementation |
| :--- | :--- |
| Harness definitions | Markdown + YAML frontmatter under `.opencode/` |
| Helper scripts | Python 3.8+, standard library only |
| Installers | PowerShell (`install.ps1`) and Bash (`install.sh`) |
| Context Mode MCP server | Node.js >= 22.5.0 (built-in `node:sqlite`), under `.opencode/context-mode/` |
| Tests | Python `unittest` in `tests/test_horus.py` |

There is no `package.json`, `pyproject.toml`, `requirements.txt`, Makefile, or Dockerfile. No dependency install is required for the core harness.

## Getting started

### Prerequisites

- Python 3.8+ on `PATH` (used by the adapter installer, validator, and helper scripts)
- One of: OpenCode V1/V2, Google Antigravity, or DeepSeek Harness Desktop App
- Node.js >= 22.5.0 **only** for the Horus Context Mode MCP server
- PowerShell 5.1+ (Windows) or Bash (Linux/macOS) to run the installer
- `git` only if you plan to run `sync_upstream.py`

### Install

Project-local, for the current repository:

```powershell
.\install.ps1 -Mode project -TargetDir "C:\path\to\your\repo"
```

```bash
bash install.sh project /path/to/your/repo
```

Global, for every project in the harness:

```powershell
.\install.ps1 -Mode global -ForceConfig
```

```bash
bash install.sh global --force-config
```

The `-Harness` / `--harness` flag selects the target (`opencode`, `antigravity`, `dsh`, or `all`; default `opencode`):

```powershell
.\install.ps1 -Mode project -TargetDir "C:\path\to\your\repo" -Harness all
```

```bash
bash install.sh project /path/to/your/repo --harness all
```

`-ForceConfig` / `--force-config` overwrites `AGENTS.md` and the harness config after saving a `.bak`. Without it, existing config files are kept and agents, skills, and commands are refreshed. In global OpenCode mode, an existing `opencode.json` is never replaced by a competing `opencode.jsonc`.

Verify the result:

```bash
python scripts/validate_horus.py
```

```
HORUS VALIDATION PASSED (project): 7 agents, 41 skills, 14 commands, 4 Vibe templates, 8 bilingual Vibe handbooks, 8 Graphify references.
```

### Configuration

OpenCode settings live in `opencode.jsonc` (V2), `opencode.v1.json` (V1), or global `opencode.json`. The V2 config sets `horus` as `default_agent`, allows the `question` tool, and still asks before `git push *` and `rm -rf *`. No agent ships a hardcoded `model:`; models are selected per session.

Optional environment variables:

| Name | Description | Required | Default |
| :--- | :--- | :--- | :--- |
| `DSH_HOME` | DSH global install root | No | `~/.dsh` |
| `LINEAR_API_KEY` | Linear API key for Foundry | For Foundry | none |
| `LINEAR_API_URL` | Linear GraphQL endpoint | No | `https://api.linear.app/graphql` |
| `LINEAR_TEAM_KEY` | Linear team key | For Foundry | auto-detect |
| `HORUS_FOUNDRY_RUNNER` | Worker CLI (`opencode`, `antigravity`, `dsh`) | No | `opencode` |
| `HORUS_FOUNDRY_AGENT` | Agent name passed to the runner | No | `horus` |
| `HORUS_FOUNDRY_MODEL` | Provider/model override | No | none |
| `HORUS_FOUNDRY_MODE` | `staged` or `oneshot` | No | `staged` |
| `HORUS_FOUNDRY_WORKERS` | Parallel worktree workers | No | `1` |
| `HORUS_FOUNDRY_MERGE` | `pr`, `merge`, or `auto` | No | `pr` |
| `OPENCODE_BIN` | Override `opencode` CLI path | No | PATH lookup |
| `ANTIGRAVITY_BIN` | Override `agy` CLI path | No | PATH lookup |
| `DSH_BIN` | Override `dsh` CLI path | No | PATH lookup |

Optional external tools, wired through commented-out MCP entries or separate setup:

```bash
uv tool install --upgrade "graphifyy[mcp]"
npx -y rea-agents@latest setup
pip install playwright && python -m playwright install chromium
```

For cross-session memory, install `ai-memory` and wire it to the target harness as documented in [horus-memory/SKILL.md](.opencode/skills/horus-memory/SKILL.md).

## Usage

### Evidence-gated tasks

```bash
PLAN=.opencode/skills/planning-with-evidence/scripts/plan.py
python "$PLAN" init
python "$PLAN" start T1.1
python "$PLAN" done T1.1 --run "python -m unittest tests.test_horus"
python "$PLAN" verify --rerun
```

Task lines use `- [ ] T1.1 Title | accept: <checkable command or file>`. `verify` marks hand-edited `[x]` entries as `UNPROVEN`; `status`, `next`, `block`, and `handoff` are also available.

### Todo workflow

```bash
python scripts/horus_todo.py list
python scripts/horus_todo.py add "Fix the parser"
python scripts/horus_todo.py promote
```

### Foundry dry run

```bash
python scripts/horus_foundry.py status --team YOUR_TEAM
python scripts/horus_foundry.py run --runner opencode --once --dry-run
```

`--dry-run` plans claims without mutating Linear or running a worker.

### Validate another harness layout

```bash
python scripts/validate_horus.py --harness antigravity --root /path/to/project
python scripts/validate_horus.py --harness dsh --root /path/to/project
```

### Repair an OpenCode database schema mismatch

```bash
python scripts/migrate-opencode-db.py --db "$HOME/.local/share/opencode/opencode.db" --dry-run
```

The tool backs up the database with SQLite's online backup API before changing anything. `--dry-run` only checks locks and reports counts.

## Project structure

```
horus-super-agent/
├─ AGENTS.md                 # always-on harness rules and skill routing
├─ opencode.jsonc            # OpenCode V2 config (permissions array)
├─ opencode.v1.json          # OpenCode V1 config (permission map)
├─ install.ps1 / install.sh  # multi-harness project/global installers
├─ .opencode/
│  ├─ agents/                # horus + 6 subagents
│  ├─ commands/              # 14 slash commands
│  ├─ context-mode/          # Node.js FTS5 MCP server and dashboard
│  └─ skills/                # 41 skills, nested reference playbooks
├─ adapters/
│  ├─ antigravity/           # MCP config template
│  └─ dsh/                   # Cordis MCP patch template
├─ scripts/
│  ├─ validate_horus.py      # multi-harness integrity validator
│  ├─ install_harness.py     # Antigravity/DSH adapter installer
│  ├─ sync_upstream.py       # replace offline skills with upstream editions
│  ├─ migrate-opencode-db.py # restore projects/sessions after a schema change
│  ├─ horus_foundry.py       # Linear-driven parallel workers
│  └─ horus_todo.py          # git-tracked .todo.md manager
└─ tests/test_horus.py       # unittest suite for all of the above
```

## Development

```bash
python -m unittest tests.test_horus
python scripts/validate_horus.py
python -m ruff check scripts tests
python scripts/sync_upstream.py --dry-run
```

`--harness` defaults to `auto`, which validates only the layouts present under `--root`. Use `opencode`, `antigravity`, `dsh`, or `all` only after installing those targets.

Observed on this checkout: 32 tests run, OK (4 skipped); Ruff reports no errors with the rules in [ruff.toml](ruff.toml). There is no build step. CI runs tests on Python 3.10–3.12 on Linux and Windows, and Ruff separately; see [ci.yml](.github/workflows/ci.yml).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for skill, agent, and adapter conventions.

## License

[MIT](LICENSE) — Copyright (c) 2026 Neemo07.

## Acknowledgments

Skill definitions adapt or bundle upstream work from OpenCode, DeepSeek, the Vibe Engineering Playbook, Superpowers, Anthropic, Vercel, Supabase, Graphify, ai-memory, and others. See [SKILLS.md](SKILLS.md) for the full provenance table.
