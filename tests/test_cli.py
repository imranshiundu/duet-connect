"""Tests for CLI argument parsing (no network required)."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock

from duetconnect.cli import GriotLinkCLI


def test_cli_prints_help_when_no_command():
    cli = GriotLinkCLI()
    with pytest.raises(SystemExit) as exc_info:
        cli.run(["--help"])
    assert exc_info.value.code == 0


def test_cli_status_parses():
    cli = GriotLinkCLI()
    with patch.object(type(cli.health), 'status',
                      return_value=(True, "OK")):
        rc = cli.run(["status"])
        assert rc == 0


def test_cli_send_parses_args():
    cli = GriotLinkCLI()
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
    with patch.object(type(cli.config), 'verify_after_backup',
                      new_callable=PropertyMock, return_value=True):
        with patch.object(type(cli.config), 'exclude_patterns',
                          new_callable=PropertyMock, return_value=[]):
            with patch.object(type(cli.config), 'history_keep',
                              new_callable=PropertyMock, return_value=5):
                with patch('duetconnect.backup.BackupManager') as mock_bm:
                    mock_instance = MagicMock()
                    mock_instance.selective.return_value = (0, "", "")
                    mock_bm.return_value = mock_instance
                    rc = cli.run(["backup", "selective"])
                    assert rc == 0


def test_cli_connect_setup_keys(tmp_path):
    cli = GriotLinkCLI(config_file=tmp_path / "cfg.cfg")
    assert cli is not None
    assert cli.config is not None
