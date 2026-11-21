#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-project}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$MODE" == "global" ]]; then
  TARGET_BASE="$HOME/.config/opencode"
  mkdir -p "$TARGET_BASE/agents" "$TARGET_BASE/skills"
  cp -r "$SCRIPT_DIR/.opencode/agents/"* "$TARGET_BASE/agents/"
  cp -r "$SCRIPT_DIR/.opencode/skills/"* "$TARGET_BASE/skills/"
  cp -n "$SCRIPT_DIR/AGENTS.md" "$TARGET_BASE/AGENTS.md" 2>/dev/null || true
  cp -n "$SCRIPT_DIR/opencode.jsonc" "$TARGET_BASE/opencode.jsonc" 2>/dev/null || true
  echo "Installed globally to $TARGET_BASE"
else
  TARGET_DIR="${2:-$(pwd)}"
  mkdir -p "$TARGET_DIR/.opencode/agents" "$TARGET_DIR/.opencode/skills"
  cp -r "$SCRIPT_DIR/.opencode/agents/"* "$TARGET_DIR/.opencode/agents/"
  cp -r "$SCRIPT_DIR/.opencode/skills/"* "$TARGET_DIR/.opencode/skills/"
  cp -n "$SCRIPT_DIR/AGENTS.md" "$TARGET_DIR/AGENTS.md" 2>/dev/null || true
  cp -n "$SCRIPT_DIR/opencode.jsonc" "$TARGET_DIR/opencode.jsonc" 2>/dev/null || true
  echo "Installed into project: $TARGET_DIR"
fi

if ! command -v graphify >/dev/null 2>&1; then
  echo "Note: Graphify CLI not found. Install it for AST knowledge graphs:"
  echo "  uv tool install --upgrade graphifyy   # or: pip install graphifyy"
fi
if ! command -v rea >/dev/null 2>&1; then
  echo "Note: REA CLI not found. Optional for binary reverse engineering:"
  echo "  npx -y rea-agents@latest setup"
fi
