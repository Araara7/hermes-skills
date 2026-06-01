---
name: anti-ip-detection
description: Anti IP detection for web3 airdrops — proxy rotation, browser fingerprinting, Camoufox, user-agent spoofing, VPN management
tags: [airdrop, proxy, fingerprint, vpn, web3, camoufox]
---

# 🛡️ Anti IP Detection

Teknik untuk menghindari deteksi IP dan fingerprint saat menjalankan task airdrop multi-wallet.

## Browser Anti-Detect: Camoufox (Recommended)

Camoufox lebih aman dari Playwright biasa karena:
- ✅ `navigator.webdriver = false` (tidak terdeteksi bot)
- ✅ Randomized fingerprint (WebGL, Canvas, Audio)
- ✅ Real Firefox user-agent
- ✅ Anti-fingerprinting built-in

## Browser Anti-Detect: Nodriver (Chromium-based — NEW)

Nodriver adalah successor undetected-chromedriver. Lebih cepat dari Camoufox:
- ✅ `navigator.webdriver = false` — truly undetected
- ✅ Bypass Cloudflare, Imperva, DataDome
- ✅ Async-first, CDP-based (no Selenium)
- ✅ Startup cepat (<5 detik vs Camoufox 2-3 menit)
- ❌ WASM captcha gak work (lazy loading issue)
- ❌ Perlu `--no-sandbox` di VPS

**Install:** `pip install nodriver` (v0.50+)

**Chrome path:** `~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome`

```python
import nodriver as uc
CHROME = "/home/ubuntu/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome"

browser = await uc.start(
    headless=True,
    browser_executable_path=CHROME,
    browser_args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
)
tab = await browser.get("https://target.com")
# navigator.webdriver = False ✅
```

### Browser Comparison
| Feature | Camoufox | Nodriver | Playwright |
|---------|----------|----------|------------|
| webdriver flag | false ✅ | false ✅ | true ❌ |
| WASM captcha | ❌ | ❌ | ✅ |
| Cloudflare bypass | ✅ | ✅✅ | ❌ |
| Startup speed | 2-3 min | <5 sec | <5 sec |
| Anti-fingerprint | ✅✅ | ✅ | ❌ |
| Async support | ❌ | ✅ | ✅ |
| Best for | Turnstile | Token extract | WASM captcha |

### Install & Setup
```bash
pip install camoufox
```

### Basic Usage
```python
from camoufox.sync_api import Camoufox

with Camoufox(headless=True) as browser:
    page = browser.new_page()
    page.goto("https://target-site.com")
    
    # Verify stealth
    webdriver = page.evaluate("navigator.webdriver")  # Should be False
    ua = page.evaluate("navigator.userAgent")  # Real Firefox UA
```

### Dengan Virtual Display (untuk popup support)
```bash
apt-get install xvfb
xvfb-run -a python3 script.py
```

Lihat `references/xvfb_usage.md` untuk detail lebih lanjut.

## VPN / Proxy Solutions

### Cloudflare WARP (FREE - Recommended)
- ✅ **Unlimited bandwidth** gratis
- ✅ **No registration** needed
- ✅ **WireGuard** protocol (cepat, ringan)
- ✅ **Cloudflare IP** (tidak blacklisted)
- ⚠️ IP shared dengan user lain

**Install & Setup:**
```bash
# Install
curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ jammy main" | sudo tee /etc/apt/sources.list.d/cloudflare-client.list
sudo apt-get update && sudo apt-get install -y cloudflare-warp

# Register (needs expect for TOS acceptance)
sudo apt-get install -y expect
cat << 'EOF' > /tmp/warp_register.exp
#!/usr/bin/expect -f
set timeout 30
spawn warp-cli registration new
expect "Accept Terms" { send "y\r" }
expect eof
EOF
expect /tmp/warp_register.exp

# Connect
warp-cli connect
curl -s ipinfo.io  # Verify IP changed

# Disconnect
warp-cli disconnect
```

**VPN Manager Script:** `~/airdrop-agent/scripts/vpn_manager.sh`
```bash
./scripts/vpn_manager.sh on       # Nyalakan WARP
./scripts/vpn_manager.sh off      # Matikan WARP
./scripts/vpn_manager.sh status   # Cek status
./scripts/vpn_manager.sh switch   # Reconnect
```

### hide.me Free VPN (10GB/bulan)
- ✅ No credit card
- ✅ 5 lokasi (Singapore, Canada, US, Germany, Netherlands)
- ⚠️ Butuh akun untuk WireGuard config
- ⚠️ 10GB/bulan limit

**Setup:** Daftar di https://hide.me/en/free-vpn → Generate WireGuard config → Import ke `/etc/wireguard/wg0.conf`

### Tor (FREE - Multi-IP)
- ✅ Ganti IP setiap request
- ✅ Sangat private
- ⚠️ Lambat (3-10 detik per request)
- ⚠️ Sering blocked oleh site

```bash
# Install
sudo apt-get install -y tor

# Start
sudo systemctl start tor

# Use with curl
curl --socks5-hostname 127.0.0.1:9050 https://api.ipify.org

# Python
import socks
import socket
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
socket.socket = socks.socksocket
```

## Proxy Rotation

### Format Proxy
```
protocol://user:pass@host:port
socks5://user:pass@host:port
```

### Free Proxy Sources (Low Quality)
| Source | URL | Quality |
|--------|-----|---------|
| ProxyScrape | proxyscrape.com | ⚠️ 10-20% working |
| Free-Proxy-List | free-proxy-list.net | ⚠️ 5-15% working |
| Geonode | geonode.com | ⚠️ 10-20% working |
| PubProxy | pubproxy.com | ⚠️ 10-20% working |

