# Termux — Android Terminal & Linux Environment

## What is Termux?

```
┌─────────────────────────────────────────────────────────────┐
│                    ANDROID OS (your phone)                  │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   WhatsApp   │    │     Chrome   │    │   Camera     │  │
│  │   (app)      │    │   (app)      │    │   (app)      │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                   │                   │           │
│         └───────────────────┴───────────────────┘           │
│                    Android Linux kernel                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐    │
│  │                 TERMUX APP                          │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │    │
│  │  │   bash      │  │   python3   │  │   openssh   │ │    │
│  │  │   rsync     │  │   git       │  │   adb       │ │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘ │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

**Termux** is a powerful terminal emulator and Linux environment for Android.
It gives you a real command-line shell (bash/zsh) plus access to 1,000+ Linux
packages through its own package manager (`pkg`). No root required.

Think of it as **"a miniature Ubuntu inside your phone"** that can:
- Run bash, python, git, rsync, ssh, nginx, sqlite, and more
- Access your phone's shared storage (`/storage/emulated/0`)
- Run an SSH server so your laptop can connect to your phone
- Run an SSH client so your phone can connect to your laptop

---

## Install Termux

**⚠️ Use F-Droid, NOT Google Play.** The Play Store version is outdated and
missing critical updates.

```
┌─────────────────────────────────────────────────────────────┐
│  1. Open F-Droid (or install F-Droid from f-droid.org)      │
│  2. Search: Termux                                          │
│  3. Tap Install                                             │
│  4. Open Termux — a black terminal window appears           │
└─────────────────────────────────────────────────────────────┘
```

---

## First-time setup inside Termux

Run these commands **in the Termux app on your phone**:

```bash
# 1. Update package lists
pkg update && pkg upgrade -y

# 2. Install core tools we need
pkg install -y openssh rsync python git android-tools

# 3. Grant Termux access to your phone's files (photos, videos, documents)
termux-setup-storage
#   → A popup appears on screen: tap "Allow"

# 4. Set a password for the SSH user (temporary, for the transfer)
passwd
#   → Enter a password (e.g., imran123)
#   → Retype to confirm

# 5. Start the SSH server on port 8022
sshd

# 6. Keep the phone awake while transferring
termux-wake-lock
```

---

## Verify Termux is ready

```bash
# Check your phone's IP address (needed by the laptop)
ip -4 addr show wlan0 | grep inet
# Example output: 192.168.100.51

# Confirm SSH is listening
pgrep -a sshd
```

---

## Termux file layout (important)

| Path | What it is |
|------|------------|
| `/data/data/com.termux/files/home` | Your Termux home folder (`~`) |
| `/storage/emulated/0` | Phone's shared storage (DCIM, Download, Movies, etc.) |
| `~/storage` | Shortcut to shared storage after `termux-setup-storage` |
| `/data/data/com.termux/files/usr/bin` | Installed binaries (ssh, rsync, python) |

```
~/storage/
├── dcim/          → /storage/emulated/0/DCIM
├── downloads/     → /storage/emulated/0/Download
├── documents/     → /storage/emulated/0/Documents
├── movies/        → /storage/emulated/0/Movies
├── music/         → /storage/emulated/0/Music
├── pictures/      → /storage/emulated/0/Pictures
├── audiobooks/    → /storage/emulated/0/Audiobooks
├── podcasts/      → /storage/emulated/0/Podcasts
└── shared/        → all shared storage
```

---

**Next:** [Connection methods →](CONNECTION-METHODS.md)
