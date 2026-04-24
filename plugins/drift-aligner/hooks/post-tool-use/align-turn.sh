#!/usr/bin/env bash
# drift-aligner: PostToolUse hook.
# Per-turn alignment: D1 LCS vs anchor + D3 reservoir bookkeeping + D2 HMM state.
# Advisory-only, fail-open. MUST exit 0.

if [[ -n "${CLAUDE_SUBAGENT:-}" ]]; then
  exit 0
fi

trap 'exit 0' ERR INT TERM
set -uo pipefail

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 "${SCRIPT_DIR}/align-turn.py" "$PLUGIN_ROOT" 2>/dev/null || true
exit 0
