#!/usr/bin/env bash
# Runs all Djinn unit tests. Stdlib-only; no external deps.
# Exit 0 on all-pass, non-zero on any failure.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "▸ Djinn tests — $(python3 --version)"
python3 -m unittest discover tests -v
