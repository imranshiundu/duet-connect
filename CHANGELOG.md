# Changelog

## [0.1.0] — 2026-11-09
- Initial release of Duet Connect
- Two-way SSH connectivity (phone <-> laptop) with ed25519 keys
- File transfer/sync via rsync (send, receive, sync) with dry-run, checksum, resume, progress
- Full and selective phone backups to external drive with dated generations + pruning
- Remote inspection: battery, storage, connectivity, directories, processes
- CLI: status, connect, send, receive, backup, sync, battery, storage, doctor, disconnect, setup
- Subnet discovery for dynamic phone IPs
- Bash installer + Python packaging (pip install -e .)
- Tests, docs, MIT license
