# ctc — Claude Terminal Connect

Launch **Claude Code** as detached, Remote-Control-enabled backends and manage
them from a phone-friendly terminal menu. You start a coding session on your
Linux box from your phone in two taps, then drive the actual work from the
**Claude mobile/web app** — the session keeps running even when your phone
disconnects.

```
 ┌─┐┌┬┐┌─┐  claude terminal connect
 │   │ │    detached RC backends · my-server
 └─┘ ┴ └─┘
────────────────────────────────────────
 1 running · select to manage
 ▎ ● my-api            live · connect from app
   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
   [n] launch new session…
   [o] options   auto RC● detached
   [q] quit
   ↑↓/jk · enter · q
```

## Why

[Claude Code's Remote Control](https://code.claude.com/docs/en/remote-control)
lets you drive a running `claude` session from the Claude app — but the `claude`
**process has to stay alive**, and there's no built-in headless/daemon mode. The
usual answer is "wrap it in tmux and SSH in," which works but is fiddly,
especially from a phone.

`ctc` makes that ergonomic: it launches `claude --remote-control` in a **detached
tmux session** (the process stays alive, no terminal attached), one per project,
and gives you a small arrow-key TUI to launch / list / kill those backends. You
connect to them from the Claude app. From a phone over SSH (Termux on Android,
Blink/Termius on iOS), it's a two-tap workflow.

## Requirements

- A Linux box (server, VPS, homelab, Pi, WSL — anything always-on) with:
  - [**Claude Code**](https://code.claude.com) installed **and logged in**
  - **tmux**
  - **bash** 4+
- A way to reach that box from your phone over **SSH**. A mesh VPN like
  [**Tailscale**](https://tailscale.com) or WireGuard is the easiest and safest;
  LAN-only and port-forwarding also work. `ctc` is connectivity-agnostic — bring
  your own SSH reachability.
- A terminal/SSH app on the phone: **Termux** (Android), **Blink** or **Termius**
  (iOS).

> Note: `ctc` does not handle Claude authentication — it just launches `claude`,
> which uses whatever login already exists on the box. Log in once with `claude`
> on the server before using `ctc`.

## Install

```bash
git clone https://github.com/badbread/ctc
cd ctc
./install.sh          # installs bin/ctc to ~/.local/bin and writes a default config
```

Or drop `bin/ctc` anywhere on your `PATH` manually. Then set where your projects
live (defaults to `~/projects`):

```bash
mkdir -p ~/.config/ctc
echo 'BASE=~/code' > ~/.config/ctc/config     # point at your projects dir
```

## Use it

On the box:

```bash
ctc                 # open the session manager
ctc my-api          # fuzzy-jump: launch/connect the project matching "my-api"
ctc ~/some/path     # launch in an explicit directory
```

From a phone, add an SSH host that runs `ctc` on connect, e.g. in Termux
`~/.ssh/config`:

```
Host ctc
    HostName 100.x.y.z          # your box (Tailscale IP shown)
    User you
    RequestTTY force
    RemoteCommand ctc
```

then `ssh ctc`. (See [docs/phone-setup.md](docs/phone-setup.md) for the full
phone walkthrough.)

### Keys

| Key | Action |
|---|---|
| `↑/↓` or `j/k` | move |
| `Enter` | choose |
| `q` / `Esc` | back / quit |
| bracketed letter (`n`, `o`, `k`, `a`, `b`, `/`) | jump straight to that action |

Select a **running** session to attach (`a`) or kill (`k`). When attached,
**`Ctrl-b` then `d`** detaches and returns you to the menu — the session keeps
running. `/exit` inside Claude ends it.

## Options

Press `o`. Persisted to `~/.config/ctc/config`:

- **launch mode** — `detached` (backend you connect to from the app, default) or
  `attach` (open the session in your terminal over SSH).
- **permission mode** — `auto` / `acceptEdits` / `bypassPermissions` / `default` /
  `plan` (maps to `claude --permission-mode`).
- **remote control** — toggle `--remote-control`.

## License

MIT — see [LICENSE](LICENSE).

---

*`ctc` is an independent, unofficial tool. "Claude" and "Claude Code" are
trademarks of Anthropic; this project is not affiliated with or endorsed by
Anthropic. It simply launches the `claude` CLI you already have installed.*
