#!/usr/bin/env bash
# drift-learning: PreCompact hook.
# Folds the just-completed session's summary statistics into the per-(intent-type, developer)
# drift-signature posterior. D5 Gauss Accumulation.
# Advisory, fail-open. MUST exit 0.

if [[ -n "${CLAUDE_SUBAGENT:-}" ]]; then
  exit 0
fi

trap 'exit 0' ERR INT TERM
set -uo pipefail

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 "${SCRIPT_DIR}/update-posterior.py" "$PLUGIN_ROOT" 2>/dev/null || true
exit 0
