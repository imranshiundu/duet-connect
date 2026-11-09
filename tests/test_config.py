"""Tests for Duet Connect configuration (no network required)."""

import tempfile
from pathlib import Path

from duetconnect.config import Duet ConnectConfig, DeviceConfig


def test_defaults_loaded_when_config_missing():
    with tempfile.TemporaryDirectory() as tmp:
        cfg = Duet ConnectConfig(config_file=Path(tmp) / "nonexistent.cfg")
        assert cfg.get("devices", "phone_user") == "u0_a320"
        assert cfg.getint("devices", "phone_port") == 8022
        assert cfg.getbool("backup", "verify_after_backup") is True


def test_device_config():
    with tempfile.TemporaryDirectory() as tmp:
        cfg = Duet ConnectConfig(config_file=Path(tmp) / "nonexistent.cfg")
        phone = cfg.device("phone")
        assert phone.nickname == "phone"
        assert phone.user == "u0_a320"
        assert phone.port == 8022
        assert isinstance(phone, DeviceConfig)


def test_getlist():
    with tempfile.TemporaryDirectory() as tmp:
        cfg = Duet ConnectConfig(config_file=Path(tmp) / "nonexistent.cfg")
        folders = cfg.selective_folders
        assert "DCIM" in folders
        assert "Pictures" in folders


def test_exclude_patterns():
    with tempfile.TemporaryDirectory() as tmp:
        cfg = Duet ConnectConfig(config_file=Path(tmp) / "nonexistent.cfg")
        assert "Android/data/*" in cfg.exclude_patterns


def test_save_and_reload():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "cfg.cfg"
        cfg = Duet ConnectConfig(config_file=path)
        cfg.parser.set("devices", "phone_user", "customuser")
        cfg.save()
        cfg2 = Duet ConnectConfig(config_file=path)
        assert cfg2.get("devices", "phone_user") == "customuser"
