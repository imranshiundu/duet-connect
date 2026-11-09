# Duet Connect Architecture

## Overview
Duet Connect connects an Android phone running Termux with a Linux laptop over
local Wi-Fi using stateless SSH + rsync. It is deliberately lightweight:
**no daemon, no central server, no root, no hardcoded credentials.**

## Layers
```
CLI (argparse)  ->  Orchestrators (backup/transfer/remote/health)
                ->  SSH manager (keys, fingerprints, connections)
                ->  System tools: ssh, rsync, ssh-keygen, ssh-keyscan, ping
```

### Modules
| Module | Responsibility |
|--------|----------------|
| `config.py` | INI config at `~/.config/duetconnect/duetconnect.cfg`; defaults with overrides; device objects |
| `ssh.py` | ed25519 key generation, host-key validation, connection test, remote command |
| `transfer.py` | rsync wrapper; dry-run, --partial resume, progress, checksum, excludes |
| `backup.py` | Full / selective phone backups to external drive; dated generations; pruning |
| `remote.py` | Read-only inspection (battery, storage, processes) via Termux:API or shell |
| `health.py` | Status, subnet discovery, doctor diagnostics |
| `cli.py` | `duetconnect` CLI with the commands from the spec |

## Design principles
- **Stateless**: Each invocation opens its own SSH connection; nothing stays open.
- **No passwords**: Only SSH public-key auth. Keys generated with `ssh-keygen -t ed25519`.
- **No source deletion**: rsync runs without `--delete`; copies only, never removes.
- **Configurable**: Every machine-specific value (user, port, drive, subnet) is in `duetconnect.cfg`.
- **No public exposure**: SSH ports are never opened to the internet; discovery is local-subnet only.

## Security
See `SECURITY.md`. Host fingerprints are validated via `ssh-keyscan`; `BatchMode=yes` is used so
interactive password prompts never block automation.

## Limitations
- Phone IP is dynamic; `duetconnect doctor` re-discovers it each run.
- Only shared storage (`/storage/emulated/0`) is rsync-accessible; app-private data must be
  exported through its own app before a wipe.
- Termux:API commands (`termux-battery-status`) require the `termux-api` package on Android.
