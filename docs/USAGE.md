# Duet Connect Usage

## First-time setup
```bash
# Install (Ubuntu/Debian)
sudo apt install -y rsync openssh-client python3-pip
python3 -m pip install --user -e .

# Generate keys + show how to copy them to the phone
duetconnect setup

# One-time: copy phone key onto the phone (password-based, run from laptop)
ssh-copy-id -i ~/.ssh/duetconnect/duetconnect_phone.pub -p 8022 u0_a320@<phone-ip>

# Verify
duetconnect doctor
```

## Connection
```bash
duetconnect status
duetconnect connect phone
duetconnect connect laptop
```

## File transfer
```bash
# Laptop -> Phone
duetconnect send ./project phone:~/projects/

# Phone -> Laptop
duetconnect receive phone:~/storage/downloads/ ./downloads/

# Dry run (preview, no changes)
duetconnect send ./project phone:~/projects/ --dry-run
```

## Backup
```bash
# Everything visible on phone storage -> external drive
duetconnect backup

# Only DCIM, Pictures, Movies, Music, Documents, Downloads
duetconnect backup selective

# Skip verification (faster)
duetconnect backup --no-verify
```

## Sync
```bash
# Pull phone Downloads into local ./downloads
duetconnect sync ./downloads phone:~/storage/downloads/ --pull

# Push local project to phone
duetconnect sync ./project phone:~/projects/ --push
```

## Inspection
```bash
duetconnect battery
duetconnect storage
duetconnect doctor
```

## Config
Edit `~/.config/duetconnect/duetconnect.cfg`:
- `phone_user`, `phone_port` (default `u0_a320`, `8022`)
- `backup_destination` (your external drive mount point)
- `discovery_network` (your Wi-Fi subnet for `doctor`)
- `exclude` (patterns skipped during backup/sync)
