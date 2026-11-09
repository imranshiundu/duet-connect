"""Connection status, discovery, and doctor diagnostics."""

from __future__ import annotations

import socket
import subprocess
from typing import List, Tuple

from .config import DeviceConfig, Duet ConnectConfig
from .ssh import SshManager


class HealthManager:
    """Diagnose the link between laptop and phone."""

    def __init__(self, config: Duet ConnectConfig):
        self.config = config

    def status(self, device: DeviceConfig) -> Tuple[bool, str]:
        """One-line connection status for a device."""
        ssh = SshManager(self.config, device)
        ok, message = ssh.test_connection()
        return ok, message

    def discover(self, network: Optional[str] = None, port: int = 8022) -> List[str]:
        """Ping-sweep the local subnet and return hosts with the port open.

        Best-effort, no root required. Returns IP strings.
        """
        network = network or self.config.get("devices", "discovery_network", "192.168.100.0/24")
        # Parse a simple /24 CIDR.
        base = network.split("/")[0]
        octets = base.split(".")
        if len(octets) != 4:
            return []
        prefix = ".".join(octets[:3])
        found: List[str] = []
        for i in range(1, 255):
            ip = f"{prefix}.{i}"
            # Quick ping first (cheap filter), then port check.
            ping = subprocess.run(["ping", "-c", "1", "-W", "300", ip],
                                  capture_output=True, timeout=2)
            if ping.returncode != 0:
                continue
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            try:
                if sock.connect_ex((ip, port)) == 0:
                    found.append(ip)
            finally:
                sock.close()
        return found

    def doctor(self, devices: List[DeviceConfig]) -> List[str]:
        """Run a full diagnostic and return human-readable findings."""
        findings: List[str] = []
        # Tool availability
        for tool in ("rsync", "ssh", "ssh-keygen", "ssh-keyscan", "ping"):
            if subprocess.run(["which", tool], capture_output=True).returncode == 0:
                findings.append(f"[OK] {tool} found")
            else:
                findings.append(f"[MISSING] {tool} not installed")
        # Config
        findings.append(f"[CONFIG] {self.config.config_file}")
        findings.append(f"[KEYS]   {self.config.key_dir}")
        # Per-device status
        for device in devices:
            ok, message = self.status(device)
            tag = "[OK]" if ok else "[FAIL]"
            findings.append(f"{tag} {device.nickname}: {message}")
        return findings
