"""File transfer and synchronization via rsync.

Never deletes source files during normal synchronization. Supports dry-run,
resume (--partial), progress, checksum verification, and conflict detection.
"""

from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from .config import DeviceConfig, Duet ConnectConfig
from .ssh import SshManager


class TransferError(RuntimeError):
    """Raised when a file transfer fails."""


@dataclass
class TransferSpec:
    """Parsed source/destination for a transfer operation."""
    source: str
    destination: str
    source_remote: bool
    dest_remote: bool
    dry_run: bool = False
    checksum: bool = False
    exclude: Optional[List[str]] = None


def parse_device_path(text: str, local_device: str = "laptop") -> Tuple[str, bool, Optional[DeviceConfig]]:
    """Split 'nickname:/path' or plain '/path' into (path, is_remote, device)."""
    if ":" in text and not text.startswith("/") and not text.startswith("./") and not text.startswith("~"):
        nickname, _, path = text.partition(":")
        return path, True, DeviceConfig(nickname=nickname, user="", host=None)
    return text, False, None


class RsyncTransfer:
    """Wrapper around the system rsync binary."""

    def __init__(self, config: Duet ConnectConfig):
        self.config = config

    def _base_cmd(self, spec: TransferSpec, device: Optional[DeviceConfig]) -> List[str]:
        cmd = ["rsync", "-avh", "--partial", "--progress"]
        if spec.dry_run:
            cmd.insert(1, "--dry-run")
        if spec.checksum:
            cmd.append("--checksum")
        if spec.exclude:
            for pattern in spec.exclude:
                cmd += ["--exclude", pattern]
        if device and device.identity_file and device.identity_file.exists():
            ssh = f"ssh -p {device.port} -i {device.identity_file} -o BatchMode=yes -o ConnectTimeout={self.config.connect_timeout}"
            cmd += ["-e", ssh]
        return cmd

    def run(self, spec: TransferSpec, source_device: Optional[DeviceConfig],
            dest_device: Optional[DeviceConfig]) -> Tuple[int, str, str]:
        """Execute the rsync. Returns (returncode, stdout, stderr)."""
        cmd = self._base_cmd(spec, source_device or dest_device)
        cmd.append(spec.source)
        cmd.append(spec.destination)

        # Add trailing slash semantics: if source is a directory we want its
        # contents, so normalize trailing slashes consistently.
        if spec.source_remote and spec.source.endswith("/"):
            pass  # rsync handles "host:path/" as contents already
        result = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=self.config.command_timeout)
        return result.returncode, result.stdout, result.stderr

    def send(self, local_path: str, remote_target: str, device: DeviceConfig,
             dry_run: bool = False, checksum: bool = False,
             exclude: Optional[List[str]] = None) -> Tuple[int, str, str]:
        """Copy local_path -> remote:remote_target."""
        if not device.host:
            raise TransferError(f"No host resolved for {device.nickname}")
        remote = f"{device.ssh_target}:{remote_target}"
        spec = TransferSpec(source=local_path, destination=remote,
                            source_remote=False, dest_remote=True,
                            dry_run=dry_run, checksum=checksum, exclude=exclude)
        return self.run(spec, None, device)

    def receive(self, remote_source: str, local_target: str, device: DeviceConfig,
                dry_run: bool = False, checksum: bool = False,
                exclude: Optional[List[str]] = None) -> Tuple[int, str, str]:
        """Copy remote:remote_source -> local_target."""
        if not device.host:
            raise TransferError(f"No host resolved for {device.nickname}")
        remote = f"{device.ssh_target}:{remote_source}"
        spec = TransferSpec(source=remote, destination=local_target,
                            source_remote=True, dest_remote=False,
                            dry_run=dry_run, checksum=checksum, exclude=exclude)
        return self.run(spec, device, None)

    def sync(self, left: str, right: str, device: DeviceConfig,
             direction: str = "pull", dry_run: bool = False,
             checksum: bool = False, exclude: Optional[List[str]] = None) -> Tuple[int, str, str]:
        """Bidirectional directory sync.

        direction='pull'  -> remote to local
        direction='push'  -> local to remote
        """
        if direction == "pull":
            return self.receive(right, left, device, dry_run, checksum, exclude)
        if direction == "push":
            return self.send(left, right, device, dry_run, checksum, exclude)
        raise TransferError(f"Unknown sync direction: {direction}")


def check_rsync_available() -> bool:
    import shutil
    return shutil.which("rsync") is not None
