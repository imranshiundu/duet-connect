# Duet Connect — Real-World Command Examples

## Scenario 1: First-time setup (phone → laptop pairing)

```bash
# Laptop: generate keys
duetconnect setup

# Laptop: copy key to phone (enter phone's SSH password)
ssh-copy-id -i ~/.ssh/duetconnect/duetconnect_phone.pub \
  -p 8022 u0_a320@192.168.100.51

# Laptop: verify
duetconnect doctor
```

## Scenario 2: Back up entire phone to external drive

```bash
duetconnect backup
# → Creates /run/media/imran/GRAVITY/PhoneBackup/full-YYYYMMDD-HHMMSS/
```

## Scenario 3: Back up only photos and documents

```bash
duetconnect backup selective
# → Backs up DCIM, Pictures, Movies, Music, Documents, Downloads
```

## Scenario 4: Pull phone Downloads to laptop

```bash
duetconnect receive phone:~/storage/downloads/ ./phone-downloads/
```

## Scenario 5: Push laptop project to phone

```bash
duetconnect send ./my-app phone:~/projects/my-app/
```

## Scenario 6: Two-way sync (laptop → phone)

```bash
duetconnect sync ./docs phone:~/storage/documents/ --push
```

## Scenario 7: Two-way sync (phone → laptop)

```bash
duetconnect sync ./phone-docs phone:~/storage/documents/ --pull
```

## Scenario 8: Preview changes before making them (dry-run)

```bash
duetconnect send ./important phone:~/docs/ --dry-run --checksum
```

## Scenario 9: Check phone battery before long transfer

```bash
duetconnect battery
# → {"status": "charging", "percentage": 92, ...}
```

## Scenario 10: Full diagnostic when connection fails

```bash
duetconnect doctor
# → Shows all checks: tools, config, keys, phone SSH, laptop health
```

## Scenario 11: Using phone hotspot (no router)

```bash
# Phone: turn on Wi-Fi hotspot
# Laptop: join hotspot Wi-Fi
# Laptop: update config for 192.168.43.0/24 subnet
duetconnect doctor
duetconnect backup
```

## Scenario 12: Resume interrupted transfer

```bash
# If Wi-Fi drops mid-transfer, just rerun the same command
duetconnect receive phone:~/storage/movies/ /run/media/imran/GRAVITY/Backup/movies/
# --partial is always on: already-copied files are skipped
```
