# Duet Connect

**Connect your devices. Own your infrastructure.**

A two-way Android (Termux) ↔ Linux connectivity toolkit: SSH connectivity,
file transfer/synchronization via rsync, encrypted backups to external drives,
remote device inspection, and developer utilities — all over local Wi-Fi,
without root, without a cloud, without hardcoded credentials.

```
duetconnect status
duetconnect connect phone
duetconnect send ./project phone:~/projects/
duetconnect receive phone:~/storage/downloads/ ./downloads/
duetconnect backup
duetconnect battery
duetconnect doctor
```

## Why
When you need to move a phone's data off the device (cables failing, no SD card,
giving the phone away), you need a reliable wireless path that:
- resumes interrupted transfers (rsync `--partial`)
- never deletes your source files
- works without root on Android
- keeps you in control of where the data lands

Duet Connect is built for exactly that, plus ongoing two-way device management.

## Features
- **Two-way SSH** — laptop → phone and phone → laptop, ed25519 keys, no passwords
- **Dynamic IP handling** — subnet discovery finds your phone on Wi-Fi
- **File transfer** — `send` / `receive` with dry-run, checksum, resume, progress
- **Directory sync** — bidirectional `sync`, never deletes sources
- **Backups** — full or selective (DCIM, Pictures, Movies, Music, Documents, Downloads)
  to an external drive, with dated generations and pruning
- **Remote inspection** — battery, storage, connectivity, directories, processes
- **CLI** — one command: `duetconnect`

## Install
See [INSTALL.md](INSTALL.md).

## Docs
- [Usage](docs/USAGE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Security](SECURITY.md)
- [Contributing](CONTRIBUTING.md)

## License
[MIT](LICENSE)
