---
name: verification-before-completion
description: "Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims"
license: MIT
compatibility: opencode
metadata:
  source: obra/superpowers (superpowers plugin of obra/superpowers-marketplace)
  edition: condensed-offline
---
> Provenance: offline condensed edition re-authored from the `superpowers` plugin (MIT). Run `python scripts/sync_upstream.py --only superpowers` for the verbatim upstream skill.

# Verification Before Completion

**Iron law: no completion claims without fresh verification evidence.** Claiming success without running the check is dishonesty, not efficiency.

## Gate (before any "done", "fixed", "passing")
1. Identify the command that proves the claim.
2. Run it fully, now (not a previous run).
3. Read the whole output and exit code.
4. Only then state the result, with the evidence.

| Claim | Required evidence |
|---|---|
| Tests pass | test command output: 0 failures |
| Build succeeds | build command exit 0 |
| Bug fixed | original symptom reproduced before, gone after |
| Requirements met | line-by-line checklist against the spec |
| Subagent finished | inspect the VCS diff yourself |

Red flags: "should work", "probably", "seems to", "I'm confident", satisfaction before verifying, trusting an agent's success report.

## Under Horus
This gate is mechanical: close tasks only with `plan.py done <id> --run "<cmd>"` and run `plan.py verify --rerun` before declaring the project finished.
