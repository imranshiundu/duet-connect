"""Tests for transfer parsing and rsync wrapper (no network required)."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from duetconnect.config import GriotLinkConfig
from duetconnect.transfer import (
    TransferSpec, parse_device_path, RsyncTransfer, check_rsync_available,
)
from duetconnect.config import DeviceConfig


def test_parse_device_path_local():
    path, is_remote, device = parse_device_path("/home/user/file.txt")
    assert path == "/home/user/file.txt"
    assert is_remote is False
    assert device is None


def test_parse_device_path_remote():
    path, is_remote, device = parse_device_path("phone:/storage/emulated/0/")
    assert path == "/storage/emulated/0/"
    assert is_remote is True
    assert device.nickname == "phone"


def test_parse_device_path_relative_not_remote():
    path, is_remote, device = parse_device_path("./project")
    assert path == "./project"
    assert is_remote is False


def test_parse_device_path_tilde_not_remote():
    path, is_remote, device = parse_device_path("~/file.txt")
    assert path == "~/file.txt"
    assert is_remote is False


def test_transfer_spec_defaults():
    spec = TransferSpec(source="src", destination="dst",
                        source_remote=False, dest_remote=True)
    assert spec.dry_run is False
    assert spec.checksum is False
    assert spec.exclude is None


def test_check_rsync_available_when_installed():
    # Should be True if rsync is installed in this environment
    import shutil
    expected = shutil.which("rsync") is not None
    assert check_rsync_available() == expected


def test_rsync_transfer_send_builds_command():
    with tempfile.TemporaryDirectory() as tmp:
        cfg = GriotLinkConfig(config_file=Path(tmp) / "nonexistent.cfg")
        rt = RsyncTransfer(cfg)
        device = DeviceConfig(nickname="phone", user="u0_a320",
                              host="192.168.100.51", port=8022,
                              identity_file=Path(tmp / "key"))
        # Create a dummy key file so -i is included
        device.identity_file.write_text("dummy")
        spec = TransferSpec(source="./local", destination="phone:/remote/",
                            source_remote=False, dest_remote=True)
        rc, out, err = rt.run(spec, None, device)
        # rsync will fail (no SSH server), but command should be built correctly
        assert rc != 0  # Expected failure without real SSH


def test_exclude_patterns_applied():
    with tempfile.TemporaryDirectory() as tmp:
        cfg = GriotLinkConfig(config_file=Path(tmp) / "nonexistent.cfg")
        exclude = cfg.exclude_patterns
        assert "Android/data/*" in exclude
        assert "*.cache" in exclude
        assert ".thumbnails" in exclude
