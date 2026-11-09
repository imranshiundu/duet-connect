#!/usr/bin/env bash
# Duet Connect installer (Linux)
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="$HOME/.config/duetconnect"
KEY_DIR="$HOME/.ssh/duetconnect"

echo "=================================================="
echo "  Duet Connect Installer"
echo "  Repo: $REPO_DIR"
echo "=================================================="

# ---------------------------------------------------------------- deps
echo "▶ Installing system dependencies (rsync, openssh-client, python3-pip)"
if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update -y
  sudo apt-get install -y rsync openssh-client python3-pip python3-venv
elif command -v dnf >/dev/null 2>&1; then
  sudo dnf install -y rsync openssh-clients python3-pip
elif command -v pacman >/dev/null 2>&1; then
  sudo pacman -Sy --needed rsync openssh python-pip
else
  echo "  [WARN] Unknown package manager — install rsync, openssh, python3 manually"
fi

# ---------------------------------------------------------------- python package
echo "▶ Installing Duet Connect Python package"
python3 -m pip install --user -e "$REPO_DIR"

# ---------------------------------------------------------------- config dirs
echo "▶ Creating config and key directories"
mkdir -p "$CONFIG_DIR" "$KEY_DIR"
if [ ! -f "$CONFIG_DIR/duetconnect.cfg" ]; then
  cp "$REPO_DIR/examples/duetconnect.cfg.example.laptop" "$CONFIG_DIR/duetconnect.cfg"
  echo "  Wrote default config → $CONFIG_DIR/duetconnect.cfg"
else
  echo "  Config already present, skipping"
fi

# ---------------------------------------------------------------- path check
if ! command -v duet-connect >/dev/null 2>&1; then
  echo "  [WARN] 'duet-connect' not on PATH. Add ~/.local/bin to PATH:"
  echo "         echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
fi

echo ""
echo "=================================================="
echo "  Install complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Edit $CONFIG_DIR/duetconnect.cfg (phone_user, phone_port, backup_destination)"
echo "  2. On the phone (Termux): pkg install openssh rsync python git android-tools"
echo "  3. On the phone: termux-setup-storage → tap Allow"
echo "  4. On the phone: passwd → set SSH password"
echo "  5. On the phone: sshd → start SSH server on port 8022"
echo "  6. Run: duet-connect setup     (generates SSH keys)"
echo "  7. Run: ssh-copy-id -i ~/.ssh/duetconnect/duetconnect_phone.pub"
echo "              -p 8022 u0_a320@<phone-ip>"
echo "  8. Run: duet-connect doctor    (verify connection)"
echo "=================================================="
