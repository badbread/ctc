# `tools/dev/` — ctc dev/test fixture

A throwaway Docker environment for testing ctc without touching your real
home dir. Use it to verify install, autodetect, and repo-scanning behavior
in a clean Linux box before shipping changes.

## Quickstart

```bash
# From the repo root
cd tools/dev
./run.sh                 # build (first run) + run every scenario
./run.sh 02              # run just scenarios/02*.sh
./run.sh --shell         # drop into a bash shell inside a fresh container
./run.sh --build         # force rebuild the image
```

Each scenario runs in its OWN fresh container so state can't leak between
tests. The repo's `bin/ctc` is bind-mounted in read-only, so iterating on
the script doesn't require a rebuild — just rerun `./run.sh`.

## What's tested

| Scenario | What it covers |
|---|---|
| `00-smoke.sh`         | ctc starts, banner renders, `q` exits cleanly |
| `01-fresh-firstrun.sh` | Empty home → interactive first-run prompt fires + persists BASE (uses `script -qec` for a real pty) |
| `02-autodetect.sh`    | `~/projects` present → silent autodetect + persist |
| `03-env-override.sh`  | `CTC_BASE=…` wins for one run, does NOT clobber the config file |
| `04-list-repos.sh`    | `list_repos()` finds `.git` markers under BASE up to DEPTH |
| `05-prune-junk.sh`    | `list_repos()` prunes `node_modules` / `vendor` / `.cache` / `.venv` / `#recycle` / `@eaDir` / `.Trashes` but keeps `.git` itself |
| `06-depth.sh`         | `DEPTH=1/2/3` clamps the scan correctly |

## How the stub works

`claude-stub` (installed at `/usr/local/bin/claude` in the image) records its
invocation args to `~/.claude-stub.log` and then `exec sleep 86400`. That
keeps the tmux session in `live` state without burning real Claude credits
or needing network. ctc only needs `command -v claude` at startup; the actual
launch goes through the stub.

If a scenario needs to inspect what flags ctc passed, it can `cat
~/.claude-stub.log` after the run.

## Driving the TUI

Most scenarios don't need a pty — they pipe input through stdin and ctc's
no-tty fallback paths kick in (the numbered picker, the no-prompt resolve).
The first-run scenario DOES need a pty because `resolve_base()` checks
`have_tty` before the prompt; it uses `script -qec` to give ctc a real
terminal while still feeding stdin programmatically.

For function-level tests (like 04-list-repos and 05-prune-junk), the script
does:

```bash
source <(head -n -1 /usr/local/bin/ctc)
load_cfg
list_repos
```

`head -n -1` strips the final `main "$@"` invocation so sourcing defines the
functions without running the program. Cheap, no test hooks in production.

## Adding a scenario

Drop a `NN-name.sh` in `scenarios/`. Exit `0` for pass, non-zero for fail.
Print `PASS` on success. The runner picks it up automatically.
