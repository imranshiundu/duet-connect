# Duet Connect — Visual Examples

## Example A: Back up phone movies to external drive

```
┌─────────────────────────────────────────────────────────────────────┐
│  PHONE                                                LAPTOP        │
│  ┌─────────────┐                                      ┌─────────┐   │
│  │ /storage/   │   rsync over SSH (port 8022)         │ duet-   │   │
│  │  emulated/  │ ──────────────────────────────────▶  │ connect │   │
│  │     /0      │                                      │         │   │
│  │             │                                      │  GRAV   │   │
│  │   Movies/   │                                      │  ITY/   │   │
│  │   (27.4 GB) │                                      │ Phone-  │   │
│  └──────┬──────┘                                      │ Backup/ │   │
│         │                                             │         │   │
│         │                                             │ full-   │   │
│         │                                             │ 2026... │   │
│         │                                             │ /Movies/│   │
│         │                                             └────┬────┘   │
│ Termux sshd (8022)                                         │         │
└─────────────────────────────────────────────────────────────────────┘
```

### Command (laptop)
```bash
duetconnect receive phone:~/storage/movies/ \
  /run/media/imran/GRAVITY/PhoneBackup/movies/
```

### Expected output
```
sending incremental file list
Movies/
Movies/AfroBeat & Others/
Movies/AfroBeat & Others/song1.mp4
      45.2M 100%   3.2MB/s    0:00:14
...
sent 27.4G bytes  received 482 bytes  1.8M bytes/sec
total size is 27.4G  speedup is 1.00
[OK] backup full complete -> /run/media/imran/GRAVITY/PhoneBackup/
```

---

## Example B: Phone hotspot (no router)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PHONE HOTSPOT                                    │
│                                                                     │
│  ┌─────────────┐                  ┌─────────────┐                  │
│  │   PHONE     │                  │  LAPTOP     │                  │
│  │  192.168.   │                  │  192.168.   │                  │
│  │   43.1      │◄──── Wi-Fi ─────▶  43.50       │                  │
│  │             │     hotspot      │             │                  │
│  │   sshd:8022 │                  │  duet-connect│                 │
│  └──────┬──────┘                  └──────┬──────┘                  │
│         │                               │                          │
│         └────────── SSH ────────────────┘                          │
│                    port 8022                                        │
└─────────────────────────────────────────────────────────────────────┘
```

### Steps
1. Phone: Settings → Hotspot & tethering → Wi-Fi hotspot → ON
2. Laptop: Wi-Fi → join phone's hotspot
3. Phone (Termux): `ip -4 addr show wlan0` → confirm `192.168.43.1`
4. Phone (Termux): `sshd`
5. Laptop: `duetconnect doctor` → should show phone OK

---

## Example C: Same Wi-Fi network

```
┌─────────────────────────────────────────────────────────────────────┐
│                    HOME Wi-Fi ROUTER                                │
│                        (192.168.100.1)                              │
│                       /               \                             │
│                      /                 \                            │
│             ┌──────────┐         ┌─────────────┐                   │
│             │  PHONE   │         │  LAPTOP     │                   │
│             │          │         │   Griot     │                   │
│             │ 192.168. │         │ 192.168.    │                   │
│             │ .100.51  │         │ .100.60     │                   │
│             └────┬─────┘         └──────┬──────┘                   │
│                  │                      │                           │
│                  └─────── SSH ───────────┘                           │
│                       port 8022                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Example D: Selective backup folder structure

```
/run/media/imran/GRAVITY/PhoneBackup/
└── selective-20261109-150000/
    ├── DCIM/
    │   ├── 100MEDIA/
    │   │   ├── IMG_0001.JPG
    │   │   └── VID_0002.MP4
    │   └── .thumbnails/
    ├── Download/
    │   ├── document.pdf
    │   └── video.mp4
    ├── Documents/
    │   ├── CV.pdf
    │   └── notes.txt
    ├── Movies/
    ├── Music/
    └── Pictures/
```

---

## Example E: doctor output (all green)

```
$ duetconnect doctor
[OK] rsync found
[OK] ssh found
[OK] ssh-keygen found
[OK] ssh-keyscan found
[OK] ping found
[CONFIG] /home/imran/.config/duetconnect/duetconnect.cfg
[KEYS]   /home/imran/.ssh/duetconnect
[OK] phone: SSH to phone (192.168.100.51) OK
[OK] laptop: laptop root: total=476G used=120G free=320G
```

### doctor output (with issues)

```
$ duetconnect doctor
[OK] rsync found
[OK] ssh found
[MISSING] ssh-keygen not installed        ← install it
[OK] ssh-keyscan found
[OK] ping found
[CONFIG] /home/imran/.config/duetconnect/duetconnect.cfg
[KEYS]   /home/imran/.ssh/duetconnect
[FAIL] phone: No SSH key for phone        ← run duet-connect setup
[OK] laptop: laptop root: total=476G used=120G free=320G
```
