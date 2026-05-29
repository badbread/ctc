#!/usr/bin/env bash
# Smoke test: ctc starts, sees claude + tmux, exits cleanly when given 'q'.
# Catches catastrophic regressions (syntax errors, missing deps, etc.) fast.
set -euo pipefail

# Pipe `q` so the menu fallback (non-TTY path) takes 'quit' and exits 0.
output=$(echo q | ctc 2>&1) || { echo "FAIL: ctc errored"; echo "$output"; exit 1; }

echo "$output" | grep -qi "claude terminal connect" \
  || { echo "FAIL: banner not rendered"; echo "$output"; exit 1; }

echo "PASS"
