"""Tests for SSH key management and connection (no network required)."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from duetconnect.config import GriotLinkConfig
from duetconnect.ssh import SshManager, DeviceConfig, SshError


def test_key_exists_false_when_missing():
    with tempfile.TemporaryDirectory() as tmp:
        cfg = GriotLinkConfig(config_file=Path(tmp) / "nonexistent.cfg")
        device = cfg.device("phone")
        ssh = SshManager(cfg, device)
        assert ssh.key_exists() is False


def test_generate_key_creates_files():
    with tempfile.TemporaryDirectory() as tmp:
        cfg = GriotLinkConfig(config_file=Path(tmp) / "nonexistent.cfg")
        device = cfg.device("phone")
        ssh = SshManager(cfg, device)
        key_path = ssh.generate_key()
        assert key_path.exists()
        pub = key_path.with_suffix(".pub")
        assert pub.exists()
        # Check permissions
        assert oct(key_path.stat().st_mode & 0o777) == "0o600"
        assert oct(pub.stat().st_mode & 0o777) == "0o644"


def test_generate_key_overwrite_protection():
    with tempfile.TemporaryDirectory() as tmp:
        cfg = GriotLinkConfig(config_file=Path(tmp) / "nonexistent.cfg")
        device = cfg.device("phone")
        ssh = SshManager(cfg, device)
        ssh.generate_key()
        try:
            ssh.generate_key(overwrite=False)
            assert False, "Expected SshError for existing key"
        except SshError:
            pass


def test_public_key_returns_text():
    with tempfile.TemporaryDirectory() as tmp:
        cfg = GriotLinkConfig(config_file=Path(tmp) / "nonexistent.cfg")
        device = cfg.device("phone")
        ssh = SshManager(cfg, device)
        assert ssh.public_key() is None
        ssh.generate_key()
        pub = ssh.public_key()
        assert pub is not None
        assert pub.startswith("ssh-ed25519")


def test_install_key_interactive_instructions():
    with tempfile.TemporaryDirectory() as tmp:
        cfg = GriotLinkConfig(config_file=Path(tmp) / "nonexistent.cfg")
        device = cfg.device("phone")
        device.host = "192.168.100.51"
        ssh = SshManager(cfg, device)
        ssh.generate_key()
        instructions = ssh.install_key_interactive()
        assert "ssh-copy-id" in instructions
        assert "8022" in instructions
        assert "u0_a320@192.168.100.51" in instructions


def test_device_config_ssh_args():
    device = DeviceConfig(nickname="phone", user="u0_a320", host="192.168.100.51", port=8022)
    args = device.ssh_args
    assert "-p" in args
    assert "8022" in args
    assert device.ssh_target == "u0_a320@192.168.100.51"
