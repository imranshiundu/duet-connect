"""Duet Connect command-line interface.

Commands:
    duetconnect status
    duetconnect connect phone        (alias: connect laptop)
    duetconnect send ./project phone:~/projects/
    duetconnect receive phone:~/storage/downloads/ ./downloads/
    duetconnect backup               (full | selective)
    duetconnect sync <left> <right>  [--pull|--push]
    duetconnect battery
    duetconnect storage
    duetconnect doctor
    duetconnect disconnect
    duetconnect setup                (generate keys + show install instructions)
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional, Tuple

from .config import DEFAULT_CONFIG_FILE, DeviceConfig, Duet ConnectConfig
from .health import HealthManager
from .remote import RemoteManager
from .ssh import SshManager, SshError
from .transfer import RsyncTransfer, TransferSpec, parse_device_path
from .backup import BackupManager


class Duet ConnectCLI:
    def __init__(self, config_file=None):
        self.config = Duet ConnectConfig(config_file)
        self.health = HealthManager(self.config)
        self.transfer = RsyncTransfer(self.config)
        self.phone = self.config.device("phone")
        self.laptop = self.config.device("laptop")

    # ------------------------------------------------------------------ run
    def run(self, argv: Optional[List[str]] = None) -> int:
        parser = self._build_parser()
        args = parser.parse_args(argv)
        if not getattr(args, "cmd", None):
            parser.print_help()
            return 1
        return args.func(args, self)

    # ---------------------------------------------------------------- parser
    def _build_parser(self) -> argparse.ArgumentParser:
        p = argparse.ArgumentParser(
            prog="duetconnect",
            description="Two-way Android (Termux) <-> Linux connectivity toolkit.",
        )
        p.add_argument("--config", default=str(DEFAULT_CONFIG_FILE),
                       help="Path to duetconnect.cfg")
        p.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
        sub = p.add_subparsers(dest="cmd", required=True)

        # status
        sub.add_parser("status", help="Show connection status for both devices")

        # connect
        connect = sub.add_parser("connect", help="Test/establish SSH to a device")
        connect.add_argument("device", choices=["phone", "laptop"])
        connect.add_argument("--setup-keys", action="store_true",
                             help="Generate ed25519 key and show install steps")
        connect.set_defaults(func=self._cmd_connect)

        # send
        send = sub.add_parser("send", help="Copy LOCAL -> REMOTE (device:path)")
        send.add_argument("source")
        send.add_argument("destination")
        send.add_argument("--dry-run", action="store_true")
        send.add_argument("--checksum", action="store_true")
        send.set_defaults(func=self._cmd_send)

        # receive
        receive = sub.add_parser("receive", help="Copy REMOTE -> LOCAL (device:path)")
        receive.add_argument("source")
        receive.add_argument("destination")
        receive.add_argument("--dry-run", action="store_true")
        receive.add_argument("--checksum", action="store_true")
        receive.set_defaults(func=self._cmd_receive)

        # backup
        backup = sub.add_parser("backup", help="Back up phone storage")
        backup.add_argument("mode", choices=["full", "selective"], nargs="?", default="full")
        backup.add_argument("--dry-run", action="store_true")
        backup.add_argument("--no-verify", action="store_true")
        backup.set_defaults(func=self._cmd_backup)

        # sync
        sync = sub.add_parser("sync", help="Bidirectional directory sync")
        sync.add_argument("left")
        sync.add_argument("right")
        sync.add_argument("--pull", action="store_true", help="remote -> local (default)")
        sync.add_argument("--push", action="store_true", help="local -> remote")
        sync.add_argument("--dry-run", action="store_true")
        sync.add_argument("--checksum", action="store_true")
        sync.set_defaults(func=self._cmd_sync)

        # battery / storage
        sub.add_parser("battery", help="Phone battery status").set_defaults(func=self._cmd_battery)
        sub.add_parser("storage", help="Storage usage").set_defaults(func=self._cmd_storage)

        # doctor / disconnect / setup
        sub.add_parser("doctor", help="Run diagnostics").set_defaults(func=self._cmd_doctor)
        sub.add_parser("disconnect", help="Informational disconnect hint").set_defaults(func=self._cmd_disconnect)
        sub.add_parser("setup", help="First-time setup: keys + config").set_defaults(func=self._cmd_setup)
        return p

    # ---------------------------------------------------------------- commands
    def _cmd_connect(self, args, cli) -> int:
        device = cli.phone if args.device == "phone" else cli.laptop
        ssh = SshManager(cli.config, device)
        if args.setup_keys:
            try:
                ssh.generate_key()
                print(f"[OK] Key generated: {device.identity_file}")
            except SshError as exc:
                print(f"[ERR] {exc}")
                return 1
            print(ssh.install_key_interactive())
            return 0
        ok, message = ssh.test_connection()
        print(f"{'[OK]' if ok else '[FAIL]'} {message}")
        if not ok:
            print(ssh.install_key_interactive())
            return 1
        return 0

    def _cmd_send(self, args, cli) -> int:
        source, src_remote, src_dev = parse_device_path(args.source)
        dest, dst_remote, dst_dev = parse_device_path(args.destination)
        if src_remote and dst_remote:
            print("[ERR] send requires a local source; use sync for remote-to-remote")
            return 1
        if not dst_remote:
            print("[ERR] destination must be device:path (e.g. phone:~/projects/)")
            return 1
        device = dst_dev or cli.phone
        device.host = self._resolve(device.nickname)
        rc, out, err = cli.transfer.send(
            source, dest, device,
            dry_run=args.dry_run, checksum=args.checksum,
            exclude=cli.config.exclude_patterns,
        )
        print(out, end="")
        if err:
            print(err, file=sys.stderr, end="")
        return rc

    def _cmd_receive(self, args, cli) -> int:
        source, src_remote, src_dev = parse_device_path(args.source)
        dest, dst_remote, dst_dev = parse_device_path(args.destination)
        if not src_remote:
            print("[ERR] source must be device:path (e.g. phone:~/storage/downloads/)")
            return 1
        if dst_remote:
            print("[ERR] receive requires a local destination")
            return 1
        device = src_dev or cli.phone
        device.host = self._resolve(device.nickname)
        rc, out, err = cli.transfer.receive(
            source, dest, device,
            dry_run=args.dry_run, checksum=args.checksum,
            exclude=cli.config.exclude_patterns,
        )
        print(out, end="")
        if err:
            print(err, file=sys.stderr, end="")
        return rc

    def _cmd_backup(self, args, cli) -> int:
        verify = not args.no_verify and cli.config.verify_after_backup
        mgr = BackupManager(cli.config, cli.phone)
        if args.mode == "full":
            rc, out, err = mgr.full(dry_run=args.dry_run, verify=verify)
        else:
            rc, out, err = mgr.selective(dry_run=args.dry_run, verify=verify)
        print(out, end="")
        if err:
            print(err, file=sys.stderr, end="")
        if rc == 0:
            print(f"[OK] backup {args.mode} complete -> {cli.config.backup_destination}")
        else:
            print(f"[FAIL] backup {args.mode} exited {rc}", file=sys.stderr)
        return rc

    def _cmd_sync(self, args, cli) -> int:
        direction = "push" if args.push else "pull"
        device = cli.phone
        device.host = self._resolve(device.nickname)
        rc, out, err = cli.transfer.sync(
            args.left, args.right, device, direction=direction,
            dry_run=args.dry_run, checksum=args.checksum,
            exclude=cli.config.exclude_patterns,
        )
        print(out, end="")
        if err:
            print(err, file=sys.stderr, end="")
        return rc

    def _cmd_battery(self, args, cli) -> int:
        mgr = RemoteManager(cli.config, cli.phone)
        rc, out, err = mgr.battery()
        print(out, end="")
        if err:
            print(err, file=sys.stderr, end="")
        return rc

    def _cmd_storage(self, args, cli) -> int:
        mgr = RemoteManager(cli.config, cli.phone)
        rc, out, err = mgr.storage()
        print(out, end="")
        if err:
            print(err, file=sys.stderr, end="")
        return rc

    def _cmd_doctor(self, args, cli) -> int:
        findings = cli.health.doctor([cli.phone, cli.laptop])
        for line in findings:
            print(line)
        return 0

    def _cmd_disconnect(self, args, cli) -> int:
        print("Duet Connect uses stateless SSH — nothing to tear down.")
        print("Close your terminal or run 'ssh -O exit -p 8022 u0_a320@<phone-ip>' to end any multiplexed session.")
        return 0

    def _cmd_setup(self, args, cli) -> int:
        cli.config.key_dir.mkdir(parents=True, exist_ok=True)
        print(f"[CONFIG] {cli.config.config_file}")
        print(f"[KEYS]   {cli.config.key_dir}")
        for dev in (cli.phone, cli.laptop):
            ssh = SshManager(cli.config, dev)
            if not ssh.key_exists():
                ssh.generate_key()
                print(f"[KEY] Generated {dev.nickname} key: {dev.identity_file}")
            else:
                print(f"[KEY] Exists   {dev.nickname}: {dev.identity_file}")
            print(ssh.install_key_interactive())
        cli.config.save()
        print("[DONE] Edit ~/.config/duetconnect/duetconnect.cfg to match your network, then run 'duetconnect doctor'")
        return 0

    # ---------------------------------------------------------------- helpers
    def _resolve(self, nickname: str):
        """Resolve a device nickname to an IP via discovery if unset."""
        # Try config-stored host first (none by default), then discovery.
        found = self.health.discover(port=self.phone.port if nickname == "phone" else self.laptop.port)
        if found:
            return found[0]
        return None


def main(argv: Optional[List[str]] = None) -> int:
    cli = Duet ConnectCLI()
    return cli.run(argv)


if __name__ == "__main__":
    sys.exit(main())
