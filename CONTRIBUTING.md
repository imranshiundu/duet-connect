# Contributing to Duet Connect

Thanks for helping! Duet Connect is a small, focused toolkit. Keep it that way.

## How to contribute
1. Fork the repo and create a feature branch: `git checkout -b feature/your-idea`
2. Make your change, add or update tests under `tests/`
3. Run the test suite: `python3 -m pytest tests/`
4. Lint/format: `flake8 duetconnect tests` and `black duetconnect tests`
5. Open a pull request with a clear description

## Guidelines
- No new heavy dependencies. Prefer Bash + Python stdlib + system tools (ssh, rsync).
- Never hardcode credentials or machine-specific values.
- Every user-facing command should have a `--dry-run` where it mutates data.
- Confirm destructive operations (there are none by design — rsync never deletes sources).

## Code style
- Python 3.8+, type hints, docstrings on public functions.
- Follow PEP 8; 100-char line limit.
