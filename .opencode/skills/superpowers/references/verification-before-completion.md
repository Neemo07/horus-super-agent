# Superpowers: Verification Before Completion

**Iron Law:** No completion claim without fresh verification evidence executed *after* the last edit.

## Mandatory Gate
1. Identify the exact command that proves the claim (test suite, build, typecheck, linter, Playwright script, or `plan.py verify --rerun`).
2. Execute it fresh in the current turn — never rely on an earlier run before a "tiny tweak".
3. Read the complete output and exit code (exit 0 + expected passing counts, zero skipped/ignored failures).
4. Close the task via `plan.py done <id> --run "<cmd>"` so proof is written to `evidence/`.
5. State only what the fresh output directly proved; report any untested surface or limitation explicitly.
