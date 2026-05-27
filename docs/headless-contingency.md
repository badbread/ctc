# When Claude Code ships native headless mode

**Status: not yet shipped as of 2026-05.** This is a staged pivot, kept here so
the day `--headless` (or `--daemon`) lands, repositioning ctc is a 10-minute
commit, not a scramble. Tracking issues: [#30447](https://github.com/anthropics/claude-code/issues/30447),
[#29116](https://github.com/anthropics/claude-code/issues/29116),
[#28420](https://github.com/anthropics/claude-code/issues/28420).

## The one-sentence repositioning

> Claude Code now has native headless mode — so ctc no longer needs tmux to keep
> sessions alive. ctc is now purely the phone-friendly launcher and manager: pick
> a project, set permission mode and flags the way Claude Code expects, and start
> or attach a session in two keystrokes.

## Why ctc survives the day this ships

Nothing in the *user-facing* pitch changes. The job — "start and manage coding
work on my always-on machine from the device in my pocket" — doesn't go away when
the plumbing underneath changes. We swap one mechanism for another and keep the
entire value proposition:

- **Phone-first launcher + per-project session management** — unchanged.
- **No server / minimal attack surface** — unchanged, and arguably *stronger*
  once we can drop the tmux dependency.
- **Claude-Code-native feel + safe-by-default (`acceptEdits`)** — unchanged.

It's a dependency drop, not a feature loss. Spin it as "simpler than ever," and
position ctc as the first launcher to adopt native headless cleanly.

## Concrete change list for that day

1. `bin/ctc`: replace the detached-tmux launch path in `ensure_session()` /
   `launch()` with the native headless invocation. Keep tmux as a fallback for
   older `claude` versions if the engine can detect the flag via `claude --help`.
2. `README.md`:
   - Hero: change "launches `claude --remote-control` as a detached session"
     to the native-headless phrasing.
   - "Why it works this way": replace the tmux-keepalive explanation with the
     headless one.
   - "Honest caveat" block: replace with "ctc adopted native headless in
     vX.Y — the tmux era is documented in git history."
3. Comparison section: the "same keepalive problem" framing vs. Channels no
   longer applies if Channels also adopts headless; revisit.

## What does NOT change

The trust-dialog handling, project discovery, liveness detection, the TUI, the
options screen, the phone client setup docs — all orthogonal to the keepalive
mechanism and carry over verbatim.
