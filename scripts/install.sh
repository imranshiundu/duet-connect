#!/usr/bin/env bash
# Duet Connect installer (Linux). Installs Python package + system dependencies.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="$HOME/.config/duetconnect"
KEY_DIR="$HOME/.ssh/duetconnect"

echo "==> Duet Connect installer"
echo "    repo: $REPO_DIR"

# 1. System dependencies
echo "==> Installing system dependencies (rsync, openssh-client, python3-pip)"
if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update -y
  sudo apt-get install -y rsync openssh-client python3-pip python3-venv
elif command -v dnf >/dev/null 2>&1; then
  sudo dnf install -y rsync openssh-clients python3-pip
elif command -v pacman >/dev/null 2>&1; then
  sudo pacman -Sy --needed rsync openssh python-pip
else
  echo "[WARN] Could not detect package manager. Install rsync, openssh, python3 manually."
fi

# 2. Python package (editable, user install)
echo "==> Installing Duet Connect Python package"
python3 -m pip install --user -e "$REPO_DIR"

# 3. Config directory + example config
mkdir -p "$CONFIG_DIR" "$KEY_DIR"
if [ ! -f "$CONFIG_DIR/duetconnect.cfg" ]; then
  cp "$REPO_DIR/duetconnect.cfg.example" "$CONFIG_DIR/duetconnect.cfg"
  echo "    wrote default config -> $CONFIG_DIR/duetconnect.cfg"
else
  echo "    config already present, skipping"
fi

# 4. PATH check
if ! command -v duetconnect >/dev/null 2>&1; then
  echo "[WARN] 'duetconnect' not on PATH. Add ~/.local/bin to PATH or re-log."
fi

echo "==> Done. Next steps:"
echo "    1. Edit $CONFIG_DIR/duetconnect.cfg (phone_user, phone_port, backup_destination)"
echo "    2. Run: duetconnect setup        (generates SSH keys)"
echo "    3. On the phone, run: ssh-copy-id -i ~/.ssh/duetconnect/duetconnect_phone.pub -p 8022 u0_a320@<phone-ip>"
echo "    4. Run: duetconnect doctor"
