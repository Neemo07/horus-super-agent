---
description: Open the 18-playbook Engineering Craft suite (deep-module architecture, domain modeling, wayfinder, tracer-bullet tickets, PR body, triage, bug diagnosis, retros, pre-commit, agent-doc authoring).
---

Load and follow the `engineering-craft` skill immediately:

1. If `$ARGUMENTS` names a concrete engineering task (e.g. `improve-codebase-architecture`, `domain-modeling`, `pr`, `retro`, `wayfinder`, `diagnosing-bugs`), read ONLY the matching playbook(s) under `.opencode/skills/engineering-craft/references/` and execute cleanly.
2. If `$ARGUMENTS` is empty or broad, invoke OpenCode's native `question` tool (`header: "Craft"`, options: `Deepen Architecture (Recommended)`, `Domain Model / Wayfinder`, `PR Body / Triage / Retro`, `Diagnose Hard Bug`, `Write Agent Docs / Pre-Commit`) before reading any playbooks.

Arguments:
$ARGUMENTS
