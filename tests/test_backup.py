"""Tests for backup manager (no network required)."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from duetconnect.config import GriotLinkConfig
from duetconnect.backup import BackupManager
from duetconnect.config import DeviceConfig


def test_backup_manager_init():
    with tempfile.TemporaryDirectory() as tmp:
        cfg = GriotLinkConfig(config_file=Path(tmp) / "nonexistent.cfg")
        phone = cfg.device("phone")
        phone.host = "192.168.100.51"
        mgr = BackupManager(cfg, phone)
        assert mgr.config is cfg
        assert mgr.phone is phone


def test_timestamp_format():
    with tempfile.TemporaryDirectory() as tmp:
        cfg = GriotLinkConfig(config_file=Path(tmp) / "nonexistent.cfg")
        phone = cfg.device("phone")
        mgr = BackupManager(cfg, phone)
        ts = mgr._timestamp()
        # Format: YYYYMMDD-HHMMSS
        assert len(ts) == 15
        assert ts[8] == "-"


def test_prune_history_keeps_only_configured_count():
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "backup"
        dest.mkdir()
        cfg = GriotLinkConfig(config_file=Path(tmp) / "nonexistent.cfg")
        cfg.parser.set("backup", "history_keep", "3")
        phone = cfg.device("phone")
        mgr = BackupManager(cfg, phone)
        mgr.destination = dest

        # Create 7 fake generations
        for i in range(7):
            (dest / f"full-20261109-{i:06d}").mkdir()

        mgr._prune_history("full")
        remaining = sorted(p.name for p in dest.iterdir()
                           if p.is_dir() and p.name.startswith("full-"))
        assert len(remaining) == 3
        # Should keep the newest 3
        assert remaining == ["full-20261109-000004",
                             "full-20261109-000005",
                             "full-20261109-000006"]


def test_prune_history_zero_keeps_all():
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "backup"
        dest.mkdir()
        cfg = GriotLinkConfig(config_file=Path(tmp) / "nonexistent.cfg")
        cfg.parser.set("backup", "history_keep", "0")
        phone = cfg.device("phone")
        mgr = BackupManager(cfg, phone)
        mgr.destination = dest

        for i in range(3):
            (dest / f"selective-20261109-{i:06d}").mkdir()

        mgr._prune_history("selective")
        remaining = list(dest.iterdir())
        assert len(remaining) == 3


def test_selective_backup_default_folders():
    with tempfile.TemporaryDirectory() as tmp:
        cfg = GriotLinkConfig(config_file=Path(tmp) / "nonexistent.cfg")
        phone = cfg.device("phone")
        folders = cfg.selective_folders
        assert "DCIM" in folders
        assert "Pictures" in folders
        assert "Movies" in folders
        assert "Music" in folders
        assert "Documents" in folders
        assert "Downloads" in folders


def test_verify_returns_false_for_missing_dir():
    with tempfile.TemporaryDirectory() as tmp:
        cfg = GriotLinkConfig(config_file=Path(tmp) / "nonexistent.cfg")
        phone = cfg.device("phone")
        mgr = BackupManager(cfg, phone)
        missing = Path(tmp) / "does-not-exist"
        ok, msg = mgr.verify(missing)
        assert ok is False
        assert "not found" in msg
