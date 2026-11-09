# Security Policy

## Supported versions
Only the latest release on `main` receives security fixes.

## Core security properties
- **SSH keys only**: Passwords are never stored, transmitted by Duet Connect, or used for automation.
- **ed25519 keys**: Generated per device with `ssh-keygen -t ed25519`, no passphrase (unattended use), stored in `~/.ssh/duetconnect/`.
- **Host-key validation**: `StrictHostKeyChecking=yes`; fingerprints obtained via `ssh-keyscan` and never auto-accepted blindly.
- **Batch mode**: `ssh -o BatchMode=yes` so interactive password prompts cannot block or leak.
- **Local network only**: Discovery is a ping-sweep of the configured local subnet; no ports are exposed to the public internet.
- **No deletion**: rsync runs without `--delete`; sources are never removed during backup or sync.

## Reporting
Please contact the maintainer privately before filing a public issue for security concerns.
