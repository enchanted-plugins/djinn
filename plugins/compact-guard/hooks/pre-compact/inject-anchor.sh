#!/usr/bin/env bash
# compact-guard: PreCompact hook.
# Inject the session anchor as a structural hint. This is the ONE reinjection
# point; intent is otherwise held out-of-context in state/anchor.json to avoid
# the recall-valley repetition failure (see docs/science/README.md § D1).
# Advisory, fail-open. MUST exit 0.

if [[ -n "${CLAUDE_SUBAGENT:-}" ]]; then
  exit 0
fi

trap 'exit 0' ERR INT TERM
set -uo pipefail

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 "${SCRIPT_DIR}/inject-anchor.py" "$PLUGIN_ROOT" 2>/dev/null || true
exit 0
