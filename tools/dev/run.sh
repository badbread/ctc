#!/usr/bin/env bash
# Entry point for ctc dev/test scenarios.
#
# Usage:
#   ./run.sh                # build (if needed) + run all scenarios
#   ./run.sh 02             # run just scenarios/02*.sh
#   ./run.sh --build        # force rebuild the image
#   ./run.sh --shell        # interactive bash in a fresh container
#
# Each scenario runs in its OWN fresh container so state can't leak between
# tests. The repo's bin/ctc is bind-mounted in read-only, so iterating on the
# script doesn't require a rebuild.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CTC_REPO="$(cd "$HERE/../.." && pwd)"
IMAGE="ctc-dev"

build() {
  echo "===> docker build $IMAGE"
  docker build -t "$IMAGE" "$HERE"
}

run_scenario() {
  local script="$1" name; name="$(basename "$script" .sh)"
  printf '\n'
  printf '%.0s=' {1..64}; printf '\n'
  printf '  %s\n' "$name"
  printf '%.0s=' {1..64}; printf '\n'

  docker run --rm \
    -v "$CTC_REPO/bin/ctc:/usr/local/bin/ctc:ro" \
    -v "$HERE/scenarios:/scenarios:ro" \
    -e SCENARIO="$name" \
    "$IMAGE" \
    bash "/scenarios/$(basename "$script")"
}

case "${1:-}" in
  --build) build; exit 0 ;;
  --shell)
    docker images -q "$IMAGE" | grep -q . || build
    docker run --rm -it \
      -v "$CTC_REPO/bin/ctc:/usr/local/bin/ctc:ro" \
      -v "$HERE/scenarios:/scenarios:ro" \
      "$IMAGE" bash
    exit 0 ;;
esac

docker images -q "$IMAGE" | grep -q . || build

filter="${1:-}"
shopt -s nullglob
if [ -n "$filter" ]; then
  scenarios=("$HERE"/scenarios/${filter}*.sh)
else
  scenarios=("$HERE"/scenarios/*.sh)
fi

if [ "${#scenarios[@]}" -eq 0 ]; then
  echo "No scenarios match '${filter:-*}*.sh'" >&2; exit 1
fi

pass=0; fail=0; failed_names=()
for s in "${scenarios[@]}"; do
  if run_scenario "$s"; then
    pass=$((pass+1))
  else
    fail=$((fail+1))
    failed_names+=("$(basename "$s" .sh)")
  fi
done

printf '\n'
printf '%.0s=' {1..64}; printf '\n'
printf '  %d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -gt 0 ] && printf '  failed: %s\n' "${failed_names[*]}"
printf '%.0s=' {1..64}; printf '\n'

[ "$fail" -eq 0 ]
