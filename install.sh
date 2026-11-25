#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-project}"
TARGET_DIR=""
FORCE_CONFIG=0
APPLY_DSH_PROFILES=0
HARNESS="opencode"

shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --force-config) FORCE_CONFIG=1 ;;
    --apply-dsh-profiles) APPLY_DSH_PROFILES=1 ;;
    --harness)
      shift
      HARNESS="${1:-opencode}"
      ;;
    --harness=*)
      HARNESS="${1#--harness=}"
      ;;
    *) TARGET_DIR="$1" ;;
  esac
  shift || true
done

case "$HARNESS" in
  opencode|antigravity|dsh|all) ;;
  *)
    echo "Unsupported --harness '$HARNESS' (expected: opencode, antigravity, dsh, all)" >&2
    exit 1
    ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${TARGET_DIR:-$(pwd)}"

copy_jsonc_as_strict_json() {
  local src="$1"
  local dst="$2"
  local ctx_server="${3:-}"
  if command -v python3 >/dev/null 2>&1; then
    python3 - "$src" "$dst" "$ctx_server" << 'PYEOF'
import json, re, sys
from pathlib import Path
text = Path(sys.argv[1]).read_text(encoding="utf-8-sig")
lines = [ln for ln in text.splitlines() if not ln.lstrip().startswith("//")]
cleaned = re.sub(r",(\s*[}\]])", r"\1", "\n".join(lines))
if len(sys.argv) > 3 and sys.argv[3]:
    cleaned = cleaned.replace(".opencode/context-mode/server.js", sys.argv[3])
data = json.loads(cleaned)
Path(sys.argv[2]).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PYEOF
  else
    grep -v '^[[:space:]]*//' "$src" > "$dst"
  fi
}

run_harness_adapter() {
  local adapter="$1"
  local extra=()
  if [[ "$FORCE_CONFIG" -eq 1 ]]; then
    extra+=(--force-config)
  fi
  if [[ "$APPLY_DSH_PROFILES" -eq 1 ]]; then
    extra+=(--apply-dsh-profiles)
  fi
  python3 "$SCRIPT_DIR/scripts/install_harness.py" \
    --harness "$adapter" \
    --mode "$MODE" \
    --target-dir "$TARGET_DIR" \
    "${extra[@]}"
}

if [[ "$HARNESS" == "opencode" || "$HARNESS" == "all" ]]; then
  if [[ "$MODE" == "global" ]]; then
    BASE="$HOME/.config/opencode"
    CFG="$BASE"
  else
    BASE="$TARGET_DIR/.opencode"
    CFG="$TARGET_DIR"
  fi

  mkdir -p "$BASE/agents" "$BASE/skills" "$BASE/commands" "$BASE/context-mode" "$CFG/scripts"
  cp -r "$SCRIPT_DIR/.opencode/agents/." "$BASE/agents/"
  cp -r "$SCRIPT_DIR/.opencode/skills/." "$BASE/skills/"
  cp -r "$SCRIPT_DIR/.opencode/commands/." "$BASE/commands/"
  cp -r "$SCRIPT_DIR/.opencode/context-mode/." "$BASE/context-mode/"

  for f in AGENTS.md opencode.jsonc; do
    dest="$CFG/$f"
    write_strict_json=0

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
          copy_jsonc_as_strict_json "$SCRIPT_DIR/$f" "$dest" "$BASE/context-mode/server.js"
        else
          cp "$SCRIPT_DIR/$f" "$dest"
        fi
        echo "Updated $dest (backup saved to $dest.bak)"
      else
        echo "Kept existing $dest (pass --force-config to upgrade with .bak backup)"
      fi
    else
      if [[ "$write_strict_json" -eq 1 ]]; then
        copy_jsonc_as_strict_json "$SCRIPT_DIR/$f" "$dest" "$BASE/context-mode/server.js"
      else
        cp "$SCRIPT_DIR/$f" "$dest"
      fi
    fi
  done

  for s in sync_upstream.py validate_horus.py migrate-opencode-db.py horus_foundry.py horus_todo.py install_harness.py; do
    cp "$SCRIPT_DIR/scripts/$s" "$CFG/scripts/$s"
  done
  if [[ "$MODE" == "global" ]] && command -v python3 >/dev/null 2>&1; then
    python3 "$CFG/scripts/install_harness.py" --harness opencode-global --mode global --target-dir "$BASE"
  fi
  echo "Installed Horus v0.7.5 ($MODE) to $BASE"

  if command -v python3 >/dev/null 2>&1; then
    python3 "$CFG/scripts/validate_horus.py" || true
  fi
fi

if [[ "$HARNESS" == "antigravity" || "$HARNESS" == "all" ]]; then
  run_harness_adapter "antigravity"
fi

if [[ "$HARNESS" == "dsh" || "$HARNESS" == "all" ]]; then
  run_harness_adapter "dsh"
fi

if ! command -v node >/dev/null 2>&1; then
  echo "Note: Horus Context Mode MCP requires Node.js >= 22.5.0 (built-in node:sqlite)."
else
  NODE_MAJ="$(node -p "process.versions.node.split('.')[0]" 2>/dev/null || echo 0)"
  NODE_MIN="$(node -p "process.versions.node.split('.')[1]" 2>/dev/null || echo 0)"
  if [[ "$NODE_MAJ" -lt 22 || ( "$NODE_MAJ" -eq 22 && "$NODE_MIN" -lt 5 ) ]]; then
    echo "Note: Horus Context Mode MCP requires Node.js >= 22.5.0 (found $(node -v))."
  fi
fi
command -v graphify >/dev/null 2>&1 || {
  echo 'Note: Graphify CLI not found (AST knowledge graphs):  uv tool install --upgrade "graphifyy[mcp]"'; }
command -v rea >/dev/null 2>&1 || {
  echo "Note: REA CLI not found (binary reverse engineering, optional):  npx -y rea-agents@latest setup"; }
python3 -c "import playwright" >/dev/null 2>&1 || {
  echo "Note: 'webapp-testing' needs Playwright:  pip install playwright && python -m playwright install chromium"; }
