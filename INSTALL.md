# Install Duet Connect

## Quick install (Ubuntu/Debian)
```bash
git clone <your-fork>/duetconnect.git
cd duetconnect
sudo apt-get install -y rsync openssh-client python3-pip
python3 -m pip install --user -e .
duetconnect setup
duetconnect doctor
```

## One-time phone pairing
```bash
ssh-copy-id -i ~/.ssh/duetconnect/duetconnect_phone.pub -p 8022 u0_a320@<phone-ip>
```

Then configure `~/.config/duetconnect/duetconnect.cfg` (copy from `duetconnect.cfg.example`) to match your network and external-drive mount point.

## Requirements
- Python 3.8+
- rsync, openssh-client, ssh-keygen, ssh-keyscan, ping
- On the phone: Termux with `sshd` running on port 8022 and storage access granted (`termux-setup-storage`)
- Optional on phone: `termux-api` package for `termux-battery-status`
