"""Remote device management commands.

Uses Termux:API on the phone when available (termux-battery-status, etc.),
falling back to plain shell commands. All commands require an established
SSH key connection — no passwords.
"""

from __future__ import annotations

import json
from typing import Tuple

from .config import DeviceConfig, Duet ConnectConfig
from .ssh import SshManager, SshError


class RemoteManager:
    """Run read-only inspection and authorized commands on a device."""

    def __init__(self, config: Duet ConnectConfig, device: DeviceConfig):
        self.config = config
        self.device = device
        self.ssh = SshManager(config, device)

    # ------------------------------------------------------------ phone-specific
    def battery(self) -> Tuple[int, str, str]:
        """Phone battery status via Termux:API (requires termux-api pkg)."""
        if self.device.nickname != "phone":
            return 1, "", "battery check is phone-only"
        code, out, err = self.ssh.run("termux-battery-status 2>/dev/null || cat /sys/class/power_supply/*/capacity 2>/dev/null || echo 'battery-info-unavailable'")
        return code, out, err

    def storage(self) -> Tuple[int, str, str]:
        """Storage usage on the remote device."""
        code, out, err = self.ssh.run("df -h /storage/emulated/0 2>/dev/null || df -h /data 2>/dev/null || df -h /")
        return code, out, err

    def connectivity(self) -> Tuple[int, str, str]:
        """Check network connectivity from the remote device."""
        code, out, err = self.ssh.run("ping -c 2 -W 3 1.1.1.1 >/dev/null 2>&1 && echo online || echo offline")
        return code, out, err

    def directories(self, path: str = "/storage/emulated/0") -> Tuple[int, str, str]:
        """List accessible directories on the remote device."""
        code, out, err = self.ssh.run(f"ls -lah {path} 2>/dev/null || ls -lah / 2>/dev/null")
        return code, out, err

    def processes(self) -> Tuple[int, str, str]:
        """List running Termux processes on the phone."""
        code, out, err = self.ssh.run("ps -A 2>/dev/null | head -50 || top -bn1 | head -30")
        return code, out, err

    # ------------------------------------------------------------ generic
    def run(self, command: str) -> Tuple[int, str, str]:
        """Execute a user-authorized shell command on the remote device."""
        return self.ssh.run(command)

    def info(self) -> Tuple[int, str, str]:
        """Basic system information from the remote device."""
        code, out, err = self.ssh.run(
            "uname -a; echo '---'; uptime; echo '---'; df -h / 2>/dev/null | tail -1"
        )
        return code, out, err

    def laptop_info(self) -> Tuple[int, str, str]:
        """Laptop-side storage and health (run on laptop via local calls)."""
        import shutil
        total, used, free = shutil.disk_usage("/")
        out = (f"laptop root: total={total // (2**30)}G used={used // (2**30)}G "
               f"free={free // (2**30)}G\n")
        return 0, out, ""
