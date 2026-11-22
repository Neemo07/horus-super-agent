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

copy_jsonc_as_strict_json() {
  local src="$1"
  local dst="$2"
  if command -v python3 >/dev/null 2>&1; then
    python3 - "$src" "$dst" << 'PYEOF'
import json, re, sys
from pathlib import Path
text = Path(sys.argv[1]).read_text(encoding="utf-8-sig")
lines = [ln for ln in text.splitlines() if not ln.lstrip().startswith("//")]
cleaned = re.sub(r",(\s*[}\]])", r"\1", "\n".join(lines))
data = json.loads(cleaned)
Path(sys.argv[2]).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PYEOF
  else
    grep -v '^[[:space:]]*//' "$src" > "$dst"
  fi
}

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
  dest="$CFG/$f"
  write_strict_json=0

  # Global installs usually already have an opencode.json holding providers/MCP.
  # Dropping a competing opencode.jsonc beside it risks shadowing that config,
  # so never introduce a second config file in global mode; when creating a fresh
  # global opencode.json, strip JSONC comments so strict JSON parsers succeed.
  if [[ "$f" == "opencode.jsonc" && "$MODE" == "global" ]]; then
    if [[ -f "$CFG/opencode.json" ]]; then
      echo "Skipped $dest (opencode.json already exists; add permissions manually)"
      continue
    fi
    dest="$CFG/opencode.json"
    write_strict_json=1
  fi

  if [[ -f "$dest" ]]; then
    if [[ "$FORCE_CONFIG" -eq 1 ]]; then
      cp "$dest" "$dest.bak"
      if [[ "$write_strict_json" -eq 1 ]]; then
        copy_jsonc_as_strict_json "$SCRIPT_DIR/$f" "$dest"
      else
        cp "$SCRIPT_DIR/$f" "$dest"
      fi
      echo "Updated $dest (backup saved to $dest.bak)"
    else
      echo "Kept existing $dest (pass --force-config to upgrade with .bak backup)"
    fi
  else
    if [[ "$write_strict_json" -eq 1 ]]; then
      copy_jsonc_as_strict_json "$SCRIPT_DIR/$f" "$dest"
    else
      cp "$SCRIPT_DIR/$f" "$dest"
    fi
  fi
done

for s in sync_upstream.py validate_horus.py migrate-opencode-db.py; do
  cp "$SCRIPT_DIR/scripts/$s" "$CFG/scripts/$s"
done
echo "Installed Horus v0.3.7 ($MODE) to $BASE"

if command -v python3 >/dev/null 2>&1; then
  python3 "$CFG/scripts/validate_horus.py" || true
fi

command -v graphify >/dev/null 2>&1 || {
  echo "Note: Graphify CLI not found (AST knowledge graphs):  uv tool install --upgrade "graphifyy[mcp]""; }
command -v rea >/dev/null 2>&1 || {
  echo "Note: REA CLI not found (binary reverse engineering, optional):  npx -y rea-agents@latest setup"; }
python3 -c "import playwright" >/dev/null 2>&1 || {
  echo "Note: 'webapp-testing' needs Playwright:  pip install playwright && python -m playwright install chromium"; }
echo "Optional: sync other upstream skills:  python3 $CFG/scripts/sync_upstream.py --dest $BASE/skills"
