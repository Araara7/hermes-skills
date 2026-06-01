---
name: automation-login
description: Login to Gmail, Twitter, Discord for automation — bypass bot detection, use App Passwords, cookies, API tokens
tags: [airdrop, login, gmail, twitter, automation, bot-detection, himalaya]
related_skills: [himalaya]
---
# 🔐 Automation Login

Login ke platform populer untuk automation — bypass bot detection.

## Pola Umum

**Google (Gmail, OAuth) SELALU blokir automated browser.** Jangan buang waktu coba browser login.

### Urutan Prioritas
1. **App Password** (Gmail) — paling mudah, selalu works
2. **Cookies export** (Twitter, Discord) — user export dari browser asli
3. **API tokens** (Twitter, Discord) — untuk long-term automation
4. **IMAP/SMTP** (Email) — tanpa browser sama sekali

---

## 📧 Gmail/Google

### ❌ Yang TIDAK Works
- Browser login (Playwright, Selenium) — Google detect automation
- OAuth flow via automated browser — sama saja diblokir
- Backup codes di browser — tetap diblokir
- Camoufox untuk Google OAuth — popup tidak berfungsi di headless

### ✅ IMAP + App Password (Recommended)

**Option A: Himalaya CLI (untuk cron jobs & automation)**

Himalaya adalah CLI email client — ideal untuk automated checking:
```bash
# Install (sudah ada di Hermes)
himalaya --version

# Setup config dari accounts.json
EMAIL=$(jq -r '.email.address' ~/airdrop-agent/config/credentials/accounts.json)
PASS=$(jq -r '.email.app_password' ~/airdrop-agent/config/credentials/accounts.json)
# ... buat config.toml (lihat skill himalaya, references/gmail-app-password-config.md)

# List emails
himalaya envelope list -a gmail -f INBOX --page-size 10

# Search specific sender
himalaya envelope list -a gmail from "noreply@example.com"

# Read email by ID
himalaya message read -a gmail 5

# Send email
echo "Body text" | himalaya template send -a gmail -H "To:recipient@example.com" -H "Subject:Hello"
```

> **Pitfall**: `--page-size N` bukan `-n N`. Flag `-n` adalah search query, bukan pagination.

**Option B: Python imaplib (untuk scripts)**

```python
import imaplib
import email

EMAIL = "user@gmail.com"
APP_PASSWORD = "xxxx xxxx xxxx xxxx"  # 16 karakter, bukan password biasa

mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(EMAIL, APP_PASSWORD)

# Sekarang bisa:
mail.select("INBOX")
result, data = mail.search(None, "ALL")
```

### Cara Generate App Password
1. Buka: https://myaccount.google.com/apppasswords
2. Login dari browser user (pakai password + 2FA)
3. Select App: **Mail**
4. Generate → dapat 16 karakter
5. Simpan, tidak bisa dilihat lagi

### SMTP (Kirim Email)
```python
import smtplib
from email.mime.text import MIMEText

smtp = smtplib.SMTP("smtp.gmail.com", 587)
smtp.starttls()
smtp.login(EMAIL, APP_PASSWORD)

msg = MIMEText("Hello from agent!")
msg["Subject"] = "Test"
msg["From"] = EMAIL
msg["To"] = "recipient@example.com"
smtp.send_message(msg)
```

---

## 🐦 Twitter/X

### ❌ Yang TIDAK Works
- Google OAuth via automated browser — diblokir Google
- Browser login tanpa cookies — Twitter detect automation
- Camoufox untuk Google OAuth popup — popup tidak trigger di headless
- Direct OAuth URL — redirect_uri mismatch
- **Browser login dari VPS IP** — Twitter minta phone verification dari IP datacenter
- **App Password saja** — tidak cukup, phone number wajib linked ke akun

### ⚠️ App Password + VPS Flow (Verified 31 Mei 2026)
Dari VPS IP (Singapore/Cloudflare), urutan login Twitter:
1. Enter username → Continue
2. **Phone verification prompt** ← BLOKIR di sini, sebelum password
3. Password entry (tidak pernah tercapai)

App Password (`dr9uak4egs3g`) tidak bisa dipakai karena step 2 menghalangi. Twitter deteksi IP datacenter → wajib phone number. **Solusi satu-satunya:** user tambah nomor telepon ke akun, atau export cookies dari browser sendiri.

### ⚠️ Browser Login Pitfalls (Playwright/Camoufox)
Twitter punya overlay `data-testid="mask"` yang **memblokir semua klik** pada password field:
- `element.click()` → timeout 30s (mask intercepts pointer events)
- `force=True` → bypass mask, tapi login redirect ke phone verification
- Remove mask via JS → halaman reset ke state awal

**Phone verification trigger:**
- IP VPS (Singapore/Cloudflare) = automatic phone verification required
- App password tidak bypass phone check
- Solusi: user **harus tambah nomor telepon** ke akun Twitter dulu

**Camoufox crash:**
- `TypeError: Cannot read properties of undefined (reading 'url')` saat click Continue
- Bug di Playwright Firefox driver — gunakan Chromium sebagai alternatif

### ✅ Opsi 1: Cookies Export (Recommended)
User lakukan di browser sendiri:
1. Login Twitter normal
2. Install extension: **Cookie-Editor** (Chrome/Firefox)
3. Klik icon → **Export** → **JSON**
4. Kirim JSON ke agent

