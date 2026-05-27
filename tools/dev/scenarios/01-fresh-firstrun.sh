#!/usr/bin/env bash
# Fresh home, no project dirs present.
# resolve_base() should hit the interactive first-run prompt and persist the
# user's chosen path into ~/.config/ctc/config. The prompt only fires under
# have_tty (`[ -t 0 ] && [ -t 1 ]`), so we wrap ctc in `script -qec` to give
# it a real pty.
set -euo pipefail

# Sanity: nothing pre-existing
rm -rf ~/.config/ctc ~/projects ~/code ~/src ~/dev ~/git ~/repos ~/workspace
[ -f ~/.config/ctc/config ] && { echo "FAIL: leftover config"; exit 1; }

# Pipe the answer + a 'q' for the menu through script's pty. -q quiet,
# -e forwards exit code, -c command, /dev/null suppresses typescript file.
output=$(printf '/home/tester/code\nq\n' | script -qfec 'ctc' /dev/null 2>&1 || true)

echo "$output" | grep -q "First run" \
  || { echo "FAIL: no first-run prompt"; echo "---OUTPUT---"; echo "$output"; exit 1; }

[ -d /home/tester/code ] \
  || { echo "FAIL: ~/code not created"; exit 1; }

grep -q '^BASE=/home/tester/code$' ~/.config/ctc/config \
  || { echo "FAIL: BASE not persisted"; cat ~/.config/ctc/config; exit 1; }

echo "PASS"