**⚠️ Warning:** Free proxies sering dead/blacklisted. Gunakan WARP atau Tor sebagai alternatif gratis.

## Browser Anti-Detect: Camoufox (Recommended)

```python
from playwright.sync_api import sync_playwright

def create_stealth_browser(proxy=None):
    p = sync_playwright().start()
    
    browser = p.chromium.launch(
        headless=False,
        proxy={"server": proxy} if proxy else None,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
        ]
    )
    
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        locale="en-US",
    )
    
    return browser, context
```

## User-Agent Rotation

```python
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

def get_random_ua():
    import random
    return random.choice(USER_AGENTS)
```

## Camoufox Anti-Detect Browser

### Why Camoufox
- Randomized fingerprint per session
- Webdriver flag = False (not detected as bot)
- Based on Firefox (less suspicious than Chromium)
- Better than Playwright stealth for Google/Twitter

### Setup
```bash
pip install camoufox
# xvfb needed for non-headless mode
apt-get install -y xvfb
```

### Usage
```python
from camoufox.sync_api import Camoufox

# Headless (no popup support)
with Camoufox(headless=True) as browser:
    page = browser.new_page()
    page.goto("https://example.com")
    # navigator.webdriver = False ✅

# With xvfb (popup support)
# Run with: xvfb-run -a -s "-screen 0 1920x1080x24" python3 script.py
with Camoufox(headless=False) as browser:
    page = browser.new_page()
    # Supports popups, but Google OAuth still difficult
```

### Google Login with Camoufox
- Browser login to Google works (email + password/App Password)
- Cookies can be saved and reused
- OAuth popup handling is unreliable — use IMAP App Password instead

### Pitfalls
- Google OAuth popups in iframes are extremely hard to automate
- Session cookies from Camoufox may not include all httpOnly cookies
- Always test `navigator.webdriver` to confirm anti-detect is working

## Checklist Sebelum Run

- [ ] IP berbeda per wallet
- [ ] Fingerprint unik per session
- [ ] Cookie bersih per akun
- [ ] Delay random antar task
- [ ] Cek IP sebelum mulai: `curl ipinfo.io`

## Pitfalls

⚠️ **JANGAN:**
- Pakai Playwright biasa untuk Google/Twitter (detected sebagai bot)
- Pakai IP yang sama untuk wallet berbeda
- Login berulang dari IP berbeda terlalu cepat
- Pakai free proxy (sering blacklisted)
- Berharap cookies Google maintain session di browser baru (session cookies ≠ auth cookies)
- Coba OAuth popup automation untuk Google Sign-In (GSI API sangat sensitif)

✅ **LAKUKAN:**
- Gunakan Camoufox untuk anti-detect
- Test proxy sebelum pakai
- Simpan mapping wallet ↔ IP
- Delay 30-60 detik antar task
- **Export cookies manual** untuk Google/Twitter OAuth (paling reliable)
- Gunakan **App Password** untuk Gmail IMAP (bukan password biasa)
- Gunakan **xvfb** untuk popup support: `xvfb-run -a -s "-screen 0 1920x1080x24" python3 script.py`

## Free Proxy Reality (Tested 31 Mei 2026)

**Free proxy hampir tidak berguna:**
- 90%+ dead/timeout saat test
- Sangat lambat (5-30 detik per request)
- Sering blacklisted site airdrop
- IP shared ribuan user

**Test result (ProxyScrape):**
```
47.82.154.21:3129 → ❌ dead
47.82.154.239:3129 → ❌ dead
47.82.180.175:3129 → ❌ dead
```

## Free VPN Alternatives (Lebih Bagus dari Free Proxy)

| VPN | Tanpa Akun | WireGuard | Limit | Setup |
|-----|------------|-----------|-------|-------|
| **Cloudflare WARP** | ✅ | ✅ | Unlimited | `warp-cli` |
| hide.me | ✅ App | ❌ Butuh akun | 10GB/bulan | WireGuard config |
| ProtonVPN | ✅ App | ❌ Butuh akun | Unlimited | App only |
| Windscribe | ⚠️ Email | ✅ | 10GB/bulan | WireGuard config |

### Cloudflare WARP (Recommended untuk VPS)
```bash
# Install
curl -fsSL https://pkg.cloudflareclient.com/install.sh | sudo bash
warp-cli register
warp-cli connect
curl ipinfo.io  # IP berubah

# Switch off
warp-cli disconnect
```

### hide.me WireGuard Setup
1. Buka https://hide.me/en/account → Create Free Account
2. Menu WireGuard → Generate Config → pilih Singapore
3. Download .conf → import ke VPS:
```bash
cp hide-me.conf /etc/wireguard/wg0.conf
wg-quick up wg0
```

## Referensi Detail

- `references/google-twitter-login.md` — Tantangan login Google/Twitter dan solusi
- `references/xvfb_usage.md` — Penggunaan xvfb untuk popup support
- `references/proxy_providers.md` — Daftar provider proxy
- `references/camoufox-usage.md` — Detail penggunaan Camoufox
- `references/xvfb-usage.md` — **Panduan lengkap xvfb** (instalasi, troubleshooting, best practices)

## Teknik yang Terbukti

### ✅ Gmail IMAP dengan App Password
```python
import imaplib
mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login("email@gmail.com", "xxxx xxxx xxxx xxxx")  # App Password
```

### ❌ Google OAuth via Browser (Tidak Reliable)
Google mendeteksi automated browser bahkan dengan Camoufox. Popup GSI tidak trigger dengan benar di headless mode.

### ✅ Manual Cookie Export (Paling Reliable)
1. Login manual di browser asli
2. Export cookies dengan Cookie-Editor
3. Load cookies di script automation
