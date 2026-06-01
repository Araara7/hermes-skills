---
name: background-browser-workflow
description: Background browser execution workflow — extract tokens/auth/JWT first via Camoufox+xvfb, then use API for remaining tasks. Minimize browser usage.
tags: [browser, background, token, auth, jwt, automation, camoufox]
---

# 🔄 Background Browser Workflow

Workflow: Eksekusi browser di background untuk extract data, lalu pakai API untuk task selanjutnya.

## Browser Options

### nodriver (Anti-detect Chrome — NEW)
```python
import nodriver as uc
CHROME = "/home/ubuntu/.cache/ms-playwright/chromium-*/chrome-linux64/chrome"
browser = await uc.start(headless=True, browser_executable_path=CHROME, browser_args=['--no-sandbox'])
```
- `navigator.webdriver: false` — best anti-detection
- Async CDP-based, no Selenium
- **Pitfall**: async evaluate returns None for Promises — store in `window.__result` and poll
- **Pitfall**: needs `--no-sandbox` on VPS
- Best for: Cloudflare bypass, Twitter actions, anti-detect browsing

### Camoufox (Default — Anti-detect Firefox)
```python
from camoufox.sync_api import Camoufox
with Camoufox(headless=True) as browser:
    page = browser.new_page()
    page.goto(url)
```
- ✅ Anti-fingerprinting, Turnstile bypass
- ❌ WASM captcha FAILS ("JsValue(Promise)")
- ❌ Startup 2-3 menit

### Nodriver (Anti-detect Chromium — NEW)
```python
import nodriver as uc
CHROME = "/home/ubuntu/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome"

browser = await uc.start(
    headless=True,
    browser_executable_path=CHROME,
    browser_args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
)
tab = await browser.get(url)
```
- ✅ `navigator.webdriver: false` — truly undetected
- ✅ Bypass Cloudflare, Imperva
- ✅ Async-first, CDP-based, no Selenium
- ❌ WASM binary gak auto-load (lazy loading)
- ❌ Perlu `--no-sandbox` di VPS
- **Install:** `pip install nodriver` (v0.50+)
- **Chrome path:** `~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome`

### Playwright Chromium (WASM Captcha)
```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
```
- ✅ WASM captcha WORKS
- ❌ `navigator.webdriver: true` — terdeteksi bot

### Best Combo (Hybrid)
| Task | Browser | Why |
|------|---------|-----|
| WASM captcha | Chromium | Satu-satunya yang bisa run WASM |
| Anti-detect browse | Nodriver | `webdriver: false`, bypass CF |
| Turnstile | Camoufox | Built-in bypass |
| Token extraction | Nodriver | Undetected, fast |
| General automation | Camoufox | Anti-fingerprint |

## Prinsip (MANDATORY — User Preference)

1. **ALWAYS check API first** — sebelum buka browser, cek apakah ada API endpoint yang bisa dipakai via curl/requests
2. **Prioritize background/cron** — jika task bisa jalan di background, JANGAN pakai browser interaktif
3. **Camoufox stealth WAJIB** — semua browser task pakai Camoufox (anti-detect), JANGAN pakai Playwright/Chromium biasa
   - **EXCEPTION: WASM captcha** — Galxe WASM captcha FAILS di Camoufox ("JsValue(Promise"), WORKS di Chromium headless. See `galxe-automation` skill.
   - **EXCEPTION: Anti-detect needed** — Use `nodriver` for stronger anti-detection (Cloudflare, Imperva bypass). See `unified-auth-manager` skill.
4. **User-Agent rotation** — setiap session baru, generate user-agent baru. JANGAN pernah request tanpa User-Agent
5. **Browser hanya untuk inisialisasi** — login, extract token, cookies, lalu TUTUP browser
6. **API untuk operasi** — setelah dapat token, pakai API langsung
7. **Minimize browser** — hemat resource, lebih cepat, lebih aman
8. **JANGAN spam Telegram saat kerja** — diam, eksekusi, kirim hasil akhir aja

### Mandatory Pre-Flight Checklist
Sebelum setiap task, WAJIB lakukan:
```
□ Cek API endpoint tersedia? (curl test)
□ Bisa pakai cron/background? (jika ya → skip browser)
□ Camoufox terinstall? (bukan Playwright biasa)
□ User-Agent sudah di-set? (jangan pernah kosong)
□ Token/auth di-cache? (jangan extract ulang)
```

## Workflow Template

### Step 1: Background Browser (Extract Data)

