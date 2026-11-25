# Contributing to Horus Super Agent

## Before you start

Read [AGENTS.md](AGENTS.md) for the harness rules and [SKILLS.md](SKILLS.md) for upstream provenance. The canonical source is `.opencode/`; the `adapters/` and `scripts/install_harness.py` code generate target-specific layouts from it. Do not edit generated output in `.agents/` or `.dsh/`.

## Development setup

No dependency installation is required for the core harness. Python 3.8+ and the standard library are sufficient.

```bash
python -m unittest tests.test_horus
python scripts/validate_horus.py
```

Both must pass before opening a pull request. Add a regression test in [tests/test_horus.py](tests/test_horus.py) for any behavior change.

## Adding or editing a skill

1. Create `.opencode/skills/<name>/SKILL.md` with YAML frontmatter.
2. Set `name:` exactly equal to the directory name.
3. Keep `description:` at or below 150 characters. The validator enforces this cap and rejects duplicate reference-playbook names.
4. Keep nested reference playbooks uniquely named — two `SKILL.md` files in different trees must not share the same parent directory name.
5. Run the validator after the edit.

See [writing-skills](.opencode/skills/writing-skills/SKILL.md) for the full skill authoring process.

## Adding an agent or command

- Agents live in `.opencode/agents/`. Only `horus.md` may allow the `question` tool; every other agent must explicitly deny `question` and `subagent`. Read-only agents must also declare a `shell: "*"` deny baseline.
- Do not add a hardcoded `model:` field. Models are selected per session.
- Commands live in `.opencode/commands/`. Add the filename to `REQUIRED_COMMANDS` in `scripts/validate_horus.py` when a command becomes part of the contract.

## Harness adapters

When changing text or paths that installers copy:

1. Update the canonical file under `.opencode/`.
2. Check `scripts/install_harness.py` path rewriting so Antigravity and DSH installs contain no dangling `.opencode/` references.
3. Run `python scripts/validate_horus.py --harness all` inside a sandbox project after `-Harness all` installation.

## Changelog and commits

Add a section to [CHANGELOG.md](CHANGELOG.md) describing behavior changes. Keep commits focused; include the validator and test results in the pull request description.
