#!/usr/bin/env bash
# list_repos prunes the usual dependency / NAS / OS junk dirs so a deep scan
# stays fast and the menu doesn't fill with deleted/backup copies.
set -euo pipefail

rm -rf ~/.config/ctc ~/projects
mkdir -p ~/projects/realrepo/.git
# Junk dirs that should be pruned (each with a nested .git to be tempting)
mkdir -p ~/projects/realrepo/node_modules/somepkg/.git
mkdir -p ~/projects/realrepo/vendor/lib/.git
mkdir -p ~/projects/realrepo/.cache/junk/.git
mkdir -p ~/projects/realrepo/.venv/site-packages/foo/.git
mkdir -p ~/projects/'#recycle'/oldrepo/.git
mkdir -p ~/projects/'@eaDir'/synojunk/.git
mkdir -p ~/projects/.Trashes/whatever/.git
# But NOT this — .git itself must NOT be pruned (it IS the marker)

mkdir -p ~/.config/ctc
printf 'BASE=/home/tester/projects\nDEPTH=4\n' > ~/.config/ctc/config

got=$(
  source <(head -n -1 /usr/local/bin/ctc)
  load_cfg
  list_repos
)

echo "$got" | grep -qxF /home/tester/projects/realrepo \
  || { echo "FAIL: realrepo missing"; echo "$got"; exit 1; }

for junk in node_modules vendor .cache .venv '#recycle' @eaDir .Trashes; do
  if echo "$got" | grep -q "$junk"; then
    echo "FAIL: junk dir '$junk' not pruned"; echo "$got"; exit 1
  fi
done

echo "PASS"
