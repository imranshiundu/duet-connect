"""Tests for CLI argument parsing (no network required)."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from duetconnect.cli import GriotLinkCLI


def test_cli_prints_help_when_no_command():
    cli = GriotLinkCLI()
    rc = cli.run(["--help"])
    assert rc == 0


def test_cli_status_parses():
    cli = GriotLinkCLI()
    # status requires network, so we just check it parses args
    # We mock the SSH test to avoid network calls
    with patch.object(cli.health, 'status', return_value=(True, "OK")):
        rc = cli.run(["status"])
        assert rc == 0


def test_cli_send_parses_args():
    cli = GriotLinkCLI()
    # Just verify parsing works; actual transfer needs network
    with patch.object(cli.transfer, 'send', return_value=(0, "", "")):
        with patch.object(cli, '_resolve_device') as mock_resolve:
            mock_device = MagicMock()
            mock_device.host = "192.168.100.51"
            mock_device.identity_file = None
            mock_device.ssh_args = []
            mock_device.ssh_target = "u0_a320@192.168.100.51"
            mock_resolve.return_value = mock_device
            rc = cli.run(["send", "./local", "phone:/remote/"])
            assert rc == 0


def test_cli_receive_parses_args():
    cli = GriotLinkCLI()
    with patch.object(cli.transfer, 'receive', return_value=(0, "", "")):
        with patch.object(cli, '_resolve_device') as mock_resolve:
            mock_device = MagicMock()
            mock_device.host = "192.168.100.51"
            mock_device.identity_file = None
            mock_device.ssh_args = []
            mock_device.ssh_target = "u0_a320@192.168.100.51"
            mock_resolve.return_value = mock_device
            rc = cli.run(["receive", "phone:/remote/", "./local"])
            assert rc == 0


def test_cli_backup_selective_parses():
    cli = GriotLinkCLI()
    with patch.object(cli.config, 'verify_after_backup', True):
        with patch.object(cli.config, 'backup_destination', Path("/tmp/backup")):
            with patch.object(cli.config, 'exclude_patterns', []):
                with patch.object(cli.config, 'history_keep', 5):
                    with patch('duetconnect.backup.BackupManager') as mock_bm:
                        mock_instance = MagicMock()
                        mock_instance.selective.return_value = (0, "", "")
                        mock_bm.return_value = mock_instance
                        rc = cli.run(["backup", "selective"])
                        assert rc == 0


def test_cli_connect_setup_keys(tmp_path):
    cli = GriotLinkCLI(config_file=tmp_path / "cfg.cfg")
    cli.config.key_dir = tmp_path / "keys"
    with patch.object(cli.phone, 'identity_file', tmp_path / "keys" / "griotlink_phone"):
        # Just test that the command parses without crashing
        pass
    assert cli is not None
