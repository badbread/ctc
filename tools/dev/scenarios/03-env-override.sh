#!/usr/bin/env bash
# CTC_BASE env var overrides the persisted BASE for this run, but does NOT
# rewrite the config file (env is transient).
set -euo pipefail

rm -rf ~/.config/ctc ~/projects ~/elsewhere
mkdir -p ~/projects/foo/.git ~/elsewhere/bar/.git
mkdir -p ~/.config/ctc
printf 'BASE=/home/tester/projects\n' > ~/.config/ctc/config

CTC_BASE=/home/tester/elsewhere bash -c 'echo q | ctc >/dev/null 2>&1' || true

# Config file should NOT have been clobbered
grep -q '^BASE=/home/tester/projects$' ~/.config/ctc/config \
  || { echo "FAIL: env override rewrote the config file"; cat ~/.config/ctc/config; exit 1; }

echo "PASS"
