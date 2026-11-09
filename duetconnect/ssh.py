"""SSH connectivity layer for Duet Connect.

Handles ed25519 key generation, host-key fingerprint validation, connection
testing, and remote command execution. Passwords are never stored or used.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

from .config import DeviceConfig, Duet ConnectConfig


class SshError(RuntimeError):
    """Raised when an SSH operation fails."""


class SshManager:
    """Manage keys, fingerprints, and SSH connections for a device."""

    def __init__(self, config: Duet ConnectConfig, device: DeviceConfig):
        self.config = config
        self.device = device
        self.device.identity_file = self.config.key_dir / f"duetconnect_{device.nickname}"

    # ---------------------------------------------------------------- keys
    def key_exists(self) -> bool:
        return self.device.identity_file.exists() and self.device.identity_file.stat().st_size > 0

    def generate_key(self, overwrite: bool = False) -> Path:
        """Generate an ed25519 key pair for this device (no passphrase)."""
        self.config.key_dir.mkdir(parents=True, exist_ok=True)
        key_path = self.device.identity_file
        if key_path.exists() and not overwrite:
            raise SshError(f"Key already exists: {key_path} (use --force to overwrite)")

        cmd = [
            "ssh-keygen", "-t", "ed25519", "-f", str(key_path),
            "-N", "", "-C", f"duetconnect-{self.device.nickname}@{self.device.user}",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=self.config.command_timeout)
        if result.returncode != 0:
            raise SshError(f"ssh-keygen failed: {result.stderr.strip()}")
        os.chmod(key_path, 0o600)
        pub = key_path.with_suffix(".pub")
        if pub.exists():
            os.chmod(pub, 0o644)
        return key_path

    def public_key(self) -> Optional[str]:
        """Return the public key text, or None if no key exists."""
        pub = self.device.identity_file.with_suffix(".pub")
        if pub.exists():
            return pub.read_text(encoding="utf-8").strip()
        return None

    # ------------------------------------------------------------- connection
    def test_connection(self) -> Tuple[bool, str]:
        """Return (ok, message) after a lightweight SSH connectivity check."""
        if not self.key_exists():
            return False, f"No SSH key for {self.device.nickname} at {self.device.identity_file}"

        if not self.device.host:
            return False, f"No host resolved for {self.device.nickname}"

        cmd = ["ssh"]
        cmd += self.device.ssh_args
        cmd += ["-o", "BatchMode=yes",
                "-o", f"ConnectTimeout={self.config.connect_timeout}",
                "-o", "StrictHostKeyChecking=yes",
                self.device.ssh_target, "echo", "duetconnect-ok"]
        result = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=self.config.connect_timeout + 5)
        if result.returncode == 0 and "duetconnect-ok" in result.stdout:
            return True, f"SSH to {self.device.nickname} ({self.device.host}) OK"
        return False, (result.stderr or result.stdout or "SSH connection failed").strip()

    def run(self, command: str, capture: bool = True) -> Tuple[int, str, str]:
        """Execute an authorized command on the remote device."""
        if not self.device.host:
            raise SshError(f"No host resolved for {self.device.nickname}")
        cmd = ["ssh"] + self.device.ssh_args
        cmd += ["-o", f"ConnectTimeout={self.config.connect_timeout}",
                self.device.ssh_target, command]
        result = subprocess.run(cmd, capture_output=capture, text=True,
                                timeout=self.config.command_timeout)
        return result.returncode, result.stdout, result.stderr

    # ---------------------------------------------------------- fingerprints
    def remote_fingerprint(self) -> Optional[str]:
        """Retrieve the remote host's public key fingerprint (SHA256)."""
        if not self.device.host:
            return None
        cmd = ["ssh-keyscan", "-p", str(self.device.port), self.device.host]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode != 0 or not result.stdout.strip():
            return None
        # ssh-keyscan output: "host port-type key..." -> take the key field
        parts = result.stdout.strip().split()
        if len(parts) >= 3:
            return parts[2]
        return None

    def install_key_interactive(self) -> str:
        """Return instructions to copy the key to the remote device manually."""
        pub = self.public_key() or ""
        return (
            f"\nSSH key for {self.device.nickname} is at {self.device.identity_file}\n"
            f"Copy the public key below into the remote device's ~/.ssh/authorized_keys:\n\n{pub}\n"
            f"Example (one-time, password-based):\n"
            f"  ssh-copy-id -i {self.device.identity_file}.pub -p {self.device.port} "
            f"{self.device.ssh_target}\n"
        )
