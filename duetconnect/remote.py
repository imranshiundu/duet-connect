"""Remote device management commands.

Uses Termux:API on the phone when available (termux-battery-status, etc.),
falling back to plain shell commands. All commands require an established
SSH key connection — no passwords.
"""

from __future__ import annotations

import json
import shutil
from typing import Tuple

from .config import DeviceConfig, GriotLinkConfig
from .ssh import SshManager, SshError


class RemoteManager:
    """Run read-only inspection and authorized commands on a device."""

    def __init__(self, config: GriotLinkConfig, device: DeviceConfig):
        self.config = config
        self.device = device
        self.ssh = SshManager(config, device)

    # ------------------------------------------------------------ phone-specific
    def battery(self) -> Tuple[int, str, str]:
        """Phone battery status via Termux:API (requires termux-api pkg)."""
        if self.device.nickname != "phone":
            return 1, "", "battery check is phone-only"
        cmd = ("termux-battery-status 2>/dev/null "
               "|| cat /sys/class/power_supply/*/capacity 2>/dev/null "
               "|| echo 'battery-info-unavailable'")
        return self.ssh.run(cmd)

    def storage(self) -> Tuple[int, str, str]:
        """Storage usage on the remote device."""
        cmd = ("df -h /storage/emulated/0 2>/dev/null "
               "|| df -h /data 2>/dev/null "
               "|| df -h /")
        return self.ssh.run(cmd)

    def connectivity(self) -> Tuple[int, str, str]:
        """Check network connectivity from the remote device."""
        cmd = ("ping -c 2 -W 3 1.1.1.1 >/dev/null 2>&1 "
               "&& echo online || echo offline")
        return self.ssh.run(cmd)

    def directories(self, path: str = "/storage/emulated/0") -> Tuple[int, str, str]:
        """List accessible directories on the remote device."""
        cmd = f"ls -lah {path} 2>/dev/null || ls -lah / 2>/dev/null"
        return self.ssh.run(cmd)

    def processes(self) -> Tuple[int, str, str]:
        """List running Termux processes on the phone."""
        cmd = "ps -A 2>/dev/null | head -50 || top -bn1 | head -30"
        return self.ssh.run(cmd)

    def sms_list(self) -> Tuple[int, str, str]:
        """List SMS messages via termux-sms-list (requires termux-api)."""
        if self.device.nickname != "phone":
            return 1, "", "sms is phone-only"
        return self.ssh.run("termux-sms-list 2>/dev/null || echo 'sms-unavailable'")

    def contacts_list(self) -> Tuple[int, str, str]:
        """List contacts via termux-contact-list (requires termux-api)."""
        if self.device.nickname != "phone":
            return 1, "", "contacts is phone-only"
        return self.ssh.run("termux-contact-list 2>/dev/null || echo 'contacts-unavailable'")

    def clipboard_get(self) -> Tuple[int, str, str]:
        """Get clipboard contents via termux-clipboard-get."""
        if self.device.nickname != "phone":
            return 1, "", "clipboard is phone-only"
        return self.ssh.run("termux-clipboard-get 2>/dev/null || echo 'clipboard-unavailable'")

    def location(self) -> Tuple[int, str, str]:
        """Get phone location via termux-location (requires termux-api)."""
        if self.device.nickname != "phone":
            return 1, "", "location is phone-only"
        return self.ssh.run("termux-location 2>/dev/null || echo 'location-unavailable'")

    # ------------------------------------------------------------ generic
    def run(self, command: str) -> Tuple[int, str, str]:
        """Execute a user-authorized shell command on the remote device."""
        return self.ssh.run(command)

    def info(self) -> Tuple[int, str, str]:
        """Basic system information from the remote device."""
        cmd = ("uname -a; echo '---'; uptime; echo '---'; "
               "df -h / 2>/dev/null | tail -1")
        return self.ssh.run(cmd)

    def laptop_info(self) -> Tuple[int, str, str]:
        """Laptop-side storage and health (run on laptop via local calls)."""
        total, used, free = shutil.disk_usage("/")
        out = (f"laptop root: total={total // (2**30)}G "
               f"used={used // (2**30)}G free={free // (2**30)}G\n")
        return 0, out, ""

    def laptop_memory(self) -> Tuple[int, str, str]:
        """Laptop memory usage."""
        with open("/proc/meminfo") as f:
            meminfo = f.read()
        lines = [l for l in meminfo.splitlines()
                 if l.startswith(("MemTotal:", "MemAvailable:", "MemFree:"))]
        return 0, "\n".join(lines) + "\n", ""