```python
import json
import time
from pathlib import Path
from camoufox.sync_api import Camoufox

def extract_auth_data(url, actions=None):
    """
    Extract tokens/cookies/auth from website via background browser
    
    Args:
        url: Target URL
        actions: List of actions to perform (click, fill, etc)
    
    Returns:
        dict with extracted tokens, cookies, auth data
    """
    
    COOKIES_DIR = Path.home() / "airdrop-agent" / "data" / "tokens"
    COOKIES_DIR.mkdir(parents=True, exist_ok=True)
    
    captured = {
        "tokens": [],
        "cookies": [],
        "localStorage": {},
        "requests": []
    }
    
    def handle_request(request):
        """Capture auth headers"""
        headers = request.headers
        
        if "authorization" in headers:
            captured["tokens"].append({
                "type": "authorization",
                "value": headers["authorization"][:200],
                "url": request.url[:100]
            })
        
        for key in ["x-csrf-token", "x-auth-token", "x-api-key"]:
            if key in headers:
                captured["tokens"].append({
                    "type": key,
                    "value": headers[key][:100],
                    "url": request.url[:80]
                })
    
    def handle_response(response):
        """Capture response tokens"""
        url = response.url
        
        if any(x in url.lower() for x in ['token', 'auth', 'session', 'login']):
            try:
                if 'json' in response.headers.get('content-type', ''):
                    body = response.json()
                    if isinstance(body, dict):
                        for key in ['token', 'access_token', 'jwt', 'refresh_token']:
                            if key in body:
                                captured["tokens"].append({
                                    "type": key,
                                    "value": body[key][:200],
                                    "url": url[:80]
                                })
            except:
                pass
    
    with Camoufox(headless=True) as browser:
        context = browser.new_context()
        page = context.new_page()
        
        # Setup interception
        page.on("request", handle_request)
        page.on("response", handle_response)
        
        # Navigate
        page.goto(url)
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        
        # Perform actions if specified
        if actions:
            for action in actions:
                if action["type"] == "click":
                    page.locator(action["selector"]).first.click()
                    time.sleep(action.get("wait", 2))
                elif action["type"] == "fill":
                    page.locator(action["selector"]).first.fill(action["value"])
                    time.sleep(action.get("wait", 1))
                elif action["type"] == "wait":
                    time.sleep(action["seconds"])
        
        # Extract cookies
        cookies = context.cookies()
        captured["cookies"] = cookies
        
        # Extract localStorage
        captured["localStorage"] = page.evaluate("""
            () => {
                const data = {};
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    data[key] = localStorage.getItem(key);
                }
                return data;
            }
        """)
        
        # Save captured data
        domain = url.split("//")[1].split("/")[0].replace(".", "_")
        output_file = COOKIES_DIR / f"{domain}_auth.json"
        
        with open(output_file, "w") as f:
            json.dump(captured, f, indent=2)
        
        return captured
```

### Step 2: Use API with Extracted Data

```python
import requests

def use_api(base_url, auth_data, endpoint, method="GET", data=None):
    """Use API with extracted auth data"""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0"
    }
    
    # Add auth headers from captured data
    cookies = {}
    for token in auth_data.get("tokens", []):
        if token["type"] == "authorization":
            headers["Authorization"] = token["value"]
        elif token["type"] == "x-csrf-token":
            headers["x-csrf-token"] = token["value"]
    
    # Add cookies
    for cookie in auth_data.get("cookies", []):
        cookies[cookie["name"]] = cookie["value"]
    
    # Make request
    if method == "GET":
        resp = requests.get(f"{base_url}{endpoint}", headers=headers, cookies=cookies)
    elif method == "POST":
        resp = requests.post(f"{base_url}{endpoint}", headers=headers, cookies=cookies, json=data)
    
    return resp
```

## Contoh Penggunaan

### Twitter: Extract lalu Pakai API

```python
# Step 1: Extract Twitter auth (sudah dilakukan)
twitter_auth = {
    "tokens": [{"type": "authorization", "value": "Bearer AAA..."}],
    "cookies": [{"name": "auth_token", "value": "5c433f..."}, {"name": "ct0", "value": "3636..."}]
}

# Step 2: Pakai API langsung (tanpa browser)
def search_airdrops(query):
    headers = {
        "Authorization": "Bearer AAA...",
        "x-csrf-token": "3636..."
    }
    cookies = {"auth_token": "5c433f...", "ct0": "3636..."}
    
    resp = requests.get(
        f"https://api.x.com/2/search/recent?query={query}",
        headers=headers,
        cookies=cookies
    )
    return resp.json()
```

### Website Airdrop: Extract Token lalu Automasi

