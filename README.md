# Duet Connect

**Connect your devices. Own your infrastructure.**

A two-way Android (Termux) ↔ Linux connectivity toolkit over local Wi-Fi.
No root. No cloud. No hardcoded credentials.

```
┌──────────────────────────────────────────────────────────────────────┐
│                      DUET CONNECT                                    │
│              Android (Termux)  ◄────────►  Linux Laptop              │
│                                                                       │
│  • SSH connectivity (both directions)                               │
│  • File transfer & sync via rsync (resumable, verified)             │
│  • Encrypted backups to external drives                              │
│  • Remote inspection: battery, storage, processes                    │
│  • Works on Wi-Fi, phone hotspot, USB tethering, ADB                 │
└──────────────────────────────────────────────────────────────────────┘
```

## Why Duet Connect?

You need to move your phone's data before giving it away — but the cable
doesn't work, there's no SD card, and you don't want to lose photos,
messages, or app data.

Duet Connect turns your phone and laptop into interconnected devices using
tools already on both machines: **SSH + rsync**.

---

## Quick start

```bash
# 1. Install (Ubuntu/Debian laptop)
sudo apt install -y rsync openssh-client python3-pip
python3 -m pip install -e .

# 2. First-time setup — generates SSH keys
duetconnect setup

# 3. Copy your phone key onto the phone (one-time, password-based)
ssh-copy-id -i ~/.ssh/duetconnect/duetconnect_phone.pub \
  -p 8022 u0_a320@<phone-ip>

# 4. Verify connection
duetconnect doctor

# 5. Back up phone to your external drive
duetconnect backup
```

---

## CLI at a glance

| Command | What it does |
|---------|-------------|
| `duetconnect status` | Connection status for phone & laptop |
| `duetconnect connect phone` | Test SSH to phone |
| `duetconnect send <local> phone:<remote>` | Laptop → Phone |
| `duetconnect receive phone:<remote> <local>` | Phone → Laptop |
| `duetconnect backup [full\|selective]` | Back up phone storage to drive |
| `duetconnect sync <left> <right> [--pull\|--push]` | Two-way folder sync |
| `duetconnect battery` | Phone battery status |
| `duetconnect storage` | Phone storage usage |
| `duetconnect doctor` | Full diagnostic |
| `duetconnect setup` | Generate keys + initial config |

---

## Example: move phone data to external drive

```bash
# On the laptop
duetconnect doctor                                    # verify link
duetconnect backup                                    # full phone → GRAVITY drive
duetconnect receive ~/phone-apps.txt ./phone-backup/ # save app list
duetconnect receive ~/ACCOUNTS-REPORT.txt ./         # save accounts report
```

---

## Supported connection methods

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Same Wi-Fi │     │ Phone Hotspot│     │ USB Tethering│
│   (router)   │     │   (no router)│     │   (cable + net)│
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       └────────── SSH ─────┴────────── SSH ─────┘
                      port 8022
```

See `docs/CONNECTION-METHODS.md` for step-by-step instructions for each.

---

## Project structure

```
duet-connect/
├── duetconnect/          # Python package (CLI, SSH, transfer, backup…)
├── docs/                 # Guides: TERMUX, CONNECTION-METHODS, ARCHITECTURE…
├── scripts/              # Bash installer
├── tests/                # pytest suite
├── pyproject.toml        # Package config + CLI entry point
├── duet-connect.cfg.example
├── .github/workflows/ci.yml
└── LICENSE (MIT)
```

---

## Documentation

- [Install](INSTALL.md)
- [Termux setup](docs/TERMUX.md)
- [Connection methods](docs/CONNECTION-METHODS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Usage](docs/USAGE.md)
- [Security](SECURITY.md)
- [Contributing](CONTRIBUTING.md)

---

## License

[MIT](LICENSE)
