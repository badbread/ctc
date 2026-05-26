#!/usr/bin/env bash
# ctc installer — copies bin/ctc onto your PATH and writes a default config.
# Idempotent. No root needed (installs to ~/.local/bin by default).
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
src="$here/bin/ctc"
[ -f "$src" ] || { echo "error: $src not found (run from the cloned repo)" >&2; exit 1; }

# Pick an install dir: ~/.local/bin if it's (or can be) on PATH, else /usr/local/bin.
bindir="${CTC_BINDIR:-$HOME/.local/bin}"
mkdir -p "$bindir"
install -m 0755 "$src" "$bindir/ctc"
echo "installed: $bindir/ctc"

case ":$PATH:" in
  *":$bindir:"*) ;;
  *) echo "note: $bindir is not on your PATH — add this to your shell rc:"
     echo "      export PATH=\"$bindir:\$PATH\"" ;;
esac

# Default config (don't clobber an existing one).
cfgdir="${XDG_CONFIG_HOME:-$HOME/.config}/ctc"
mkdir -p "$cfgdir"
if [ ! -f "$cfgdir/config" ]; then
  install -m 0644 "$here/ctc.config.example" "$cfgdir/config"
  echo "wrote default config: $cfgdir/config  (edit BASE to point at your projects)"
else
  echo "config exists, left as-is: $cfgdir/config"
fi

# Friendly dependency check (warn, don't fail — they may install later).
for dep in claude tmux; do
  command -v "$dep" >/dev/null 2>&1 || echo "warning: '$dep' not found on PATH — ctc needs it at runtime"
done

echo "done. run:  ctc"
