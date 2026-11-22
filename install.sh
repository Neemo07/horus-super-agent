#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-project}"
TARGET_DIR=""
FORCE_CONFIG=0

shift || true
for arg in "$@"; do
  case "$arg" in
    --force-config) FORCE_CONFIG=1 ;;
    *) TARGET_DIR="$arg" ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$MODE" == "global" ]]; then
  BASE="$HOME/.config/opencode"
  CFG="$BASE"
else
  TARGET_DIR="${TARGET_DIR:-$(pwd)}"
  BASE="$TARGET_DIR/.opencode"
  CFG="$TARGET_DIR"
fi

mkdir -p "$BASE/agents" "$BASE/skills" "$BASE/commands" "$CFG/scripts"
cp -r "$SCRIPT_DIR/.opencode/agents/." "$BASE/agents/"
cp -r "$SCRIPT_DIR/.opencode/skills/." "$BASE/skills/"
cp -r "$SCRIPT_DIR/.opencode/commands/." "$BASE/commands/"

for f in AGENTS.md opencode.jsonc; do
  if [[ -f "$CFG/$f" ]]; then
    if [[ "$FORCE_CONFIG" -eq 1 ]]; then
      cp "$CFG/$f" "$CFG/$f.bak"
      cp "$SCRIPT_DIR/$f" "$CFG/$f"
      echo "Updated $CFG/$f (backup saved to $CFG/$f.bak)"
    else
      echo "Kept existing $CFG/$f (pass --force-config to upgrade with .bak backup)"
    fi
  else
    cp "$SCRIPT_DIR/$f" "$CFG/$f"
  fi
done

cp "$SCRIPT_DIR/scripts/sync_upstream.py" "$CFG/scripts/sync_upstream.py"
cp "$SCRIPT_DIR/scripts/validate_horus.py" "$CFG/scripts/validate_horus.py"
echo "Installed Horus v0.3 ($MODE) to $BASE"

if command -v python3 >/dev/null 2>&1 && [[ "$MODE" == "project" ]]; then
  python3 "$CFG/scripts/validate_horus.py" || true
fi

command -v graphify >/dev/null 2>&1 || {
  echo "Note: Graphify CLI not found (AST knowledge graphs):  uv tool install --upgrade graphifyy"; }
command -v rea >/dev/null 2>&1 || {
  echo "Note: REA CLI not found (binary reverse engineering, optional):  npx -y rea-agents@latest setup"; }
python3 -c "import playwright" >/dev/null 2>&1 || {
  echo "Note: 'webapp-testing' needs Playwright:  pip install playwright && python -m playwright install chromium"; }
echo "Optional: sync other upstream skills:  python3 $CFG/scripts/sync_upstream.py --dest $BASE/skills"
