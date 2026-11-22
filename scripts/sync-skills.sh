#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${1:-$SCRIPT_DIR/../.opencode/skills}"
COMMANDS_DIR="${2:-$SCRIPT_DIR/../.opencode/commands}"

if ! command -v git >/dev/null 2>&1; then
  echo "Error: git is required to sync upstream skills." >&2
  exit 1
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

sync_subdir() {
  local repo="$1" subpath="$2" dest="$3" label="$4"
  echo "Syncing $label from $repo ..."
  local clone_dir="$TMP_DIR/${label//[^a-zA-Z0-9_-]/_}"
  if git clone --depth 1 --filter=blob:none --sparse "$repo" "$clone_dir" >/dev/null 2>&1; then
    local src="$clone_dir"
    if [[ "$subpath" != "." ]]; then
      git -C "$clone_dir" sparse-checkout set "$subpath" >/dev/null 2>&1 || true
      src="$clone_dir/$subpath"
    fi
    if [[ -d "$src" ]]; then
      mkdir -p "$dest"
      cp -r "$src/"* "$dest/" 2>/dev/null || true
      echo "  OK -> $dest"
    else
      echo "  Warning: path '$subpath' not found in $repo; keeping bundled version." >&2
    fi
  else
    echo "  Warning: could not clone $repo; keeping bundled version." >&2
  fi
}

sync_subdir "https://github.com/abduallahJamal/vibe-engineering-playbook.git" ".opencode/skills" "$SKILLS_DIR" "vibe-skills"
sync_subdir "https://github.com/abduallahJamal/vibe-engineering-playbook.git" ".opencode/commands" "$COMMANDS_DIR" "vibe-commands"
sync_subdir "https://github.com/anthropics/skills.git" "skills/frontend-design" "$SKILLS_DIR/frontend-design" "frontend-design"
sync_subdir "https://github.com/anthropics/skills.git" "skills/webapp-testing" "$SKILLS_DIR/webapp-testing" "webapp-testing"
sync_subdir "https://github.com/obra/superpowers.git" "skills" "$SKILLS_DIR/superpowers/upstream-skills" "superpowers-core"
sync_subdir "https://github.com/vercel-labs/agent-skills.git" "skills/react-best-practices" "$SKILLS_DIR/vercel-react-best-practices" "vercel-react-best-practices"
sync_subdir "https://github.com/supabase/agent-skills.git" "skills/supabase-postgres-best-practices" "$SKILLS_DIR/supabase-postgres-best-practices" "supabase-postgres-best-practices"

echo "Upstream skill sync complete."
