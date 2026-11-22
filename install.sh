#!/usr/bin/env bash
set -euo pipefail

MODE="project"
TARGET_DIR=""
FORCE=0
V1=0
SYNC=0

for arg in "$@"; do
  case "$arg" in
    project|global) MODE="$arg" ;;
    --force) FORCE=1 ;;
    --v1) V1=1 ;;
    --sync) SYNC=1 ;;
    *) TARGET_DIR="$arg" ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

copy_cfg() {
  local src="$1" dst="$2"
  if [[ -f "$dst" ]]; then
    if [[ "$FORCE" -eq 1 ]]; then
      cp "$dst" "${dst}.bak"
      cp "$src" "$dst"
      echo "Updated $dst (backup saved to ${dst}.bak)"
    else
      echo "Kept existing $dst (pass --force to upgrade to v0.2.1)"
    fi
  else
    cp "$src" "$dst"
  fi
}

if [[ "$MODE" == "global" ]]; then
  CONFIG_BASE="$HOME/.config/opencode"
  AGENTS_DST="$CONFIG_BASE/agents"
  SKILLS_DST="$CONFIG_BASE/skills"
  COMMANDS_DST="$CONFIG_BASE/commands"
else
  CONFIG_BASE="${TARGET_DIR:-$(pwd)}"
  AGENTS_DST="$CONFIG_BASE/.opencode/agents"
  SKILLS_DST="$CONFIG_BASE/.opencode/skills"
  COMMANDS_DST="$CONFIG_BASE/.opencode/commands"
fi

mkdir -p "$AGENTS_DST" "$SKILLS_DST" "$COMMANDS_DST"
cp -r "$SCRIPT_DIR/.opencode/agents/"* "$AGENTS_DST/"
cp -r "$SCRIPT_DIR/.opencode/skills/"* "$SKILLS_DST/"
if [[ -d "$SCRIPT_DIR/.opencode/commands" ]]; then
  cp -r "$SCRIPT_DIR/.opencode/commands/"* "$COMMANDS_DST/"
fi

copy_cfg "$SCRIPT_DIR/AGENTS.md" "$CONFIG_BASE/AGENTS.md"
if [[ "$V1" -eq 1 ]]; then
  copy_cfg "$SCRIPT_DIR/opencode.v1.json" "$CONFIG_BASE/opencode.json"
else
  copy_cfg "$SCRIPT_DIR/opencode.jsonc" "$CONFIG_BASE/opencode.jsonc"
fi

if [[ "$SYNC" -eq 1 ]]; then
  bash "$SCRIPT_DIR/scripts/sync-skills.sh" "$SKILLS_DST" "$COMMANDS_DST"
fi

echo "Installed Horus Super Agent v0.2.1 ($MODE) -> $CONFIG_BASE"

if ! command -v graphify >/dev/null 2>&1; then
  echo "Note: Graphify CLI not found. Optional AST knowledge graph:"
  echo "  uv tool install --upgrade graphifyy   # or: pip install graphifyy"
fi
if ! command -v rea >/dev/null 2>&1; then
  echo "Note: REA CLI not found. Optional for binary reverse engineering:"
  echo "  npx -y rea-agents@latest setup"
fi
