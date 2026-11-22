# Superpowers: Brainstorming (Intent Before Code)

Activate BEFORE writing code on any non-trivial feature or new project.

## Protocol
1. **Check context first:** Read `AGENTS.md`, `.horus/STATE.md`, `task_plan.md`, or key repo files so you never ask questions the codebase already answers.
2. **Clarify via OpenCode `question` tool:** Ask 1–4 focused questions (never a wall of 10 text questions). Provide concrete multiple-choice options with your recommended default marked; OpenCode always lets the user type a custom answer.
3. **Present 2–3 architectural options** with explicit trade-offs (complexity, speed, maintainability, YAGNI) and let the user pick via `question`.
4. **Write a concise design spec** (short digestible sections: Goal, Scope/Non-Goals, Architecture/Data Model, Verification Plan) and confirm approval via `question` before entering implementation planning (`plan.py init`).
5. **YAGNI & DRY:** Cut speculative features, unused abstractions, and premature infrastructure.
