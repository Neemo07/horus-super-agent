# OpenCodeReview — Native Cross-Model & GitHub PR Guide

## 1. One-Time Native Provider Setup (Independent Reviewer Model)
```bash
npm install -g @alibaba-group/open-code-review
ocr config provider
ocr config model
ocr llm test
```
Supports Anthropic, OpenAI Chat Completions, OpenAI Responses, AWS Bedrock, DeepSeek, Gemini, and OpenAI-compatible endpoints.

## 2. Common Native Invocations
| Target | Command |
| :--- | :--- |
| Working copy (staged + unstaged + untracked) | `ocr review --audience agent -b "<business context>"` |
| Current branch vs `main` | `ocr review --audience agent -b "<context>" --from main --analysis --format json` |
| Branch range | `ocr review --audience agent -b "<context>" --from <base> --to <head> --format json` |
| Single commit | `ocr review --audience agent -b "<context>" -c <sha>` |
| Preview files only (0 LLM calls) | `ocr review --preview` |
| SARIF output for CI / security tools | `ocr review --audience agent --format sarif --output review.sarif` |
| Local review history viewer | `ocr viewer` |

- Always pass `--audience agent` for clean machine-consumable findings.
- For long context (>1 paragraph), write a Markdown file and pass `--background-file <path>` (up to 8,000 chars; mutually exclusive with `-b`).
- Route large JSON/SARIF output files through `ctx_search` / `ctx_execute`.

## 3. GitHub PR Mode (`scripts/review_pr.py`)
```bash
python3 .opencode/skills/open-code-review/scripts/review_pr.py <pr-number-or-url> [--repo OWNER/REPO] [--background "<context>"]
```
- Requires Python 3 and authenticated `gh` CLI.
- Reads the printed `run.json` and result file; report resolved PR URL, reviewed revisions, freshness, and artifact path.
- **Policy Stops (Never Bypass):** `review_pr.py` intentionally stops if the PR modifies Git filtering metadata or configures untrusted MCP servers, and ignores untrusted review rules inside the PR diff. On failure, report the exact failed step — never silently fall back to a local branch review.
