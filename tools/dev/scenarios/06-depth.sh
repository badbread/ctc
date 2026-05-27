#!/usr/bin/env bash
# DEPTH=1 = flat (only repos directly under BASE).
# DEPTH=2 = one level of subdir nesting allowed.
# DEPTH=3 = two levels of subdir nesting allowed.
set -euo pipefail

rm -rf ~/.config/ctc ~/projects
mkdir -p \
  ~/projects/flat/.git \
  ~/projects/one/sub1/.git \
  ~/projects/two/lvl1/lvl2/.git

mkdir -p ~/.config/ctc

run_with_depth() {
  printf 'BASE=/home/tester/projects\nDEPTH=%s\n' "$1" > ~/.config/ctc/config
  (
    source <(head -n -1 /usr/local/bin/ctc)
    load_cfg
    list_repos
  )
}

assert_has()    { echo "$1" | grep -qxF "$2" || { echo "FAIL: depth=$3 missing $2"; echo "$1"; exit 1; }; }
assert_lacks()  { echo "$1" | grep -qxF "$2" && { echo "FAIL: depth=$3 unexpectedly has $2"; echo "$1"; exit 1; } || true; }

# DEPTH=1: only flat
got=$(run_with_depth 1)
assert_has   "$got" /home/tester/projects/flat            1
assert_lacks "$got" /home/tester/projects/one/sub1        1
assert_lacks "$got" /home/tester/projects/two/lvl1/lvl2   1

# DEPTH=2: flat + one level
got=$(run_with_depth 2)
assert_has   "$got" /home/tester/projects/flat            2
assert_has   "$got" /home/tester/projects/one/sub1        2
assert_lacks "$got" /home/tester/projects/two/lvl1/lvl2   2

# DEPTH=3: all three
got=$(run_with_depth 3)
assert_has   "$got" /home/tester/projects/flat            3
assert_has   "$got" /home/tester/projects/one/sub1        3
assert_has   "$got" /home/tester/projects/two/lvl1/lvl2   3

echo "PASS"
