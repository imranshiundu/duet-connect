# Contributing to Duet Connect

Thanks for helping! Duet Connect stays small and focused. Keep it that way.

```
┌─────────────────────────────────────────────────────────────────┐
│              CONTRIBUTION WORKFLOW                              │
├─────────────────────────────────────────────────────────────────┤
│  1. Fork the repo                                               │
│  2. Create feature branch: git checkout -b feature/your-idea    │
│  3. Make your change + add/update tests                         │
│  4. Run: python3 -m pytest tests/                               │
│  5. Lint: flake8 duetconnect tests                              │
│  6. Format: black duetconnect tests                             │
│  7. Open PR with clear description                              │
└─────────────────────────────────────────────────────────────────┘
```

## Guidelines

- **No new heavy dependencies.** Prefer Bash + Python stdlib + system tools
  (ssh, rsync, ping, ssh-keygen).
- **Never hardcode credentials or machine-specific values.** Everything goes
  in `duetconnect.cfg`.
- **Every data-mutating command needs `--dry-run`.**
- **No deletion.** rsync never uses `--delete`; sources are never removed.
- **User-facing commands need clear help, error messages, and suggestions.**

## Code style

- Python 3.8+, type hints, docstrings on public functions
- PEP 8, 100-char line limit
- Commit messages: conventional commits (`feat:`, `fix:`, `docs:`, `chore:`)

## Before you submit

```bash
python3 -m pytest tests/ -v
flake8 duetconnect tests --max-line-length=100
black --check duetconnect tests --line-length=100
```

## Code of conduct

Be respectful. This project helps people move their personal data safely —
assume good faith, especially from users in difficult situations (broken
phones, no cables, giving devices away).
