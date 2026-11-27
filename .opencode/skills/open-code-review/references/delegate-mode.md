# OpenCodeReview — LLM-Free Delegation Mode (65+ Language Rule Packs)

Use Delegation Mode when you have **no separate OCR API key** and want Horus's active model (OpenCode, Antigravity, or DeepSeek Harness) to review changes guided by OCR's deterministic file filter and 65+ language-specific rule packs.

## 1. Preview Reviewable Files (Zero LLM Calls)
```bash
ocr delegate preview --format json [--from <ref> [--to <ref>]] [--commit <hash>] [--exclude <patterns>]
```
- Omit range/commit flags for workspace changes; `--from <base>` defaults `--to HEAD` (merge-base to HEAD).
- Returns `mode`, `merge_base`, reviewable file paths, and excluded files with reasons.

## 2. Fetch Language-Specific Review Rules
```bash
ocr delegate rule --format json [--from <ref> [--to <ref>]] [--commit <hash>] <path1> <path2> ...
```
- Pass the exact same range/commit flags as Step 1.
- Output groups files sharing identical rule docs; route large JSON output through `ctx_search` / `ctx_execute`.

## 3. Inspect Plain Diffs & Caller Blast Radius
Use `git --no-pager` with external diff/color disabled:
- **Workspace:** `git --no-pager diff --no-ext-diff --no-textconv --no-color -- "<path>"` (and `--cached` for staged)
- **Range:** `git --no-pager diff --no-ext-diff --no-textconv --no-color <merge_base>..<to> -- "<path>"`
- **Commit:** `git --no-pager show --no-ext-diff --no-textconv --no-color <sha> -- "<path>"`

Pair with `graphify query` on modified public symbols to catch cross-file regressions, then output severity-ranked `file:line` findings (zero sycophancy, fix code only if requested).
