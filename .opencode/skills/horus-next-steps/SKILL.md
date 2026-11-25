---
name: horus-next-steps
description: "Primary-agent-only end-of-turn momentum: 2-4 state-aware continuations (plan.py/git/Graphify) in a native OpenCode question poll."
license: MIT
compatibility: opencode, antigravity, dsh
metadata:
  source: Domush/antigravity-plugin-suggest-next-steps (upgraded & adapted for Horus / OpenCode)
  version: "2.0.0-horus"
---

# Horus Next-Steps Protocol (OpenCode Native Polls)

Eliminates blank-canvas friction at the end of substantive turns by presenting **2–4 concrete, state-aware, 1-click continuations** via OpenCode's native **`question` tool** — without breaking Horus's signal-only output discipline.

## 1. Strict Scope & Subagent Isolation
- **Primary agent (`horus`) ONLY.** Subagents have `question: deny`, never load this skill, and never propose next steps to the user (they return compact Result Envelopes to `horus`).
- **Complete the work first.** Finish all requested edits, verification commands (`plan.py done --run`), and terse result reporting before invoking the next-steps poll. Never offer next steps mid-task or in place of finishing.

## 2. Smart Suppression (When NOT to Fire)
Skip the next-steps poll completely when:
- The user asked a quick factual lookup, simple conversion, or single-line question.
- You already asked a clarifying, plan-approval, or retry-escalation `question` poll in this turn.
- You are blocked by an error (use Horus's `Blocked` escalation poll instead).
- The user explicitly said "done", "stop", or skipped/dismissed the previous next-steps card.

## 3. State-Aware Grounding (Better Than Generic Guesses)
Derive options from **real workspace state** in this priority order:
1. **Plan frontier (`task_plan.md` / `plan.py`):** next ready DAG wave (`plan.py next`), or fixing any `UNPROVEN` / blocked task.
2. **Quality & proof gates:** `/horus-review` (read-only adversarial audit), `vibe-test-gate` (16-point launch gate for `Production / MVP`), or `plan.py verify --rerun`.
3. **Repo & graph hygiene:** `graphify update .` after structural edits, `finishing-a-development-branch` when a feature branch is clean and green, or `plan.py handoff` before ending a long session.
4. **High-leverage follow-ups:** targeted tests, hardening/perf pass (`speed-engineer` / `ctx_stats`), or next vertical slice from `IMPLEMENTATION_PLAN.md`.

## 4. OpenCode `question` Tool Schema (Strict Guardrails)
Put the rationale inside each option's `description` so the chat stays terse (no duplicate wall of bullet prose before the card):
- `header`: **≤ 12 chars** (e.g., `"Next Step"` or `"Next Wave"`).
- `question`: non-empty prompt (e.g., `"Task verified. What would you like to run next?"`).
- `options`: **2–4 atomic, immediately executable choices**, each with:
  - `label`: **≤ 30 chars**, recommended choice **first** with `(Recommended)`.
  - `description`: 1 crisp sentence explaining what will run and why it matters.
- `multiple`: `true` when options compose cleanly (e.g. review + update graph + handoff); `false` for mutually exclusive paths.
- `custom`: leave default (`true`) so OpenCode renders `"Type your own answer"` automatically (never add a dummy `"Other"` option).

### Example OpenCode `question` Payload
```json
{
  "questions": [
    {
      "header": "Next Step",
      "question": "Wave 1 is proven. Which follow-up actions should Horus run?",
      "multiple": true,
      "options": [
        {
          "label": "Start Wave 2 (Recommended)",
          "description": "Dispatch ready tasks T2.1 and T2.2 in parallel with disjoint file locks."
        },
        {
          "label": "Run /horus-review",
          "description": "Adversarial read-only diff audit plus anti-test-theater check before proceeding."
        },
        {
          "label": "Refresh Graphify & Handoff",
          "description": "Run `graphify update .` and generate a fresh HANDOFF.md checkpoint."
        }
      ]
    }
  ]
}
```

## 5. Respectful Skip
If the user dismisses, skips, or declines the poll, conclude the turn immediately with zero reprompting or nagging.
