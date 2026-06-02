---
name: auto-get-token
description: Auto extract API keys, JWT tokens, auth headers from web apps — network interception, localStorage, cookies, API discovery, Camoufox integration
tags: [airdrop, api, jwt, token, automation, web3, camoufox]
---

# 🔑 Auto Get API/JWT/Token

Ekstraksi otomatis token autentikasi dari web apps untuk task airdrop.

## Token Types

| Type | Format | Lokasi |
|------|--------|--------|
| JWT | `eyJhbG...` | Header, Cookie, localStorage |
| Bearer Token | `Bearer xxx` | Authorization header |
| API Key | `sk-xxx`, `pk-xxx` | Header, Query param |
| Session Cookie | `session=xxx` | Cookie |
| CSRF Token | Random string | Form field, Meta tag |

## Quick Start: browser_auth.py

Universal auth extractor script (F12-style). Works on any website.

```bash
cd ~/airdrop-agent
python3 scripts/browser_auth.py https://target.com --timeout 120
```

Features:
- Auto-detects login state (logout button, avatar, dashboard, tokens in storage)
- Extracts: cookies, localStorage, sessionStorage, JWT tokens, API keys
- Detects auth method: Privy, Firebase, Auth0, Supabase, Clerk, NextAuth
- Scans for JWT patterns, Bearer tokens, Slack/GitHub/Google API keys
- Saves structured JSON report

For Web3 platforms using Privy: script opens WalletConnect QR, user scans from phone, script auto-extracts everything.

Script location: `~/airdrop-agent/scripts/browser_auth.py` (also in skill `scripts/`)

## 1. Intercept Network (Camoufox - Recommended)

```python
from camoufox.sync_api import Camoufox
import json

captured_tokens = []

def handle_request(request):
    """Capture auth headers from requests"""
    headers = request.headers
    
    # Check Authorization header
    if "authorization" in headers:
        auth = headers["authorization"]
        captured_tokens.append({
            "type": "authorization",
            "value": auth[:100],
            "url": request.url[:80]
        })
        print(f"[TOKEN] Authorization: {auth[:50]}...")
    
    # Check custom auth headers
    for key in ["x-api-key", "x-auth-token", "x-csrf-token", "x-jwt"]:
        if key in headers:
            captured_tokens.append({
                "type": key,
                "value": headers[key][:100],
                "url": request.url[:80]
            })

def handle_response(response):
    """Capture tokens from response bodies"""
    url = response.url
    
    # Check for token endpoints
    if any(x in url for x in ["/login", "/auth", "/token", "/session"]):
        try:
            if 'json' in response.headers.get('content-type', ''):
                body = response.json()
                for field in ["token", "access_token", "jwt", "session_token"]:
                    if field in body:
                        captured_tokens.append({
                            "type": field,
                            "value": body[field][:100],
                            "url": url[:80]
                        })
        except:
            pass

def intercept_tokens(url, cookies=None):
    """Main function to intercept tokens using Camoufox"""
    with Camoufox(headless=True) as browser:
        context = browser.new_context()
        
        if cookies:
            context.add_cookies(cookies)
        
        page = context.new_page()
        
        # Setup interception
        page.on("request", handle_request)
        page.on("response", handle_response)
        
        # Navigate
        page.goto(url)
        page.wait_for_load_state("networkidle")
        
        return captured_tokens
```

## 2. Extract from localStorage

```python
def extract_local_storage(page):
    """Extract tokens from localStorage"""
    
    tokens = page.evaluate("""
        () => {
            const tokens = {};
            const keys = Object.keys(localStorage);
            
            for (const key of keys) {
                const value = localStorage.getItem(key);
                
                if (key.toLowerCase().includes('token') || 
                    key.toLowerCase().includes('jwt') ||
                    key.toLowerCase().includes('auth')) {
                    tokens[key] = value;
                }
                
                if (value && value.startsWith('eyJ')) {
                    tokens[`jwt_${key}`] = value;
                }
            }
            
            return tokens;
        }
    """)
    
    return tokens
```

## 3. Extract from Cookies

```python
def extract_cookies(context):
    """Extract auth cookies"""
    
    cookies = context.cookies()
    
    auth_cookies = {}
    for cookie in cookies:
        name = cookie["name"].lower()
        if any(x in name for x in ["token", "jwt", "session", "auth", "sid"]):
            auth_cookies[cookie["name"]] = cookie["value"]
    
    return auth_cookies
```

## 4. JWT Decoder

```python
import base64
import json

def decode_jwt(token):
    """Decode JWT without verification"""
    
    parts = token.split(".")
    if len(parts) != 3:
        return None
    
    payload = parts[1]
    payload += "=" * (4 - len(payload) % 4)
    
    try:
        decoded = base64.b64decode(payload)
        return json.loads(decoded)
    except:
        return None
```

## Twitter Cookie Extraction (Proven Workflow)

### Step 1: Get auth_token
`auth_token` is **httpOnly** — cannot access via `document.cookie`.

