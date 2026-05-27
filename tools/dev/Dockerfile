# ctc dev/test environment.
# Fresh, throwaway Debian box per scenario. Builds in ~10s.
#
#   docker build -t ctc-dev .
#   docker run --rm -v /path/to/ctc/bin/ctc:/usr/local/bin/ctc:ro ctc-dev ctc
#
# Run via tools/dev/run.sh from the repo root, which handles mounts + scenarios.
FROM debian:13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        bash tmux git curl ca-certificates python3 procps less \
        util-linux \
    && rm -rf /var/lib/apt/lists/*

# Stub claude — installed at /usr/local/bin/claude so `command -v claude`
# succeeds at ctc startup, but launches do nothing (just log + sleep).
COPY claude-stub /usr/local/bin/claude
RUN chmod +x /usr/local/bin/claude

# Non-root test user — exercises the same install path a real downloader would
# (no root-only permissions in scope, ~/.config and ~/.local writeable, etc.).
RUN useradd -m -s /bin/bash tester
USER tester
WORKDIR /home/tester
ENV HOME=/home/tester PATH=/home/tester/.local/bin:/usr/local/bin:/usr/bin:/bin
