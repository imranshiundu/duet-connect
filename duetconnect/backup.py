"""Backup management for Duet Connect.

Full and selective phone-storage backups to a configurable external drive,
with verification, exclusion patterns, and dated generation history.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from .config import GriotLinkConfig
from .ssh import DeviceConfig, SshManager
from .transfer import RsyncTransfer, TransferSpec


class BackupError(RuntimeError):
    """Raised when a backup operation fails."""


class BackupManager:
    """Coordinate phone backups onto a local (external) destination."""

    def __init__(self, config: GriotLinkConfig, phone: DeviceConfig):
        self.config = config
        self.phone = phone
        self.transfer = RsyncTransfer(config)
        self.ssh = SshManager(config, phone)
        self.destination = config.backup_destination

    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y%m%d-%H%M%S")

    def _prune_history(self, base_name: str) -> None:
        """Keep only history_keep dated generations."""
        keep = self.config.history_keep
        if keep <= 0:
            return
        generations = sorted(
            p for p in self.destination.iterdir()
            if p.is_dir() and p.name.startswith(f"{base_name}-")
        )
        for old in generations[:-keep]:
            shutil.rmtree(old, ignore_errors=True)

    def full(self, dry_run: bool = False, verify: Optional[bool] = None) -> Tuple[int, str, str]:
        """Full backup of visible phone storage to the external drive."""
        if not self.destination.exists():
            self.destination.mkdir(parents=True, exist_ok=True)
        target = self.destination / f"full-{self._timestamp()}"
        exclude = self.config.exclude_patterns
        returncode, out, err = self.transfer.receive(
            f"{self.config.phone_storage}/", str(target) + "/",
            self.phone, dry_run=dry_run, checksum=bool(verify), exclude=exclude,
        )
        if returncode == 0 and not dry_run:
            self._prune_history("full")
        return returncode, out, err

    def selective(self, folders: Optional[List[str]] = None,
                  dry_run: bool = False, verify: Optional[bool] = None) -> Tuple[int, str, str]:
        """Back up only the configured selective folders (DCIM, Pictures, ...)."""
        folders = folders or self.config.selective_folders
        if not self.destination.exists():
            self.destination.mkdir(parents=True, exist_ok=True)
        target = self.destination / f"selective-{self._timestamp()}"
        target.mkdir(parents=True, exist_ok=True)
        exclude = self.config.exclude_patterns
        overall_rc = 0
        combined_out = []
        combined_err = []
        for folder in folders:
            remote_source = f"{self.config.phone_storage}/{folder}/"
            local_target = str(target / folder) + "/"
            rc, out, err = self.transfer.receive(
                remote_source, local_target, self.phone,
                dry_run=dry_run, checksum=bool(verify), exclude=exclude,
            )
            combined_out.append(out)
            combined_err.append(err)
            if rc != 0:
                overall_rc = rc
        if overall_rc == 0 and not dry_run:
            self._prune_history("selective")
        return overall_rc, "\n".join(combined_out), "\n".join(combined_err)

    def verify(self, backup_dir: Path) -> Tuple[bool, str]:
        """Verify a backup by re-running rsync in dry-run checksum mode."""
        if not backup_dir.exists():
            return False, f"Backup directory not found: {backup_dir}"
        # Name convention: full-TS or selective-TS -> source is phone_storage
        rc, out, err = self.transfer.receive(
            f"{self.config.phone_storage}/", str(backup_dir) + "/",
            self.phone, dry_run=True, checksum=True,
            exclude=self.config.exclude_patterns,
        )
        # In dry-run, rsync exit 0 with no file list = identical.
        identical = rc == 0 and "sent" in out and "total size is 0" in out
        return identical, out or err
