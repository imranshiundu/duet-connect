# CLI Reference — `duetconnect`

## Global options

```
duetconnect [--config PATH] [--verbose] <command> [args]
```

| Option | Description |
|--------|-------------|
| `--config` | Path to config file (default: `~/.config/duetconnect/duetconnect.cfg`) |
| `--verbose` / `-v` | Verbose output |

---

## `status`

Show connection status for both devices.

```bash
duetconnect status
```

**Output:**
```
┌─────────┬─────────────────────┬──────────────────────────────────┐
│ Device  │ Host                │ Status                           │
├─────────┼─────────────────────┼──────────────────────────────────┤
│ phone   │ 192.168.100.51:8022 │ ✅ OK — SSH reachable            │
│ laptop  │ local               │ ✅ OK — storage writable         │
└─────────┴─────────────────────┴──────────────────────────────────┘
```

Exit codes: 0 = both OK, 1 = any failure.

---

## `connect <device>`

Test SSH connection to phone or laptop.

```bash
duetconnect connect phone
duetconnect connect laptop

# First-time: generate ed25519 key and show install instructions
duetconnect connect phone --setup-keys
```

**With `--setup-keys`:**
```
[OK] Key generated: /home/imran/.ssh/duetconnect/duetconnect_phone

SSH key for phone is at /home/imran/.ssh/duetconnect/duetconnect_phone
Copy the public key below into the remote device's ~/.ssh/authorized_keys:

ssh-ed25519 AAAAC3NzaC1lZDI1NTE5... imran@duetconnect-phone

Example (one-time, password-based):
  ssh-copy-id -i /home/imran/.ssh/duetconnect/duetconnect_phone.pub -p 8022 u0_a320@192.168.100.51
```

---

## `send <source> <destination>`

Copy from laptop → phone.

```bash
duetconnect send ./photo.jpg phone:~/Pictures/
duetconnect send ./project phone:~/projects/
duetconnect send ./docs phone:~/storage/documents/ --dry-run
duetconnect send ./important.pdf phone:~/Documents/ --checksum
```

| Flag | Effect |
|------|--------|
| `--dry-run` | Preview only, no changes made |
| `--checksum` | Verify files match after transfer |

Exit codes: 0 = success, 1 = failure.

---

## `receive <source> <destination>`

Copy from phone → laptop.

```bash
duetconnect receive phone:~/storage/downloads/ ./downloads/
duetconnect receive phone:~/storage/dcim/ ./dcim-backup/
duetconnect receive phone:~/storage/movies/ /run/media/imran/GRAVITY/Backup/
duetconnect receive phone:~/storage/documents/ ./docs/ --dry-run --checksum
```

| Flag | Effect |
|------|--------|
| `--dry-run` | Preview only |
| `--checksum` | Verify with checksums |

---

## `backup [mode]`

Back up phone storage to the configured external drive.

```bash
duetconnect backup              # full backup (all shared storage)
duetconnect backup selective    # only DCIM, Pictures, Movies, Music, Documents, Downloads
duetconnect backup --no-verify  # skip post-backup checksum verification
duetconnect backup --dry-run    # preview only
```

**Output folders:**
```
/run/media/imran/GRAVITY/PhoneBackup/
├── full-20261109-143022/       # timestamped generation
└── selective-20261109-143500/
```

Older generations are pruned when count exceeds `history_keep` (default 5).

---

## `sync <left> <right>`

Bidirectional directory sync.

```bash
# Pull phone Downloads → local ./downloads (default)
duetconnect sync ./downloads phone:~/storage/downloads/ --pull

# Push local project → phone
duetconnect sync ./project phone:~/projects/ --push

# Preview without changes
duetconnect sync ./project phone:~/projects/ --push --dry-run
```

| Flag | Effect |
|------|--------|
| `--pull` | Remote → local (default) |
| `--push` | Local → remote |
| `--dry-run` | Preview only |
| `--checksum` | Verify with checksums |

**Rules:** Source files are never deleted. On conflict, the pushing side wins.

---

## `battery`

Show phone battery status (requires `termux-api` on phone).

```bash
duetconnect battery
```

**Output:**
```
{"status": "charging", "percentage": 87, "health": "good", ...}
```

---

## `storage`

Show phone storage usage.

```bash
duetconnect storage
```

**Output:**
```
Filesystem      Size  Used Avail Use% Mounted on
/dev/fuse       232G  183G   49G  79% /storage/emulated
```

---

## `doctor`

Run full diagnostic.

```bash
duetconnect doctor
```

**Output:**
```
[OK] rsync found
[OK] ssh found
[OK] ssh-keygen found
[OK] ssh-keyscan found
[OK] ping found
[CONFIG] /home/imran/.config/duetconnect/duetconnect.cfg
[KEYS]   /home/imran/.ssh/duetconnect
[OK] phone: SSH to phone (192.168.100.51) OK
[OK] laptop: laptop root: total=476G used=120G free=320G
```

---

## `disconnect`

Informational — Duet Connect is stateless (no persistent connections).

```bash
duetconnect disconnect
```

**Output:**
```
GriotLink uses stateless SSH — nothing to tear down.
Close your terminal or run 'ssh -O exit -p 8022 u0_a320@<phone-ip>' to end any multiplexed session.
```

---

## `setup`

First-time setup: generate keys, create config, show pairing instructions.

```bash
duetconnect setup
```

**Output:**
```
[CONFIG] /home/imran/.config/duetconnect/duetconnect.cfg
[KEYS]   /home/imran/.ssh/duetconnect
[KEY] Generated phone key: /home/imran/.ssh/duetconnect/duetconnect_phone
[KEY] Exists   laptop: /home/imran/.ssh/duetconnect/duetconnect_laptop
SSH key for phone is at ...
[DONE] Edit ~/.config/duetconnect/duetconnect.cfg, then run 'duetconnect doctor'
```
