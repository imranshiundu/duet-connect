# Troubleshooting

## Connection problems

### "ssh: connect to host 192.168.100.51 port 8022: Connection refused"

**Cause:** sshd is not running on the phone, or the IP changed.

**Fix:**
```bash
# On the phone (Termux)
sshd                          # start the server
ip -4 addr show wlan0         # check IP — may have changed
# Update duetconnect.cfg with the new IP if needed
```

### "Host key verification failed"

**Cause:** You restarted sshd on the phone; its host key changed.

**Fix:**
```bash
# On the laptop
ssh-keyscan -p 8022 <phone-ip> >> ~/.ssh/known_hosts
# Then retry: duetconnect connect phone
```

### "Permission denied (publickey)"

**Cause:** Your public key isn't in the phone's `~/.ssh/authorized_keys`.

**Fix:**
```bash
# On the laptop
ssh-copy-id -i ~/.ssh/duetconnect/duetconnect_phone.pub \
  -p 8022 u0_a320@<phone-ip>
# Enter the phone's SSH password when prompted
```

### "No route to host" / ping fails

**Cause:** Devices aren't on the same network.

**Fix:**
- Confirm both phone and laptop are on the same Wi-Fi, OR
- Turn on the phone's hotspot and join it from the laptop, OR
- Use USB tethering, OR
- Use ADB wireless debugging

---

## Transfer problems

### rsync transfers 0 bytes / finishes instantly

**Cause:** The `PhoneBackup/` folder doesn't exist yet, or the rsync command
was split across lines without proper spacing.

**Fix:**
```bash
mkdir -p /run/media/imran/GRAVITY/PhoneBackup
rsync -avh --progress --partial -e "ssh -p 8022" \
  u0_a320@192.168.100.51:/storage/emulated/0/ \
  /run/media/imran/GRAVITY/PhoneBackup/
```

### Transfer is slow (< 1 MB/s)

**Cause:** Router Wi-Fi congestion or weak signal.

**Fix:**
- Switch to phone hotspot (direct device-to-device, usually faster)
- Move closer to the router
- Use USB tethering for a wired connection

### Transfer interrupted (Wi-Fi dropped)

**Fix:** Rerun the same command. `--partial` lets rsync resume from where it
stopped — already-copied files are skipped.

---

## Phone storage problems

### "Permission denied" reading phone files

**Cause:** Termux doesn't have storage permission.

**Fix:**
```bash
# On the phone (Termux)
termux-setup-storage
# Tap "Allow" on the popup
# Then restart sshd
sshd
```

### Phone shows 183GB used but only ~40GB visible

**Cause:** ~140GB is inside apps' private storage (WhatsApp databases, video
vaults, download manager caches). rsync can only see shared storage.

**Fix:** Export files through each app before wiping:
- Video vault app → "restore to gallery"
- Download manager → move downloads to shared Download folder
- WhatsApp → export chats to Google Drive or local file

---

## Duet Connect problems

### "duetconnect: command not found"

**Cause:** `~/.local/bin` isn't on your PATH.

**Fix:**
```bash
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### "No module named griotlink" / import errors

**Cause:** Package not installed or installed without `-e`.

**Fix:**
```bash
python3 -m pip install -e .
```

### "No host resolved for phone"

**Cause:** Phone IP is dynamic and discovery didn't find it.

**Fix:**
```bash
# Find the phone's current IP
ping -c 3 <phone-ip>
# Update discovery_network in duetconnect.cfg to match your subnet
# Or run: duetconnect doctor  (re-discovers)
```
