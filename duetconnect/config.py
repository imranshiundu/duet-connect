"""Configuration management for Duet Connect.

All machine-specific values live in ~/.config/duetconnect/duetconnect.cfg
and are overridable. Nothing is hardcoded to a particular host, username,
or drive path.
"""

from __future__ import annotations

import configparser
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "duetconnect"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "duetconnect.cfg"
DEFAULT_KEY_DIR = Path.home() / ".ssh" / "duetconnect"

DEFAULTS: Dict[str, Dict[str, str]] = {
    "devices": {
        "phone_user": "u0_a320",
        "phone_port": "8022",
        "laptop_user": os.getenv("USER", "imran"),
        "laptop_port": "22",
        "discovery_network": "192.168.100.0/24",
    },
    "paths": {
        "phone_storage": "/storage/emulated/0",
        "backup_destination": "/run/media/imran/GRAVITY/PhoneBackup",
        "exclude": "Android/data/*,Android/obb/*,*.cache,*.tmp,.thumbnails",
    },
    "ssh": {
        "key_dir": str(DEFAULT_KEY_DIR),
        "known_hosts": str(Path.home() / ".ssh" / "known_hosts"),
        "connect_timeout": "10",
        "command_timeout": "300",
    },
    "backup": {
        "selective_folders": "DCIM,Pictures,Movies,Music,Documents,Downloads",
        "verify_after_backup": "true",
        "history_keep": "5",
    },
    "logging": {
        "level": "INFO",
        "file": str(DEFAULT_CONFIG_DIR / "duetconnect.log"),
    },
}


@dataclass
class DeviceConfig:
    """A single reachable device (phone or laptop)."""

    nickname: str
    user: str
    host: Optional[str] = None
    port: int = 22
    identity_file: Optional[Path] = None

    @property
    def ssh_target(self) -> str:
        return f"{self.user}@{self.host}" if self.host else self.user

    @property
    def ssh_args(self) -> List[str]:
        args = ["-p", str(self.port)]
        if self.identity_file:
            args += ["-i", str(self.identity_file)]
        return args


class GriotLinkConfig:
    """Load, validate, and persist Duet Connect configuration."""

    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or DEFAULT_CONFIG_FILE
        self.parser = configparser.ConfigParser()
        self._load()

    # ------------------------------------------------------------------ load
    def _load(self) -> None:
        if self.config_file.exists():
            self.parser.read(self.config_file, encoding="utf-8")
        # Backfill defaults for any missing section / key.
        for section, keys in DEFAULTS.items():
            if not self.parser.has_section(section):
                self.parser.add_section(section)
            for key, value in keys.items():
                if not self.parser.has_option(section, key):
                    self.parser.set(section, key, value)

    # ------------------------------------------------------------------ save
    def save(self) -> None:
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as handle:
            self.parser.write(handle)

    # ------------------------------------------------------------------ getters
    def get(self, section: str, key: str, fallback: Optional[str] = None) -> str:
        # Environment variable override: DUETCONNECT_<SECTION>_<KEY>
        env_key = f"DUETCONNECT_{section.upper()}_{key.upper()}"
        env_value = os.environ.get(env_key)
        if env_value is not None:
            return env_value
        return self.parser.get(section, key, fallback=fallback)

    def getint(self, section: str, key: str, fallback: int = 0) -> int:
        return self.parser.getint(section, key, fallback=fallback)

    def getbool(self, section: str, key: str, fallback: bool = False) -> bool:
        return self.parser.getboolean(section, key, fallback=fallback)

    def getlist(self, section: str, key: str, fallback: Optional[List[str]] = None) -> List[str]:
        raw = self.get(section, key, fallback="")
        if not raw:
            return fallback or []
        return [item.strip() for item in raw.split(",") if item.strip()]

    # ------------------------------------------------------------------ devices
    def device(self, nickname: str) -> DeviceConfig:
        """Build a DeviceConfig for 'phone' or 'laptop' from config."""
        prefix = nickname
        user = self.get("devices", f"{prefix}_user")
        port = self.getint("devices", f"{prefix}_port", 22)
        identity = Path(self.get("ssh", "key_dir")) / f"duetconnect_{nickname}"
        return DeviceConfig(nickname=nickname, user=user, host=None, port=port,
                            identity_file=identity)

    @property
    def backup_destination(self) -> Path:
        return Path(self.get("paths", "backup_destination"))

    @property
    def phone_storage(self) -> str:
        return self.get("paths", "phone_storage")

    @property
    def exclude_patterns(self) -> List[str]:
        return self.getlist("paths", "exclude")

    @property
    def selective_folders(self) -> List[str]:
        return self.getlist("backup", "selective_folders")

    @property
    def key_dir(self) -> Path:
        return Path(self.get("ssh", "key_dir")).expanduser()

    @property
    def known_hosts(self) -> Path:
        return Path(self.get("ssh", "known_hosts")).expanduser()

    @property
    def connect_timeout(self) -> int:
        return self.getint("ssh", "connect_timeout", 10)

    @property
    def command_timeout(self) -> int:
        return self.getint("ssh", "command_timeout", 300)

    @property
    def history_keep(self) -> int:
        return self.getint("backup", "history_keep", 5)

    @property
    def verify_after_backup(self) -> bool:
        return self.getbool("backup", "verify_after_backup", True)
