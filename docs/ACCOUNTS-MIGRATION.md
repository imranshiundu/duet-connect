# Accounts & Data Migration Checklist

Before giving your phone away, follow this checklist in order.

```
┌─────────────────────────────────────────────────────────────────┐
│          PHONE WIPE PREPARATION CHECKLIST                       │
├─────────────────────────────────────────────────────────────────┤
│  [ ] 1. Back up all files to laptop/external drive              │
│  [ ] 2. Save app list + accounts report                         │
│  [ ] 3. Export WhatsApp chats                                   │
│  [ ] 4. Export 2FA authenticator codes                          │
│  [ ] 5. Log out of banking / M-Pesa apps                        │
│  [ ] 6. Remove Google account                                   │
│  [ ] 7. Turn off Find My Device                                 │
│  [ ] 8. Remove screen lock (PIN/pattern)                        │
│  [ ] 9. Factory reset                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 1 — Back up all files

```bash
# On laptop
duetconnect doctor                          # verify connection
duetconnect backup                          # full phone → external drive
duetconnect receive ~/phone-apps.txt ./     # save app inventory
duetconnect receive ~/ACCOUNTS-REPORT.txt ./ # save accounts report
```

## Step 2 — Save app list + accounts report

Run on the phone (Termux):
```bash
pm list packages > ~/phone-apps.txt
```
Then transfer both files to your laptop (see USAGE.md).

## Step 3 — Export WhatsApp chats

**WhatsApp on the phone:**
- Settings → Chats → Chat backup → Back up to Google Drive
- OR: Settings → Chats → Chat history → Export chat (per conversation)

Transfer the exported `.zip` or `.txt` files to your laptop via Duet Connect.

## Step 4 — Export 2FA authenticator codes ⚠️ CRITICAL

If you use Google Authenticator, Authy, Microsoft Authenticator, etc.:
- **Export transfer codes to your new phone BEFORE wiping this one**
- Without these, you'll be locked out of accounts protected by 2FA

**Google Authenticator:**
- Tap the three dots → Transfer accounts → Export accounts
- Scan the QR code with your new phone

## Step 5 — Log out of banking / M-Pesa apps

- Open each banking app → Settings → Log out
- Note your PINs — you'll need them on the new phone
- M-Pesa: your SIM carries the account, but log out of the app first

## Step 6 — Remove Google account

```bash
# On the phone: Settings → Passwords & accounts → Google → Remove account
# This removes Gmail, Play Store, Drive, Photos sync from this device
```

## Step 7 — Turn off Find My Device

- Settings → Google → Find My Device → Turn OFF
- Otherwise the phone remains locked to your account after reset

## Step 8 — Remove screen lock

- Settings → Security → Screen lock → None / Swipe
- Factory reset requires no lock, or you'll need your Google credentials

## Step 9 — Factory reset

- Settings → System → Reset options → Erase all data (factory reset)
- Confirm. The phone will reboot clean.

---

## What Duet Connect saves automatically

| Item | How |
|------|-----|
| Photos, videos, DCIM | `duetconnect backup` |
| Documents, Downloads | `duetconnect backup` |
| Music, Podcasts, Audiobooks | `duetconnect backup` |
| Termux home (scripts, settings) | `duetconnect receive ~/ ./termux-home/` |
| App list (233 packages) | `pm list packages > phone-apps.txt` → transfer |
| Accounts report | Generated on phone → transfer |

---

## What Duet Connect CANNOT save

| Item | Why | What to do |
|------|-----|------------|
| WhatsApp chat database | App-private, encrypted | Export through WhatsApp app |
| 2FA authenticator seeds | Security — not exportable | Transfer codes to new phone first |
| Banking app sessions | App-private, security | Log out, re-login on new phone |
| App logins (cookies, tokens) | App-private | Re-login on new phone |
| SMS messages | App-private | Use SMS backup app or forward |
