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

## Why I built this

I run Claude Code on a box at home and wanted to use it from my phone. My routine
was: open a terminal app, `ssh` into the box, `cd` to whatever project I wanted,
type `claude`, and start working. Every single time:

```bash
ssh mybox
cd ~/projects/the-thing-i-want
claude
```

Three steps, every time, thumb-typing a path on a phone keyboard. Worse, that
session lived in my SSH connection — lock the phone or switch apps and the
connection dropped, taking `claude` with it. And it had nothing to do with
Claude Code's nice mobile app; I was staring at a raw terminal.

`ctc` is that routine collapsed into one command and made drop-proof: pick a
project from a menu, it launches a Remote-Control-enabled `claude` in a detached
tmux session that survives disconnects, and then I drive it from the **Claude
app** — the terminal's just the launcher.

## Why it works this way

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

## How this compares

This space is crowded; here's the honest positioning.

- **vs. `claude remote-control` server mode** (the official persistent server,
  `--spawn worktree`, `--capacity`): server mode is great when you're *at* the
  machine — it serves many sessions from one running process and you scan a QR
  to connect. `ctc` is aimed at the *phone-first* case: spawn a fresh
  per-project backend **from your phone over SSH** and manage its lifecycle
  (launch/list/attach/kill) from a terminal menu, without being at the box. The
  two compose fine — you can point `ctc`'s launch at server mode if you prefer
  one process.
- **vs. [vaibhav](https://github.com/manojlds/vaibhav)** (a bash per-project
  tmux launcher for phones): closest cousin. `ctc`'s difference is that it wires
  specifically into Claude Code's **Remote Control** (so sessions appear in the
  Claude app, not just an attached terminal) and mirrors Claude Code's UI
  (Shift+Tab modes, the flag-accurate options screen).
- **vs. web/Electron UIs** (CloudCLI/claudecodeui, Codeman): those give a
  browser file tree + shell with no SSH client. `ctc` is the opposite bet — no
  server to run, no extra attack surface, just a script on your box you reach
  over the SSH you already trust.

**Honest caveat:** `ctc`'s core reason to exist is that Remote Control has no
headless/daemon mode yet ([issue #30447](https://github.com/anthropics/claude-code/issues/30447)).
If Anthropic ships `--headless`, the tmux-keepalive trick becomes unnecessary and
`ctc` becomes mostly a UI convenience.

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

`ctc` is a single bash script with no dependencies of its own. **On your Linux
box** (the one running Claude Code), one command:

```bash
curl -fsSL https://raw.githubusercontent.com/badbread/ctc/main/bin/ctc \
  -o ~/.local/bin/ctc && chmod +x ~/.local/bin/ctc
```

(Make sure `~/.local/bin` is on your `PATH`.) That's it — run `ctc`.

**First run** asks where your projects live (or auto-detects `~/projects`,
`~/code`, `~/src`, …) and remembers it. No manual config editing required.

<details><summary>Prefer git clone / an installer?</summary>

```bash
git clone https://github.com/badbread/ctc && cd ctc && ./install.sh
```
`install.sh` copies `bin/ctc` to `~/.local/bin`, writes a starter config, and
checks for `claude`/`tmux`. Easy to update later with `git pull`.
</details>

Config lives at `~/.config/ctc/config` (see [`ctc.config.example`](ctc.config.example));
everything is also changeable live in the `[o] options` screen.

## Use it

On the box:

```bash
ctc                 # open the session manager
ctc my-api          # fuzzy-jump: launch/connect the project matching "my-api"
ctc ~/some/path     # launch in an explicit directory
```

## Connect from your phone

The idea on every client is the same: an SSH connection that forces a TTY and
runs `ctc` on login. Set it up once and launching is a single tap.

The host block is the same everywhere — `RemoteCommand` must be the full path if
`ctc` isn't on the non-interactive SSH `PATH` (use `which ctc` on the box to
check; `~/.local/bin` often isn't on it for non-login shells):

```
Host ctc
    HostName 100.x.y.z          # your box's address (Tailscale IP shown)
    User you
    RequestTTY force            # ctc is a TUI — it needs a terminal
    RemoteCommand ctc           # or the full path, e.g. /home/you/.local/bin/ctc
```

### Termux (Android)

1. `pkg install openssh` if needed.
2. Put the host block above in `~/.ssh/config`.
3. `ssh ctc`.

Optional one-word launch — add a function to `~/.bashrc`, then **reload it**:

```bash
echo 'ctc(){ ssh ctc; }' >> ~/.bashrc
source ~/.bashrc            # the already-open shell won't see it until you do this
```

> Gotcha: if `ctc: command not found` right after adding the function, that's a
> stale shell — `source ~/.bashrc` (or open a new Termux session). If `source`
> still doesn't help, your Termux isn't reading `~/.bashrc`; put the function in
> `~/.profile` instead and reopen Termux. For a banner/auto-launch on open, add
> the line(s) to the bottom of `~/.bashrc`.

Arrow keys and Tab live on Termux's extra-keys row; `Ctrl` is a chip there too
(used for `Ctrl-b d` to detach — see below).

### Blink Shell (iOS)

Blink has first-class SSH hosts and good modifier-key support (best iOS option
for a TUI). Add a host in **Settings → Hosts** (HostName, User, key) and set its
startup command to `ctc`, or just run `ssh ctc -t ctc` from the Blink prompt.
`Ctrl` and arrows are on the keyboard; Shift+Tab works.

### Termius (iOS/Android)

Create a host (address, user, key). Under the host's **Startup snippet / command**,
put `ctc`. Termius shows a key row with `Ctrl`, arrows and `Tab` for navigation
and detaching.

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