```python
import json
from playwright.sync_api import sync_playwright

def load_cookies(context, cookies_json):
    """Load cookies dari export"""
    cookies = json.loads(cookies_json) if isinstance(cookies_json, str) else cookies_json
    context.add_cookies(cookies)

# Usage
with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context()
    load_cookies(context, cookies_data)
    page = context.new_page()
    page.goto("https://twitter.com/home")
    # Sekarang sudah login!
```

### ✅ Opsi 1b: Cookies + nodriver (Anti-Detect)
```python
import asyncio, nodriver as uc

CHROME = "/home/ubuntu/.cache/ms-playwright/chromium-*/chrome-linux64/chrome"

async def twitter_with_cookies(auth_token, ct0):
    browser = await uc.start(headless=True, browser_executable_path=CHROME, browser_args=['--no-sandbox'])
    tab = await browser.get("https://x.com")
    await asyncio.sleep(3)
    await tab.send(uc.cdp.network.set_cookie(name="auth_token", value=auth_token, domain=".x.com", path="/"))
    await tab.send(uc.cdp.network.set_cookie(name="ct0", value=ct0, domain=".x.com", path="/"))
    tab2 = await browser.get("https://x.com/home")
    await asyncio.sleep(5)
    # navigator.webdriver = false, undetected
    return browser
```

**nodriver advantage**: `navigator.webdriver: false`, passes bot detection. Use for Twitter actions that need anti-detection (follow, like, retweet for Galxe social tasks).

### ✅ Opsi 2: API Bearer Token
1. Buka: https://developer.twitter.com/
2. Login → Create Project & App
3. Generate Bearer Token

```python
import requests

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAA..."

headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
resp = requests.get("https://api.twitter.com/2/users/me", headers=headers)
```

### Twitter Cookie Pitfalls (PENTING!)

- `auth_token` bersifat **httpOnly** — TIDAK bisa diakses via `document.cookie`
- Harus pakai **Application tab** (F12 → Application → Cookies) untuk copy
- `ct0` biasanya 32 karakter, tapi bisa lebih panjang di某些浏览器
- `guest_id`, `gt`, `twid` BUKAN auth cookies — tidak cukup untuk login
- v1.1 API (`api.x.com`) sering return 401 walau session valid
- Web scraping (`x.com/home`) lebih reliable untuk verifikasi session

### ✅ Opsi 3: Username + Password (Tidak ada 2FA)
```python
# Via Twitter API v2 (butuh developer access)
# Atau pakai library seperti tweepy
import tweepy

auth = tweepy.OAuthHandler("API_KEY", "API_SECRET")
auth.set_access_token("ACCESS_TOKEN", "ACCESS_SECRET")
api = tweepy.API(auth)
```

---

## 💬 Discord

### ✅ Cookies Export
Sama seperti Twitter — user export dari browser.

### ✅ Bot Token
```python
import requests

BOT_TOKEN = "MT..."  # Discord bot token

headers = {"Authorization": f"Bot {BOT_TOKEN}"}
resp = requests.get("https://discord.com/api/v10/users/@me", headers=headers)
```

### ✅ User Token (Tidak recommended, melanggar ToS)
Hanya untuk riset, jangan dipakai untuk automation serius.

---

## 🦊 Wallet/Blockchain

### Private Key → Address
```python
from eth_account import Account

private_key = "0x..."
account = Account.from_key(private_key)
address = account.address  # 0x...
```

### Simpan dengan Aman
```python
# .env file (chmod 600)
# JANGAN commit ke git
# JANGAN share

WALLET_PRIVATE_KEY=0x...
WALLET_ADDRESS=0x...
```

---

## ⚠️ Pitfalls

### Google Login
- **JANGAN** coba browser login — buang waktu
- **JANGAN** coba kurangi keamanan Google — tidak works
- **LANGSUNG** minta App Password — 1 langkah selesai

### Twitter Login
- **JANGAN** coba Google OAuth dari automated browser
- **MINTA** cookies export — user lakukan sekali, agent pakai terus
- **ALTERNATIF** API token untuk long-term

### General
- **SELALU** simpan credentials di `.env` dengan `chmod 600`
- **JANGAN** hardcode password di script
- **ENCRYPT** data sensitif sebelum simpan
- **ROTATE** tokens/cookies secara berkala
- **GUNAKAN** Camoufox untuk anti-detect (webdriver=false)
- **GUNAKAN** xvfb jika butuh popup: `xvfb-run -a python3 script.py`

### Credential Storage Pattern
Simpan semua credentials di `~/airdrop-agent/config/credentials/accounts.json`:
```json
{
  "email": { "address": "...", "app_password": "...", "status": "active" },
  "twitter": { "username": "...", "auth_token": "...", "ct0": "...", "status": "active" },
  "wallet": { "address": "...", "private_key_encrypted": "...", "status": "active" }
}
```

Baca dengan `jq`:
```bash
jq -r '.email.app_password' ~/airdrop-agent/config/credentials/accounts.json
jq -r '.twitter.auth_token' ~/airdrop-agent/config/credentials/accounts.json
```

---

## Referensi Detail

- `references/twitter-cookie-export.md` — Panduan export cookies Twitter
- `references/twitter-cookie-validation.md` — Validasi dan penggunaan cookies

## Checklist Login

### Gmail
- [ ] Minta App Password (bukan password biasa)
- [ ] Test IMAP connection
- [ ] Test SMTP connection
- [ ] Simpan di `.env`

### Twitter
- [ ] Minta cookies export ATAU API token
- [ ] Test koneksi
- [ ] Simpan cookies/token

### Wallet
- [ ] Dapatkan private key
- [ ] Derive address
- [ ] Simpan private key di `.env`
- [ ] Verify address di explorer
