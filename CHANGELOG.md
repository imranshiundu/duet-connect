# Changelog

## [0.1.0] — 2026-11-09

### Added
- Two-way SSH connectivity (Termux ↔ Linux) with ed25519 keys
- rsync-based send/receive/sync with dry-run, checksum, resume, progress
- Full and selective phone backups to external drive with dated generations
- Remote inspection: battery, storage, connectivity, directories, processes
- Subnet discovery for dynamic phone IPs
- CLI: status, connect, send, receive, backup, sync, battery, storage,
  doctor, disconnect, setup
- Bash installer (scripts/install.sh) + Python packaging (pip install -e .)
- Tests: test_config, test_ssh, test_transfer, test_cli
- Docs: TERMUX, CONNECTION-METHODS, ARCHITECTURE, USAGE, CLI-REFERENCE,
  TROUBLESHOOTING, ACCOUNTS-MIGRATION
- Examples: config templates (laptop, hotspot), COMMANDS.md scenarios
- MIT License, SECURITY.md, CONTRIBUTING.md, INSTALL.md, CI workflow

### Security
- ed25519 keys only — no passwords stored or transmitted
- StrictHostKeyChecking=yes with ssh-keyscan fingerprint validation
- BatchMode=yes to block interactive password prompts
- rsync without --delete — source files never deleted
- Local network only — no ports exposed to public internet

### Known limitations
- Phone IP is dynamic; doctor re-discovers each run
- Only shared storage (/storage/emulated/0) is rsync-accessible
- App-private data (WhatsApp, 2FA, banking) must be exported through its app
- Termux:API commands require termux-api package on Android
