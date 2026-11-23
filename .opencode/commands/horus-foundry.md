---
description: Launch, inspect, or initialize Horus Foundry — parallel background OpenCode agents orchestrated via Linear (`scripts/horus_foundry.py`).
---

Load and follow the `horus-foundry` skill immediately:

1. Check whether `.horus/foundry.env` or `LINEAR_API_KEY` is configured.
2. If `$ARGUMENTS` is empty, invoke OpenCode's native `question` tool (`header: "Foundry"`, options: `Check Queue (Recommended)`, `Dry-Run Next Wave`, `Init Linear States`, `Launch Pods`) to confirm what the user wants to run.
3. Run the corresponding `python scripts/horus_foundry.py` subcommand (`status`, `init-linear`, or `run --workers <N> --mode <staged|oneshot> --merge <pr|merge|auto>`) and report the terse result.

Arguments:
$ARGUMENTS
