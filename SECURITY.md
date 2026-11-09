# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.1.0 (main) | ✅ Yes |

## Core security properties

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                              │
├─────────────────────────────────────────────────────────────────┤
│  [1] Network:  Local Wi-Fi / hotspot only                       │
│              └─ SSH port 8022 never exposed to public internet  │
│                                                                  │
│  [2] Auth:     ed25519 SSH keys                                 │
│              └─ No passwords stored or transmitted              │
│              └─ BatchMode=yes blocks interactive prompts        │
│                                                                  │
│  [3] Host keys: StrictHostKeyChecking=yes                       │
│              └─ Fingerprints via ssh-keyscan, never auto-accept │
│                                                                  │
│  [4] Data:     rsync without --delete                           │
│              └─ Source files never deleted during backup/sync   │
│                                                                  │
│  [5] Config:   No hardcoded credentials                         │
│              └─ All values in duetconnect.cfg (user-editable)   │
└─────────────────────────────────────────────────────────────────┘
```

## Key management

- Keys generated with `ssh-keygen -t ed25519 -N ""` (no passphrase for unattended use)
- Stored in `~/.ssh/duetconnect/` with `600` permissions
- Public keys (`*.pub`) with `644` permissions
- One key pair per device (`duetconnect_phone`, `duetconnect_laptop`)

## What Duet Connect does NOT do

- ❌ Does not store your passwords
- ❌ Does not store your private keys remotely
- ❌ Does not open ports to the internet
- ❌ Does not delete source files during sync or backup
- ❌ Does not auto-accept unknown SSH host keys

## Reporting vulnerabilities

Please contact the maintainer privately before filing a public issue for
security concerns. Do not paste tokens, keys, or passwords in issues.

## Credentials hygiene

If you accidentally paste a token or key in a chat, issue, or commit:
1. Revoke it immediately at the provider (GitHub, Google, etc.)
2. Rotate it — treat it as compromised
3. Never commit secrets; use `duetconnect.cfg` for config only
