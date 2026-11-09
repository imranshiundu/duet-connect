# Install Duet Connect

## Requirements

| Component | Minimum | Notes |
|-----------|---------|-------|
| Laptop OS | Ubuntu 24.04 | Debian, Mint, Fedora also work |
| Python | 3.8+ | 3.11 recommended |
| rsync | 3.x | --partial, --checksum support |
| openssh-client | Any | ssh, ssh-keygen, ssh-keyscan |
| Phone | Android + Termux | F-Droid version, not Play Store |
| Phone packages | openssh, rsync, python, git, android-tools | `pkg install` |

---

## Step 1 — Install system dependencies (laptop)

```bash
# Ubuntu / Debian / Mint
sudo apt-get update -y
sudo apt-get install -y rsync openssh-client python3-pip python3-venv

# Fedora
sudo dnf install -y rsync openssh-clients python3-pip

# Arch
sudo pacman -Sy --needed rsync openssh python-pip
```

---

## Step 2 — Install Duet Connect (laptop)

```bash
git clone https://github.com/imranshiundu/duet-connect.git
cd duet-connect
python3 -m pip install -e .
```

Verify:
```bash
duetconnect --help
```

---

## Step 3 — Set up the phone (Termux)

Run these **in the Termux app on your phone**:

```bash
pkg update && pkg upgrade -y
pkg install -y openssh rsync python git android-tools
termux-setup-storage      # tap "Allow" on the popup
passwd                    # set a temporary SSH password
sshd                      # start SSH server on port 8022
termux-wake-lock          # keep phone awake during transfers
ip -4 addr show wlan0     # note your phone's IP
```

---

## Step 4 — Pair phone and laptop

```bash
# Generate keys
duetconnect setup

# Copy phone key to the phone (one-time, uses the password you set)
ssh-copy-id -i ~/.ssh/duetconnect/duetconnect_phone.pub \
  -p 8022 u0_a320@<phone-ip>

# Verify
duetconnect doctor
```

---

## Step 5 — Configure (optional)

Copy the example config and edit for your setup:

```bash
cp duet-connect.cfg.example ~/.config/duetconnect/duetconnect.cfg
# Edit: phone_user, phone_port, backup_destination, discovery_network
```

---

## Verify everything works

```bash
duetconnect status
duetconnect doctor
```

You should see `[OK]` for phone SSH and laptop storage.

---

## Uninstall

```bash
python3 -m pip uninstall duet-connect
rm -rf ~/.config/duetconnect ~/.ssh/duetconnect
```
