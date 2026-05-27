#!/usr/bin/env bash
# ~/projects exists: resolve_base should pick it silently and persist.
# No interactive prompt fires (autodetect branch in resolve_base).
set -euo pipefail

rm -rf ~/.config/ctc
mkdir -p ~/projects/foo/.git ~/projects/bar/.git

echo q | ctc >/dev/null 2>&1 || true

grep -q '^BASE=/home/tester/projects$' ~/.config/ctc/config \
  || { echo "FAIL: BASE not autodetected"; cat ~/.config/ctc/config 2>&1; exit 1; }

echo "PASS"
