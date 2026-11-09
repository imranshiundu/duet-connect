# Connecting Phone ↔ Laptop — All Methods

Duet Connect works over SSH. Your laptop and phone must be able to reach each
other on the network. Here are **four ways** to make that happen, from easiest
to most robust.

---

## Method 1 — Same Wi-Fi network (simplest)

Both devices join the same router. The phone gets an IP like `192.168.100.51`,
the laptop gets `192.168.100.60`. They can talk directly.

```
       Wi-Fi ROUTER
       (192.168.100.1)
          /    \
         /      \
   ┌───────┐  ┌─────────┐
   │ Phone │  │ Laptop  │
   │       │  │  Griot  │
   │ 192.168.│  │ 192.168.│
   │ .100.51│  │ .100.60 │
   └────┬───┘  └────┬───┘
        │          │
        └────SSH───┘  (port 8022)
```

### Steps

**On the phone (Termux):**
```bash
# Find your phone's IP
ip -4 addr show wlan0 | grep inet
# → 192.168.100.51

# Start SSH server
sshd

# Prevent screen sleep
termux-wake-lock
```

**On the laptop (Ubuntu):**
```bash
# Test you can reach the phone
ping -c 3 192.168.100.51

# Connect via Duet Connect
duetconnect connect phone

# Or pull files directly with rsync
rsync -avh --progress -e "ssh -p 8022" \
  u0_a320@192.168.100.51:/storage/emulated/0/ \
  /run/media/imran/GRAVITY/PhoneBackup/
```

---

## Method 2 — Phone hotspot (no router needed)

Use your phone as the Wi-Fi access point. The laptop joins the phone's hotspot.
Best when you have no home internet or the router blocks device-to-device traffic.

```
       PHONE HOTSPOT
    (Android phone)
       192.168.43.1
          │
    ┌─────┴─────┐
    │           │
 Laptop       (other devices)
 192.168.43.x
    │
    └──SSH──→ phone port 8022
```

### Steps

**On the phone:**
1. Settings → Network & internet → Hotspot & tethering → **Wi-Fi hotspot** → Turn ON
2. Note the hotspot name (SSID) and password
3. Find the phone's hotspot IP (usually `192.168.43.1`):
   ```bash
   ip -4 addr show wlan0 | grep inet
   ```
4. Start SSH:
   ```bash
   sshd
   termux-wake-lock
   ```

**On the laptop:**
1. Wi-Fi → join the phone's hotspot SSID
2. Test: `ping -c 3 192.168.43.1`
3. Connect: `duetconnect connect phone`

> 💡 **Tip:** Hotspot is often faster than router Wi-Fi because devices talk
> directly, but it drains the phone battery faster. Keep the phone on a charger.

---

## Method 3 — USB tethering (cable as network, not file copy)

If your USB cable doesn't transfer files (MTP broken), it can still carry a
network connection. The phone shares its mobile data over USB; the laptop gets
an IP on the `usb0` interface.

```
   PHONE                          LAPTOP
  ┌─────┐                        ┌──────────┐
  │USB  │── cable ── USB ──┐   │  usb0    │
  │port │                  │   │ 192.168. │
  └─────┘                  │   │ .42.2    │
        │                  │   └────┬─────┘
        │   mobile data    │        │
        └──────────────────┘   SSH port 8022
             (4G/5G)
```

### Steps

**On the phone:**
1. Connect USB cable to laptop
2. Settings → Network & internet → Hotspot & tethering → **USB tethering** → ON
3. In Termux:
   ```bash
   ip -4 addr show usb0 | grep inet
   # → 192.168.42.1 (or similar)
   sshd
   termux-wake-lock
   ```

**On the laptop:**
```bash
ip addr show usb0
# → 192.168.42.2
ping -c 3 192.168.42.1
duetconnect connect phone   # after configuring host to 192.168.42.1
```

---

## Method 4 — ADB Wireless Debugging (no app permissions needed)

If Termux can't access storage (locked/carrier builds), use Android's ADB over
Wi-Fi. This works at the system level and can pull files directly.

```
   PHONE                      LAPTOP
┌─────────┐              ┌─────────────┐
│ adbd    │── Wi-Fi ────▶│  adb client │
│ port    │   5555       │  (Griot)    │
│ 5555    │              └──────┬──────┘
└────┬────┘                     │
     │      adb pull             │
     └───────────────────────────┘
```

### Steps

**On the phone:**
1. Settings → About phone → tap **Build number** 7 times (enables Developer options)
2. Settings → System → Developer options → **Wireless debugging** → ON
3. Wireless debugging → Pair device with QR code or pairing code
4. Note the IP:port shown (e.g., `192.168.100.51:43221`)

**On the laptop:**
```bash
# Install adb
sudo apt install -y adb

# Pair (use the code from phone)
adb pair 192.168.100.51:43221

# Connect
adb connect 192.168.100.51:43221

# Pull all shared storage to external drive
adb pull /sdcard/ /run/media/imran/GRAVITY/PhoneBackup/

# Pull DCIM only
adb pull /sdcard/DCIM/ /run/media/imran/GRAVITY/PhoneBackup/DCIM/
```

---

## Quick comparison

| Method | Needs router? | Cable? | Speed | Best for |
|--------|---------------|--------|-------|----------|
| Same Wi-Fi | Yes | No | Medium | Everyday use |
| Phone hotspot | No | No | Fast | No router / fast transfer |
| USB tethering | No | Yes | Fast | MTP/cable broken |
| ADB Wireless | Yes | No | Medium | Termux locked out |

---

## Configure Duet Connect for your network

Edit `~/.config/duetconnect/duetconnect.cfg`:

```ini
[devices]
phone_user = u0_a320
phone_port = 8022
discovery_network = 192.168.100.0/24   # match your Wi-Fi subnet

[paths]
backup_destination = /run/media/imran/GRAVITY/PhoneBackup
```

Then run `duetconnect doctor` to verify both devices are reachable.

---

**Next:** [Architecture & internals →](ARCHITECTURE.md)
