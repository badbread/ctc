#!/usr/bin/env bash
# list_repos finds .git markers under BASE up to DEPTH.
# Source ctc directly (minus the final `main "$@"` invocation) so we can call
# the function and capture its stdout.
set -euo pipefail

rm -rf ~/.config/ctc ~/projects
mkdir -p \
  ~/projects/repo1/.git \
  ~/projects/repo2/.git \
  ~/projects/sub/repo3/.git

mkdir -p ~/.config/ctc
printf 'BASE=/home/tester/projects\nDEPTH=2\n' > ~/.config/ctc/config

# Strip the last line (`main "$@"`) so sourcing doesn't run main()
got=$(
  source <(head -n -1 /usr/local/bin/ctc)
  load_cfg
  list_repos
)

for expected in \
  /home/tester/projects/repo1 \
  /home/tester/projects/repo2 \
  /home/tester/projects/sub/repo3
do
  echo "$got" | grep -qxF "$expected" \
    || { echo "FAIL: missing $expected"; echo "---got---"; echo "$got"; exit 1; }
done

echo "PASS"
