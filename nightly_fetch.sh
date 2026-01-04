#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="${REPO_DIR:-$HOME/finance-daily}"
cd "$REPO_DIR"

# Make sure these match your EC2 paths (override via env if desired)
export DATA_DIR="${DATA_DIR:-/var/lib/finance_etl/data}"
export CONFIG_DIR="${CONFIG_DIR:-$REPO_DIR/finance_daily_config}"

# --- Bootstrap tooling on Ubuntu (assume nothing else) ---
# Needs passwordless sudo for fully unattended runs (cron/systemd).
if ! command -v pipx >/dev/null 2>&1; then
  sudo -n apt-get update -y || {
    echo "sudo requires a password (or sudo isn't available)."
    echo "Run once interactively:"
    echo "  sudo apt-get update -y && sudo apt-get install -y pipx"
    exit 1
  }
  sudo -n apt-get install -y pipx
fi

# Make sure pipx-installed binaries are available in this process
python3 -m pipx ensurepath >/dev/null 2>&1 || true
export PATH="$HOME/.local/bin:$PATH"

if ! command -v poetry >/dev/null 2>&1; then
  pipx install poetry
else
  pipx upgrade poetry >/dev/null 2>&1 || true
fi

# Keep repo up to date (fail if it would require a merge)
git pull --ff-only

# Install/update deps (non-interactive for cron)
poetry install --no-interaction --only main

# Run the nightly fetch
exec poetry run nightly_fetch