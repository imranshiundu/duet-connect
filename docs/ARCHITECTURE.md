# Duet Connect Architecture

## System overview

```mermaid
flowchart TD
    subgraph Phone["Android Phone (Termux)"]
        direction TB
        A[Termux shell<br/>bash / zsh] --> B[sshd<br/>port 8022]
        B --> C[Shared storage<br/>/storage/emulated/0]
        D[termux-api<br/>battery, storage] --> B
        E[Android filesystem] --> C
    end

    subgraph Laptop["Linux Laptop (Ubuntu)"]
        direction TB
        F[duetconnect CLI<br/>Python entry point] --> G[SSH client]
        G --> H[rsync over SSH]
        I[External drive<br/>GRAVITY / mount point] --> H
    end

    B <==>|Wi-Fi / hotspot /<br>USB tethering / ADB| G
    C -->|pull / receive| H
    H -->|push / send| C
```

## Module map

```mermaid
graph LR
    subgraph CLI["CLI layer (argparse)"]
        C1[status] --> C2[connect]
        C2 --> C3[send / receive]
        C3 --> C4[backup]
        C4 --> C5[sync]
        C5 --> C6[battery / storage / doctor]
    end

    subgraph Core["Core orchestrators"]
        M1[config.py] --> M2[ssh.py]
        M2 --> M3[transfer.py]
        M3 --> M4[backup.py]
        M4 --> M5[remote.py]
        M5 --> M6[health.py]
    end

    subgraph System["System tools (no reinvention)"]
        S1[ssh / ssh-keygen / ssh-keyscan]
        S2[rsync --partial --progress]
        S3[ping / ssh-keyscan]
        S4[termux-api (optional)]
    end

    CLI --> Core
    Core --> System
```

## Data flow — backup (phone → laptop external drive)

```mermaid
sequenceDiagram
    participant L as Laptop (duetconnect)
    participant S as SSH (port 8022)
    participant P as Phone (Termux)
    participant D as External drive (GRAVITY)

    L->>S: ssh -p 8022 u0_a320@phone-ip
    S->>P: authenticate ed25519 key
    P->>S: stream /storage/emulated/0/
    S->>L: rsync data
    L->>D: write to /run/media/.../PhoneBackup/
    L->>L: verify (--checksum dry-run)
    L->>L: prune old generations (> history_keep)
```

## Data flow — sync (bidirectional)

```mermaid
sequenceDiagram
    participant L as Laptop
    participant P as Phone

    L->>P: rsync --dry-run --checksum
    P-->>L: list differing files
    L->>L: conflict detection (no --delete)
    L->>P: push changed files only
    P->>L: pull changed files only
```

## Security boundary

```mermaid
flowchart LR
    A[Public Internet] -.->|BLOCKED| B[(SSH port 8022)]
    B --> C[Local Wi-Fi only]
    C --> D[ed25519 key auth]
    D --> E[BatchMode=yes<br/>no passwords]
    E --> F[StrictHostKeyChecking=yes]
    F --> G[rsync without --delete<br/>sources never deleted]
```

## Design principles

| Principle | How it's implemented |
|-----------|---------------------|
| **No root on Android** | Uses Termux user space; `sshd` runs as unprivileged app user |
| **Stateless** | Each CLI call opens its own SSH connection; nothing stays open |
| **No passwords** | ed25519 keys only; `BatchMode=yes` blocks interactive prompts |
| **No source deletion** | rsync invoked without `--delete`; copies only, never removes |
| **Configurable** | Every machine-specific value in `duetconnect.cfg` (users, ports, drive, subnet) |
| **Standard tools** | Built on ssh, rsync, ssh-keygen, ping — no heavy frameworks |

## Limitations

- Phone IP is dynamic — `duetconnect doctor` re-discovers it each run
- Only shared storage (`/storage/emulated/0`) is rsync-accessible. App-private data
  (WhatsApp databases, video vaults, download manager caches) must be exported
  through the app itself before a factory reset
- Termux:API commands (`termux-battery-status`) require the `termux-api` package

---

**Next:** [Usage examples →](USAGE.md)
