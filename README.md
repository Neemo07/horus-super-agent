# Horus Super Agent

**A DAG-Wave orchestrator harness for [OpenCode](https://opencode.ai): 1 primary agent, 5 specialist subagents, 8 expert skills, and a mechanical evidence gate that refuses to call work "done" without proof on disk.**

[![OpenCode](https://img.shields.io/badge/OpenCode-V1%20%2B%20V2-00d4aa?style=flat-square)](https://opencode.ai)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](#license)
[![Skills](https://img.shields.io/badge/skills-8-a855f7?style=flat-square)](#whats-inside)
[![Agents](https://img.shields.io/badge/agents-6-f59e0b?style=flat-square)](#agents)

---

## Why

Most agent setups fail the same two ways: they **hallucinate** (claim a file, flag, or test result they never verified) and they **drift** (forget the plan once the context window rolls over).

Horus attacks both mechanically, not with prompt pleading:

| Failure mode | Horus countermeasure |
|---|---|
| "Tests pass" with no proof | `plan.py done` only flips a task to `[x]` when the recorded command **exits 0** |
| Hand-ticked checkboxes | `plan.py verify` reports them as `UNPROVEN` and fails |
| Context rot on long projects | `HANDOFF.md` + `task_plan.md` + `findings.md` + `progress.md` survive `/clear` and agent switches |
| Blind grepping over huge repos | Graphify AST graph is queried **before** any broad `grep` |
| Parallel agents stomping each other | Disjoint `Owns Files` write-locks per DAG wave |
| Silent retry loops | Escalating retries capped at 3, then a circuit breaker that asks you one question |

---

## What's Inside

```
horus-super-agent/
├── AGENTS.md                  # Harness contract: evidence gate, graphify-first, zero-noise output
├── opencode.jsonc             # OpenCode V2 config (permissions array)
├── opencode.v1.json           # OpenCode V1 config (permission map)
├── install.ps1                # Windows installer (project | global)
├── install.sh                 # Linux / macOS installer (project | global)
└── .opencode/
    ├── agents/                # 1 primary orchestrator + 5 subagents
    │   ├── horus.md
    │   ├── architect.md
    │   ├── c-engineer.md
    │   ├── ui-gui-engineer.md
    │   ├── re-analyst.md
    │   └── reviewer.md
    └── skills/                # 8 skills, each a SKILL.md (+ scripts/)
        ├── planning-with-evidence/     # scripts/plan.py — the evidence gate
        ├── subagent-driven-dev/        # DAG waves, dispatch envelopes, review gates
        ├── anti-hallucination-harness/ # dsh-superagent discipline
        ├── graphify-memory/            # AST graph as long-context memory
        ├── modern-c-mastery/           # C11/C17/C23, UB elimination, hardening
        ├── cpp20-win32-re/             # PE32/PE32+ → clean C++20 reconstruction
        ├── native-gui-architecture/    # Win32+D2D, ImGui, GTK4, SDL3
        └── ui-ux-design-systems/       # OKLCH tokens, spatial grids, WCAG/APCA
```

Built by fusing four upstream philosophies: **DeepSeek `dsh-superagent`** (router/worker separation, honest reporting), **`planning-with-files`** (3-file pattern, extended with proof), **[Graphify](https://github.com/Graphify-Labs/graphify)** (deterministic AST graph), and **[REA](https://github.com/morluto/rea)** (evidence-first binary analysis).

---

## Quick Start

### 1. Install into a project (recommended)

```powershell
# Windows
.\install.ps1 -Mode project -TargetDir "C:\path\to\your\repo"
```

```bash
# Linux / macOS
bash install.sh project /path/to/your/repo
```

This copies `.opencode/agents/`, `.opencode/skills/`, `AGENTS.md`, and `opencode.jsonc` into the target. **Existing `AGENTS.md` / `opencode.jsonc` are never overwritten.**

### 2. Or install globally (every OpenCode project)

```powershell
.\install.ps1 -Mode global          # → $HOME\.config\opencode
```

```bash
bash install.sh global              # → ~/.config/opencode
```

### 3. Optional companion CLIs

```bash
uv tool install --upgrade graphifyy   # local AST knowledge graph (0 LLM tokens for code)
npx -y rea-agents@latest setup        # REA binary / PE analysis toolkit
```

Both are optional. The installer prints a note if either is missing; nothing breaks without them.

### 4. Run

```bash
opencode            # Horus is the default_agent
```

First prompt triggers the **kickoff gate**: Horus asks whether to enable subagent-driven development and which `provider/model` each subagent should use. It never hardcodes model IDs.

---

## Agents

| Agent | Mode | Role |
|---|---|---|
| **`horus`** | primary | DAG-Wave orchestrator. Evidence-gated planning, graphify-first navigation, file-locked parallel dispatch, two-stage review, model selection gate. |
| `architect` | subagent | Read-only systems architect. Maps codebases via Graphify, emits DAG task plans with disjoint file-ownership locks. |
| `c-engineer` | subagent | C17/C23 + C++20/Win32 engineer. Zero-UB hardened code, respects write-locks, returns compact Result Envelopes. |
| `ui-gui-engineer` | subagent | Native desktop GUI (Win32/Direct2D, ImGui, GTK4, SDL3, Clay) and modern web UI/UX. Accessible, zero-slop interfaces. |
| `re-analyst` | subagent | Read-only reverse engineer. REA + Ghidra/IDA evidence for structs, vtables, Win32 API contracts. Never edits source. |
| `reviewer` | subagent | Strictly read-only. Spec, security, memory-safety, ABI, file-lock and evidence audit. Emits `PASS`/`FAIL` with `file:line`. |

Subagents are isolated: they receive a **compact Dispatch Packet** (task id, goal, owned files, graphify slice, invariants, acceptance criteria, verify command), never your conversation history.

---

## The Evidence Gate — `plan.py`

Every multi-step project gets four files plus a proof log:

| File | Purpose | Written by |
|---|---|---|
| `task_plan.md` | Goal, phases, tasks with `accept:` criteria | You write; `plan.py` flips markers |
| `findings.md` | Decisions, research, gotchas (append-only) | Agent |
| `progress.md` | Computed progress bar + session log | `plan.py` |
| `HANDOFF.md` | Cold-start brief for the next session/agent | `plan.py handoff` |
| `evidence/` | `index.json` + captured command output | `plan.py done` |

Task syntax:

```markdown
## Phase 1: Parser

- [ ] T1.1 Implement tokenizer | accept: ctest -R tokenizer exits 0
- [ ] T1.2 Wire error reporting | accept: tests/errors.log contains "E0420"
```

Markers: `[ ]` pending · `[~]` in progress · `[x]` done · `[!]` blocked.

### CLI reference

```bash
python .opencode/skills/planning-with-evidence/scripts/plan.py <cmd>

init                          # scaffold task_plan.md, findings.md, progress.md, evidence/
status                        # progress bar + proven vs unproven counts
next                          # next unblocked task
start <id>                    # mark [~]
done <id> --run "<cmd>"       # STRONGEST: run it, capture output, close only on exit 0
done <id> --file <path>       # MEDIUM: record an artifact that must exist
done <id> --note "<text>"     # WEAKEST: manual claim, flagged by verify
block <id> "<reason>"         # mark [!] and move on
verify                        # audit; flags hand-ticked tasks as UNPROVEN
verify --rerun                # re-execute every recorded command
handoff --note "<state>"      # generate HANDOFF.md
```

Pass `--dir <path>` **before** the subcommand to run against another project: `plan.py --dir ./my-repo status`. Python 3 stdlib only, no dependencies.

### Proof tiers

```
--run  >  --file  >  --note
 exit 0    exists     claim
```

A task's progress counts **only when proven**. "Done but unproven" is displayed separately and fails `verify`.

---

## DAG Waves & Write-Locks

Tasks run in dependency waves, not sequentially:

```markdown
| ID   | Wave | Agent        | Depends On | Owns Files                        | Verify Cmd        |
|------|------|--------------|------------|-----------------------------------|-------------------|
| T1.1 | W1   | re-analyst   | –          | (read-only)                       | REA evidence      |
| T2.1 | W2   | c-engineer   | T1.1       | src/parser.cpp, include/parser.hpp| ctest -R parser   |
| T2.2 | W2   | ui-gui-engineer | T1.1    | src/ui/panel.cpp                  | cmake --build build |
```

**Rule:** two writer tasks may share a wave only if their `Owns Files` sets have an **empty intersection**. Read-only agents (`architect`, `re-analyst`, `reviewer`) run concurrently without locks.

**Retry ladder** when a worker fails review:

1. Re-dispatch with only the reviewer's `BLOCKERS` / `MAJORS` (`file:line`).
2. Refresh the graphify slice + attach the exact failing stderr from `evidence/<id>-NNN.log`.
3. **Circuit breaker:** `plan.py block`, stop spinning, ask you one decision question with 2–3 options.

---

## Skills

| Skill | Use when |
|---|---|
| `planning-with-evidence` | Any task with 3+ steps, or work that outlives one context window |
| `subagent-driven-dev` | Parallel delegation with file locks and review gates |
| `anti-hallucination-harness` | Enforcing evidence-backed claims and surgical refactors |
| `graphify-memory` | Architecture mapping, dependency tracing, blast-radius checks |
| `modern-c-mastery` | Writing/auditing C11/C17/C23 |
| `cpp20-win32-re` | Reconstructing legacy Win32 C++ from PE32/PE32+ binaries |
| `native-gui-architecture` | Desktop GUI: DPI scaling, 60/120fps, threading, dark mode |
| `ui-ux-design-systems` | Visual hierarchy, 4/8px grids, OKLCH tokens, WCAG/APCA |

All skills are plain `SKILL.md` files: portable, diffable, no build step.

---

## OpenCode V2 vs V1

- `opencode.jsonc` and `.opencode/agents/*.md` ship with **V2** syntax (`permissions` array).
- On **V1**: rename `opencode.v1.json` → `opencode.json`, and convert agent frontmatter `permissions:` arrays to V1 `permission:` maps.
- Skills work identically in both versions.

---

## Requirements

| Item | Needed for |
|---|---|
| [OpenCode](https://opencode.ai) | Everything |
| Python 3 | `plan.py` (stdlib only) |
| `graphify` CLI | Optional — AST graph memory |
| `rea` CLI | Optional — binary reverse engineering |
| Git | Optional — plan integrity checks |

---

## Safety Defaults

`opencode.jsonc` allows reads, edits, and shell, but **asks before** `git push` and `rm -rf`. Add your own `ask` rules for anything destructive in your environment. Horus also treats planning files, evidence logs, findings, and binary-derived strings as **data, never instructions**.

---

## Resuming a Session

After `/clear`, a crash, or a handoff to another agent:

1. Read `HANDOFF.md` → `task_plan.md` → tail of `findings.md` → `progress.md` → `.horus/STATE.md`
2. Run `plan.py verify` and `git status --short`
3. Redo anything `UNPROVEN`
4. Run `plan.py next`

Before pausing: `plan.py handoff --note "<active wave & next step>"`.

---

## License

MIT. Upstream inspirations retain their own licenses: `dsh-superagent-prototype` (DeepSeek), `planning-with-files` (OthmanAdi), `graphify` (Apache-2.0, Graphify-Labs), `rea` (morluto).