```python
# Step 1: Background browser - extract JWT
auth_data = extract_auth_data(
    "https://airdrop.example.com",
    actions=[
        {"type": "fill", "selector": "input[type=email]", "value": "otamaagent7@gmail.com"},
        {"type": "click", "selector": "button:has-text('Submit')", "wait": 3}
    ]
)

# Step 2: Pakai JWT untuk API calls
jwt_token = [t for t in auth_data["tokens"] if t["type"] == "jwt"][0]["value"]

# Complete tasks via API (no browser needed)
resp = requests.post(
    "https://airdrop.example.com/api/complete-task",
    headers={"Authorization": f"Bearer {jwt_token}"},
    json={"task_id": "follow_twitter"}
)
```

## Script Template

```python
#!/usr/bin/env python3
"""
Template: Background Browser + API Automation
"""

import json
import requests
from pathlib import Path

# Config
TARGET_URL = "https://example.com/airdrop"
EMAIL = "otamaagent7@gmail.com"
COOKIES_FILE = Path.home() / "airdrop-agent" / "data" / "tokens" / "example_auth.json"

def main():
    # Step 1: Check if we have cached auth
    if COOKIES_FILE.exists():
        print("📦 Using cached auth data")
        with open(COOKIES_FILE) as f:
            auth_data = json.load(f)
    else:
        print("🌐 Extracting auth via browser...")
        auth_data = extract_auth_data(TARGET_URL)
    
    # Step 2: Use API with auth
    print("🔄 Performing tasks via API...")
    
    # Example: Complete task
    jwt = extract_jwt(auth_data)
    if jwt:
        resp = requests.post(
            f"{TARGET_URL}/api/task/complete",
            headers={"Authorization": f"Bearer {jwt}"},
            json={"task": "daily_checkin"}
        )
        print(f"✅ Task result: {resp.status_code}")

if __name__ == "__main__":
    main()
```

## Checklist

- [ ] Browser hanya untuk extract data awal
- [ ] Simpan token/cookies ke file
- [ ] Pakai API untuk operasi selanjutnya
- [ ] Cache auth data (jangan extract ulang)
- [ ] Handle token expiry

## Pitfalls

⚠️ **JANGAN:**
- Buka browser untuk setiap operasi
- Skip token caching
- Pakai browser untuk API calls
- Lupa User-Agent header (API akan blokir)
- **Asumsikan semua Web3 app = wallet connection** — banyak yang pakai email waitlist (e.g., Umbra Privacy)

✅ **LAKUKAN:**
- Extract sekali, pakai berkali-kali
- Cache tokens ke file
- Pakai requests/API untuk task
- Refresh token sebelum expired
- Selalu set User-Agent di curl/requests
- Selalu set User-Agent di curl/requests
- OTP input: gunakan `keyboard.press()` per digit, bukan `fill()`
- Tombol terhalang modal: gunakan `page.evaluate()` + `element.click()` via JS
- **Test API via curl dulu** sebelum buka browser (hemat rate limit)

## OTP / Segmented Input Pattern

Many sites use 6-box OTP input (`input[maxlength="1"]`). `fill()` does NOT work — OTP libraries listen for `keydown` events, not value changes.

```python
first_input = page.locator("input[aria-label='Character 1 of 6']").first
first_input.click(force=True)
time.sleep(0.3)
for digit in code:
    page.keyboard.press(digit)
    time.sleep(0.2)
```

## Behind-Modal Button Click

When Playwright reports "subtree intercepts pointer events", use JS direct click:

```python
page.evaluate("""() => {
    const buttons = document.querySelectorAll('button');
    for (const b of buttons) {
        if (b.textContent.includes('Target Text')) {
            b.click();
            return true;
        }
    }
    return false;
}""")
```

## Storage Locations

Different platforms store auth data in different places:

| Platform | Storage | Key |
|----------|---------|-----|
| JAY Games | sessionStorage | `jay_games_wallet` |
| Twitter | cookies | `auth_token`, `ct0` |
| Gmail | cookies | `SID`, `SSID`, `HSID` |
| Generic | localStorage | varies |

**Important:** sessionStorage is per-tab and cleared when tab closes. localStorage persists across sessions.

## QR Code Wallet Connection Pattern

Many Web3 games use QR code for wallet connection:

```python
# 1. Create QR session
qr = requests.get("https://games.example.com/api.php?api=qr_create", 
                   headers={"User-Agent": UA}).json()
session_id = qr["session_id"]

# 2. Poll for connection (user scans QR on mobile)
while True:
    status = requests.get(f"https://games.example.com/api.php?api=qr_poll&sid={session_id}",
                         headers={"User-Agent": UA}).json()
    if status["status"] == "connected":
        wallet = status["wallet"]
        break
    time.sleep(2)

# 3. Use wallet for API calls
stats = requests.get(f"https://games.example.com/api.php?api=stats&wallet={wallet}",
                     headers={"User-Agent": UA}).json()
```