1. F12 → **Application** → **Cookies** → `https://twitter.com`
2. Filter: `auth`
3. Copy `auth_token` value (40 hex chars)

### Step 2: Get ct0
`ct0` IS accessible via JavaScript. Run in Console:
```javascript
document.cookie.match(/ct0=([^;]+)/)?.[1]
```

### Step 3: Verify Session
```python
import requests

cookies = {"auth_token": "...", "ct0": "..."}
headers = {
    "Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA3",
    "x-csrf-token": ct0[:32],
}

# Test 1: Home page (most reliable)
resp = requests.get("https://x.com/home", cookies=cookies, headers=headers, allow_redirects=True)
# 200 = valid, redirect to /login = invalid

# Test 2: API (may return 401 even with valid session)
resp = requests.get("https://api.x.com/1.1/account/verify_credentials.json", cookies=cookies, headers=headers)

# Test 3: Extract user from HTML
import re
html = resp.text
username = re.search(r'"screen_name":"([^"]+)"', html)
```

### Pitfalls
- v1.1 API may return 401 even when session is valid — always test with home page access first
- ct0 from `document.cookie` works for API calls even without the full httpOnly value
- Twitter public Bearer token: `AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA3`

## Background Execution Workflow

**PENTING:** Selalu extract data via background browser dulu, lalu pakai API.

```python
# Step 1: Background browser - extract tokens
auth_data = extract_auth_data("https://target.com")

# Step 2: Pakai API untuk operasi (tanpa browser)
resp = requests.get("https://target.com/api/data", headers={"Authorization": f"Bearer {token}"})
```

Lihat skill `background-browser-workflow` untuk detail lengkap.

### nodriver for Token Extraction
```python
import nodriver as uc
CHROME = "/home/ubuntu/.cache/ms-playwright/chromium-*/chrome-linux64/chrome"

browser = await uc.start(headless=True, browser_executable_path=CHROME, browser_args=['--no-sandbox'])
tab = await browser.get("https://target.com")
await asyncio.sleep(10)

# Extract localStorage
tokens = await tab.evaluate("""(() => {
    const data = {};
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key.includes('token') || key.includes('auth') || key.includes('jwt')) {
            data[key] = localStorage.getItem(key);
        }
    }
    return JSON.stringify(data);
})()""")
```

**Pitfall**: nodriver async evaluate returns None for Promises. Store result in `window.__result` and poll with sync evaluate.

## Pitfalls

⚠️ **JANGAN:**
- Simpan token di plain text
- Share token ke orang lain
- Pakai expired token
- Skip error handling
- Buka browser untuk setiap operasi
- **MASK/REDACT matched values** — User sangat tidak suka `...` atau `***` di output. Kirim SEMUA value lengkap, tidak dipotong. Ini berlaku untuk semua findings: secret scanner, token extraction, API discovery. Jika ada concern security, tandai sebagai DEMO/CONTOH tapi tetap tampilkan full value.

✅ **LAKUKAN:**
- Extract sekali, pakai berkali-kali
- Cache tokens ke file
- Encrypt token storage
- Cek expiry JWT
- Refresh token sebelum expire
- Pakai requests/API untuk operasi
- Skip error handling
- Berharap semua token bisa di-extract otomatis (Google/Twitter sangat protektif)

✅ **LAKUKAN:**
- Encrypt token storage
- Cek expiry JWT
- Refresh token sebelum expire
- Test token sebelum pakai
- Backup token ke tempat aman
- Gunakan Camoufox untuk anti-detect
- **Intercept network traffic** untuk capture Bearer token (terbukti berhasil untuk Twitter API)
- **Export cookies manual** untuk Google/Twitter OAuth (lebih reliable dari automation)

## Referensi Detail

- `references/twitter_cookies.md` — Detail Twitter cookies
- `references/token_handling.md` — Cara handle token
- `references/twitter-cookie-extraction.md` — **Panduan lengkap extract Twitter cookies** (termasuk httpOnly auth_token)
- `references/email-verification.md` — **Workflow verifikasi email untuk airdrop**
- `references/github-secret-scanner.md` — **24/7 GitHub secret scanner pattern** — screen setup, pattern matching, Telegram auto-notify, daily report cron

## Teknik yang Terbukti (Session Mei 2026)

### ✅ Twitter Bearer Token via Network Intercept
```python
# Twitter menggunakan public Bearer token untuk API requests
# Bisa di-capture dari network traffic
bearer_token = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCO..."
```

### ✅ Gmail IMAP Token
```python
# App Password bisa langsung digunakan untuk IMAP
# Tidak perlu OAuth token
mail.login("email@gmail.com", "xxxx xxxx xxxx xxxx")
```

### ❌ Google OAuth Token (Tidak Reliable)
Google OAuth sangat sensitif terhadap automasi. Lebih baik gunakan:
1. Manual cookie export
2. App Password untuk layanan Google
3. Developer tools untuk extract token
