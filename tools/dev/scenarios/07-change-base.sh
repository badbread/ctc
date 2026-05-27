#!/usr/bin/env bash
# Options menu: change BASE via the new "projects dir" row.
# Drives the full sequence through a PTY (script -qfec):
#   'o'                       hotkey from main menu -> options screen
#   '\n'                      enter on first row (projects dir)
#   path + '\n'               new path; doesn't exist yet, so ctc asks to create
#   'y\n'                     yes, create it
#   'q'                       back out of options screen
#   'q'                       quit the main menu
set -euo pipefail

rm -rf ~/.config/ctc ~/projects ~/newpath
mkdir -p ~/projects/foo/.git
mkdir -p ~/.config/ctc
printf 'BASE=/home/tester/projects\n' > ~/.config/ctc/config

output=$(
  printf 'o\n/home/tester/newpath\ny\nqq' | script -qfec 'ctc' /dev/null 2>&1 || true
)

[ -d /home/tester/newpath ] || {
  echo "FAIL: newpath dir was not created"
  echo "$output" | tail -15
  exit 1
}

grep -q '^BASE=/home/tester/newpath$' ~/.config/ctc/config || {
  echo "FAIL: BASE not updated in config"
  cat ~/.config/ctc/config
  echo "$output" | tail -15
  exit 1
}

echo PASS
