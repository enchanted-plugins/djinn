#!/usr/bin/env bash
# Djinn installer. Sub-plugins coordinate through the enchanted-mcp event bus;
# the `full` meta-plugin pulls them all in via one dependency-resolution pass.
# Zero external runtime deps: requires git + python3 (stdlib only).
set -euo pipefail

REPO="https://github.com/enchanted-plugins/djinn"
PLUGIN_HOME_DIR="${PLUGIN_HOME_DIR:-$HOME/.claude/plugins/djinn}"

step() { printf "\n\033[1;36m▸ %s\033[0m\n" "$*"; }
ok()   { printf "  \033[32m✓\033[0m %s\n" "$*"; }
warn() { printf "  \033[33m!\033[0m %s\n" "$*" >&2; }

step "Djinn installer"

if [[ -d "$PLUGIN_HOME_DIR/.git" ]]; then
  git -C "$PLUGIN_HOME_DIR" pull --ff-only --quiet
  ok "Updated existing clone at $PLUGIN_HOME_DIR"
else
  git clone --depth 1 --quiet "$REPO" "$PLUGIN_HOME_DIR"
  ok "Cloned to $PLUGIN_HOME_DIR"
fi

if ! command -v git >/dev/null 2>&1; then
  warn "git not found on PATH — Djinn requires git"
  exit 1
fi
ok "git present"

if ! command -v python3 >/dev/null 2>&1; then
  warn "python3 not found on PATH — Djinn requires Python 3.8+ stdlib"
  exit 1
fi
ok "python3 present"

cat <<'EOF'

─────────────────────────────────────────────────────────────────────────
  Djinn ships as a multi-plugin marketplace. Each sub-plugin owns one
  named engine or one orthogonal concern. The `full` meta-plugin lists
  them all as dependencies so one install pulls in the whole chain.
─────────────────────────────────────────────────────────────────────────

  Finish in Claude Code with TWO commands:

    /plugin marketplace add enchanted-plugins/djinn
    /plugin install full@djinn

  That installs every sub-plugin via dependency resolution. To cherry-pick
  a single sub-plugin instead, use e.g. `/plugin install intent-anchor@djinn`.

  Verify with:   /plugin list
  Expected:      full + all six sub-plugins installed under the djinn marketplace.

EOF
