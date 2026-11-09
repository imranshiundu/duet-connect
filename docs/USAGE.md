# Duet Connect — Usage Guide

All commands run from your laptop (`Griot`) unless noted.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DUET CONNECT CLI                             │
├─────────────────────────────────────────────────────────────────────┤
│  duetconnect status         → Check phone & laptop connection       │
│  duetconnect connect phone  → Test SSH to phone                     │
│  duetconnect send …         → Laptop → Phone                        │
│  duetconnect receive …      → Phone → Laptop                        │
│  duetconnect backup         → Back up phone to external drive       │
│  duetconnect sync …         → Two-way folder sync                   │
│  duetconnect battery        → Phone battery status                  │
│  duetconnect storage        → Phone storage usage                   │
│  duetconnect doctor         → Full connection diagnostic            │
│  duetconnect setup          → First-time keys & config              │
│  duetconnect disconnect     → Info on ending SSH sessions           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. First-time setup

```bash
# On the laptop
griotlink setup   # or: duet-connect

# Generates ed25519 keys for phone + laptop
# Shows the public key to copy onto the phone

# One-time: copy your phone key onto the phone
ssh-copy-id -i ~/.ssh/duetconnect/duetconnect_phone.pub \
  -p 8022 u0_a320@<phone-ip>

# Verify everything works
duetconnect doctor
```

**Expected `doctor` output:**
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

## 2. Connection status

```bash
duetconnect status
```

```
┌─────────┬─────────────────────┬──────────────────────────────────┐
│ Device  │ Host                │ Status                           │
├─────────┼─────────────────────┼──────────────────────────────────┤
│ phone   │ 192.168.100.51:8022 │ ✅ OK — SSH reachable            │
│ laptop  │ local               │ ✅ OK — storage writable         │
└─────────┴─────────────────────┴──────────────────────────────────┘
```

If phone shows FAIL, run `duetconnect connect phone --setup-keys` then copy the key to the phone.

---

## 3. File transfer — laptop → phone (`send`)

```bash
# Send a single file
duetconnect send ./vacation-photo.jpg phone:~/Pictures/

# Send a folder
duetconnect send ./my-project phone:~/projects/

# Dry run — preview what would happen, no changes
duetconnect send ./my-project phone:~/projects/ --dry-run

# Verify files match after transfer (checksums)
duetconnect send ./important.pdf phone:~/Documents/ --checksum
```

**Dry-run output example:**
```
[DRY-RUN] sending incremental file list
vacation-photo.jpg
       2.4M 100%    2.40MB/s    0:00:01
sent 2.4M bytes  received 42 bytes  4.8M bytes/sec
total size is 2.4M  speedup is 1.00
[DRY-RUN] No changes were made (dry-run mode)
```

> ⚠️ `send` never deletes files on the phone. It only adds or updates.

---

## 4. File transfer — phone → laptop (`receive`)

```bash
# Pull phone Downloads to laptop
duetconnect receive phone:~/storage/downloads/ ./downloads/

# Pull DCIM (camera photos)
duetconnect receive phone:~/storage/dcim/ ./dcim-backup/

# Pull Movies folder to external drive
duetconnect receive phone:~/storage/movies/ \
  /run/media/imran/GRAVITY/PhoneBackup/movies/

# Dry run + checksum verification
duetconnect receive phone:~/storage/documents/ ./docs-backup/ \
  --dry-run --checksum
```

---

## 5. Two-way folder sync (`sync`)

```bash
# Pull phone Downloads into local ./downloads (default direction)
duetconnect sync ./downloads phone:~/storage/downloads/ --pull

# Push local project to phone
duetconnect sync ./project phone:~/projects/ --push

# Preview sync without making changes
duetconnect sync ./project phone:~/projects/ --push --dry-run
```

**Sync rules:**
- Files only flow one direction per command (choose `--pull` or `--push`)
- Source files are **never deleted** (no `--delete` ever used)
- Conflicts: if both sides changed, laptop version wins on push, phone version wins on pull — you're warned before overwrite

---

## 6. Backups (`backup`)

### Full backup — everything visible on phone storage

```bash
duetconnect backup
```

This copies `/storage/emulated/0/` (Movies, DCIM, Download, Pictures, etc.) to your external drive:

```
/run/media/imran/GRAVITY/PhoneBackup/
└── full-20261109-143022/
    ├── DCIM/
    ├── Download/
    ├── Movies/
    ├── Pictures/
    └── ... (all shared folders)
```

### Selective backup — only key folders

```bash
duetconnect backup selective
```

Backs up only: `DCIM, Pictures, Movies, Music, Documents, Downloads`

### Skip verification (faster, less thorough)

```bash
duetconnect backup --no-verify
```

**Backup lifecycle:**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   full-…001 │───▶│   full-…002 │───▶│   full-…003 │
└─────────────┘    └─────────────┘    └─────────────┘
     │                  │                  │
oldest              middle             newest
   │                       ▲
   └── pruned when > history_keep (default 5)
```

---

## 7. Device inspection

```bash
duetconnect battery
# → {"status": "charging", "percentage": 87, ...}

duetconnect storage
# → Filesystem      Size  Used Avail Use% Mounted on
#     /dev/fuse      232G  183G   49G  79% /storage/emulated

duetconnect doctor
# → Runs all checks: tools, config, keys, phone SSH, laptop health
```

---

## 8. Configuration file

Edit `~/.config/duetconnect/duetconnect.cfg`:

```ini
[devices]
phone_user = u0_a320
phone_port = 8022
laptop_user = imran
laptop_port = 22
discovery_network = 192.168.100.0/24

[paths]
phone_storage = /storage/emulated/0
backup_destination = /run/media/imran/GRAVITY/PhoneBackup
exclude = Android/data/*,Android/obb/*,*.cache,*.tmp,*.thumbnails

[ssh]
key_dir = ~/.ssh/duetconnect
known_hosts = ~/.ssh/known_hosts
connect_timeout = 10
command_timeout = 300

[backup]
selective_folders = DCIM,Pictures,Movies,Music,Documents,Downloads
verify_after_backup = true
history_keep = 5

[logging]
level = INFO
file = ~/.config/duetconnect/duetconnect.log
```

---

## 9. Real-world scenario: moving phone data before giving it away

```bash
# Step 1: Verify connection
duetconnect doctor

# Step 2: Back up everything to external drive
duetconnect backup

# Step 3: Also save your Termux home (scripts, settings)
duetconnect receive /data/data/com.termux/files/home/ \
  /run/media/imran/GRAVITY/PhoneBackup/termux-home/

# Step 4: Save app list + accounts report (generated on phone)
duetconnect receive ~/phone-apps.txt \
  /run/media/imran/GRAVITY/PhoneBackup/
duetconnect receive ~/ACCOUNTS-REPORT.txt \
  /run/media/imran/GRAVITY/PhoneBackup/

# Step 5: Verify the copy
duetconnect receive phone:/storage/emulated/0/ \
  /run/media/imran/GRAVITY/PhoneBackup/ --dry-run --checksum

# Step 6: On the phone — remove accounts, turn off Find My Device, factory reset
```

---

**Next:** [CLI reference →](CLI-REFERENCE.md)
