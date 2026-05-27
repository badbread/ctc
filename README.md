# ctc: Claude Terminal Connect

Your phone SSHes into your box and fires `ctc` to launch a `claude` backend. From
that point it's loose: the session lives in the Claude app, so you keep coding on
the phone, pick it up in a browser, or switch to the desktop app, whichever's in
front of you. The phone's the gateway, not a leash. The real `claude` on your
real machine, your repos, your tools, showing up in the app you already use. Not
a web clone, not a chat-bot bridge.

`ctc` launches `claude --remote-control` in a detached tmux session, one per
project, and hands you an arrow-key TUI to manage them. Detached, so it outlives
the shell that started it; the session shows up in the app and keeps running
after you disconnect. One bash file, no daemon to host, no extra attack surface.
Just the SSH you already trust.

### Demo

[![asciicast](https://asciinema.org/a/REPLACE_WITH_ID.svg)](https://asciinema.org/a/REPLACE_WITH_ID)

Launch a backend, trust it once, watch it land in the app (phone shown here, but
it's the same session you'd pick up in the browser or desktop app), then manage
the live ones: attach, detach, flip launch/permission modes. Cast at
[`docs/media/demo.cast`](docs/media/demo.cast).

```
╭────────────────────────────────────────────────────────╮
│ ctc · claude terminal connect                          │
│ dev · opus · acceptEdits · rc:on · detached           │
╰────────────────────────────────────────────────────────╯

 2 running · select to manage
 ▎ ● my-api               live · connect from app
   ● homelab-infra        live · connect from app
   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
   [n] launch new session…
   [o] options
   [q] quit

   ↑↓ move · ⏎ select · ⇧⇥ cycle mode · q quit
```

## Why

Driving my box's `claude` from the app meant four steps, every time:

```bash
ssh mybox
cd ~/projects/whatever
claude
/remote-control      # inside claude, to push it to the app
```

Plus the session died with the shell that launched it. Drop the SSH connection,
lose `claude`. `ctc` collapses the launch to picking a project from a menu, and
because the backend's detached, the SSH session was only ever the ignition. Close
it and keep working from the app, on whatever device you're holding.

## How (and the clock on it)

[Remote Control](https://code.claude.com/docs/en/remote-control) drives a running
`claude` from the app, but the process has to stay alive and there's no headless
mode. So: `claude --remote-control` in a detached tmux session, tmux as the
keepalive Claude Code doesn't ship.

That "doesn't ship" is the whole risk. `ctc` exists because of an open gap
([#30447](https://github.com/anthropics/claude-code/issues/30447)). The day
`--headless` lands, the tmux trick is dead weight and `ctc` is just a launcher
UI. Built on that clock on purpose.

## vs. the alternatives

- **`claude remote-control` server mode** (`--spawn worktree`, `--capacity`):
  one process, many sessions, QR to connect. Great when you're *at* the box.
  `ctc` is for when you're not: per-project backends spun up and managed over
  SSH. They compose; point `ctc` at server mode if you want one process.
- **[vaibhav](https://github.com/manojlds/vaibhav)** (bash per-project tmux for
  phones): closest cousin. `ctc` wires into Remote Control specifically (sessions
  hit the app, not just an attached pane) and apes Claude Code's UI (Shift+Tab
  modes, flag-accurate options).
- **[Claude Code Channels](https://www.macstories.net/stories/first-look-hands-on-with-claude-codes-new-telegram-and-discord-integrations/)**
  (official TG/Discord/iMessage, preview since 2026-03): messaging ergonomic, and
  it has the *same* keepalive problem. Anthropic's docs literally say "combining
  with tmux, screen, or a background process is the current workaround." `ctc`
  hosts exactly that session. They stack.
- **web/Electron UIs** (claudecodeui, Codeman, …): browser file tree + shell,
  plus a service to run and expose. Opposite bet. Nothing to host.

## Setup

Needs: an always-on Linux box (server, VPS, Pi, WSL, whatever) with `claude`
**logged in**, `tmux`, and `bash` 4+. A way to securely SSH into it from wherever
you are; `ctc` doesn't care how you get there.

`ctc` doesn't touch auth, it just `exec`s `claude` with whatever login's already
on the box.

Single file, zero deps:

```bash
curl -fsSL https://raw.githubusercontent.com/badbread/ctc/main/bin/ctc \
  -o ~/.local/bin/ctc && chmod +x ~/.local/bin/ctc
```

Run `ctc`. First run autodetects your project dir (`~/projects`, `~/code`,
`~/src`, …) or asks once. Config at `~/.config/ctc/config`
([example](ctc.config.example)), all of it live-editable in `[o] options`.

<details><summary>git clone / installer instead</summary>

```bash
git clone https://github.com/badbread/ctc && cd ctc && ./install.sh
```

Copies to `~/.local/bin`, writes a starter config, checks for `claude`/`tmux`.
`git pull` to update.
</details>

```bash
ctc                 # session manager
ctc my-api          # fuzzy-jump to the project matching "my-api"
ctc ~/some/path     # explicit dir
```

## Managing sessions

The menu is a process manager for your backends, one tmux session per project.
This is the part I actually live in.

- **Real liveness.** `● live` vs `◌ idle · claude exited`, off the pane's actual
  `pane_current_command` (`claude`/`node` = live), not a bare `has-session`. A
  crashed backend reads idle, not falsely healthy.
- **Attach / detach.** `[a]` drops into the running `claude`; **`Ctrl-b d`**
  detaches back to the menu, session still live and still on the app. Detach ≠
  quit. `/exit` ends it.
- **Kill.** `[k]` on one, or the multi-select screen (`Space` mark, `Enter`
  confirm) to reap a batch.
- **Defaults in `[o]`**, persisted to config, applied to new sessions: launch
  mode (`detached`/`attach`), permission mode (`acceptEdits`/`auto`/
  `bypassPermissions`/`default`/`plan`, or Shift+Tab to cycle), model,
  `--remote-control`, `--continue`. Every toggle maps to a real `claude` flag.

## One-tap launch

`ctc` is a TUI, so any SSH client works as-is. To make launching a single tap,
force a TTY and run it on login. `RemoteCommand` wants the full path if `ctc`
isn't on the non-interactive `PATH` (`~/.local/bin` usually isn't, `which ctc`):

```
Host ctc
    HostName your.box.address
    User you
    RequestTTY force
    RemoteCommand ctc           # full path if needed: /home/you/.local/bin/ctc
```

Phone clients are where this shines, and they each have quirks:

- **Termux** (Android): `pkg install openssh`, host block in `~/.ssh/config`,
  `ssh ctc`. One word? `echo 'ctc(){ ssh ctc; }' >> ~/.bashrc && source ~/.bashrc`.
  `command not found` = stale shell, re-`source` or reopen; if Termux ignores
  `~/.bashrc`, use `~/.profile`. Arrows/Tab/Ctrl on the extra-keys row (Ctrl for
  `Ctrl-b d`).
- **Blink** (iOS): best iOS TUI client. Host + startup command `ctc`, or
  `ssh ctc -t ctc`. Modifiers and Shift+Tab work.
- **Termius**: host + startup snippet `ctc`. Key row has Ctrl/arrows/Tab.

Keys: `↑↓`/`jk` move, `Enter` select, `q`/`Esc` back, bracketed letter
(`n o k a b /`) jumps straight to the action.

## Stuff that went wrong

**Trust dialog deadlock.** `claude`'s first-run "trust this folder?" prompt
blocks a detached backend forever: tmux gives the pane a real pty, so `claude`
thinks it has a terminal and prompts, but nobody's attached to answer, so the RC
session never registers. Looks like the launch no-op'd. Fix: `ctc` checks
`hasTrustDialogAccepted` in `~/.claude.json` and pre-writes it (after a one-time
`[y/N]`) before launch. The non-TTY auto-skip `claude -p` gets doesn't fire here,
because the pty *is* a real terminal as far as `claude` can tell.

**`set -e` footgun, twice.** Under `set -euo pipefail`, a function whose last
statement is a bare `[ … ]` returns that test's exit code; a false test in tail
position kills the script. Bit me in two functions, both only on the unset-config
path my tests masked. Every such function ends `return 0` now. Test the path
where the env vars *aren't* set.

## The AI-assisted part

Claude Code wrote most of the code; I'm an infra guy, not a bash lifer. The
judgment is mine: tmux-as-keepalive, defaulting to `acceptEdits` not full auto
(a phone-reachable agent shouldn't run commands unwatched), killing a `--sandbox`
flag a draft hallucinated that doesn't exist on `claude` 2.1.150, keeping the
800-line engine one portable file with no hardcoded paths. That part doesn't come
from a model.

## License

MIT, see [LICENSE](LICENSE).

<hr />

*Independent, unofficial. "Claude"/"Claude Code" are Anthropic trademarks; not
affiliated or endorsed. It just launches the `claude` you already have.*
