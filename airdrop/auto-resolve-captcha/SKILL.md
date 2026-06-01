---
name: auto-resolve-captcha
description: Auto solve CAPTCHA (reCAPTCHA, hCaptcha, Turnstile, FunCaptcha) using 2captcha, CapSolver, AntiCaptcha APIs
tags: [airdrop, captcha, automation, web3]
---

# 🔓 Auto Resolve CAPTCHA

Solve CAPTCHA otomatis untuk task airdrop menggunakan third-party solving service.

## Supported CAPTCHA Types

| Type | Service | Harga |
|------|---------|-------|
| reCAPTCHA v2 | 2captcha, CapSolver | $2-3/1000 |
| reCAPTCHA v3 | 2captcha, CapSolver | $3-5/1000 |
| hCaptcha | 2captcha, CapSolver | $3-4/1000 |
| Cloudflare Turnstile | CapSolver, **Camoufox (GRATIS)** | $2-3/1000 atau **$0** |
| FunCaptcha | 2captcha, AntiCaptcha | $2-3/1000 |
| **GeeTest v4** | **2captcha, CapSolver** | **$3-4/1000** |
| **Galxe WASM** | **Chromium headless (GRATIS!)** | **$0** |
| FunCaptcha | 2captcha, AntiCaptcha | $2-3/1000 |

## 2captcha Integration

### Setup
```python
import requests
import time

TWOCAPTCHA_API_KEY = "YOUR_API_KEY"
BASE_URL = "https://2captcha.com"

def solve_recaptcha_v2(site_key, page_url):
    """Solve reCAPTCHA v2"""
    # Submit task
    submit_url = f"{BASE_URL}/in.php"
    data = {
        "key": TWOCAPTCHA_API_KEY,
        "method": "userrecaptcha",
        "googlekey": site_key,
        "pageurl": page_url,
        "json": 1
    }
    
    resp = requests.post(submit_url, data=data).json()
    if resp["status"] != 1:
        raise Exception(f"Submit failed: {resp}")
    
    task_id = resp["request"]
    
    # Poll for result
    result_url = f"{BASE_URL}/res.php"
    for _ in range(60):  # max 2 minutes
        time.sleep(2)
        result = requests.get(result_url, params={
            "key": TWOCAPTCHA_API_KEY,
            "action": "get",
            "id": task_id,
            "json": 1
        }).json()
        
        if result["status"] == 1:
            return result["request"]
        
        if result["request"] != "CAPCHA_NOT_READY":
            raise Exception(f"Solve failed: {result}")
    
    raise Exception("Timeout")
```

### Solve hCaptcha
```python
def solve_hcaptcha(site_key, page_url):
    """Solve hCaptcha"""
    submit_url = f"{BASE_URL}/in.php"
    data = {
        "key": TWOCAPTCHA_API_KEY,
        "method": "hcaptcha",
        "sitekey": site_key,
        "pageurl": page_url,
        "json": 1
    }
    
    resp = requests.post(submit_url, data=data).json()
    task_id = resp["request"]
    
    # Same polling logic as above
    return poll_result(task_id)
```

## CapSolver Integration

```python
import requests

CAPSOLVER_API_KEY = "YOUR_API_KEY"

def solve_with_capsolver(task_type, website_url, website_key):
    """Generic CapSolver solver"""
    
    # Create task
    create_url = "https://api.capsolver.com/createTask"
    task = {
        "type": task_type,  # "ReCaptchaV2Task", "HCaptchaTask", etc.
        "websiteURL": website_url,
        "websiteKey": website_key,
    }
    
    payload = {
        "clientKey": CAPSOLVER_API_KEY,
        "task": task
    }
    
    resp = requests.post(create_url, json=payload).json()
    if resp["errorId"] != 0:
        raise Exception(f"Error: {resp}")
    
    task_id = resp["taskId"]
    
    # Get result
    result_url = "https://api.capsolver.com/getTaskResult"
    for _ in range(60):
        time.sleep(2)
        result = requests.post(result_url, json={
            "clientKey": CAPSOLVER_API_KEY,
            "taskId": task_id
        }).json()
        
        if result["status"] == "ready":
            return result["solution"]
        
        if result["errorId"] != 0:
            raise Exception(f"Error: {result}")
    
    raise Exception("Timeout")
```

## Browser Integration (Playwright)

```python
async def fill_captcha_and_submit(page, site_key, page_url):
    """Fill CAPTCHA token and submit form"""
    
    # Solve CAPTCHA
    token = solve_recaptcha_v2(site_key, page_url)
    
    # Inject token
    await page.evaluate(f'''
        document.getElementById("g-recaptcha-response").value = "{token}";
        // For invisible captcha
        if (typeof ___grecaptcha_cfg !== "undefined") {{
            Object.keys(___grecaptcha_cfg.clients).forEach(key => {{
                const client = ___grecaptcha_cfg.clients[key];
                // Find callback
                const findCallback = (obj) => {{
                    for (let prop in obj) {{
                        if (typeof obj[prop] === "function" && prop.length > 10) {{
                            obj[prop]("{token}");
                        }}
                        if (typeof obj[prop] === "object") {{
                            findCallback(obj[prop]);
                        }}
                    }}
                }};
                findCallback(client);
            }});
        }}
    ''')
    
    # Click submit
    await page.click('button[type="submit"]')
```

## GeeTest v4 Integration

Used by: **Galxe** (quest claims), some Chinese Web3 platforms.

```python
def solve_geetest_v4(site_url, captcha_id):
    """Solve GeeTest v4 via 2captcha"""
    # Submit
    resp = requests.post("https://2captcha.com/in.php", data={
        "key": TWOCAPTCHA_API_KEY,
        "method": "geetest_v4",
        "geetestid": captcha_id,
        "pageurl": site_url,
        "json": 1
    }).json()
    
    task_id = resp["request"]
    
    # Poll
    for _ in range(60):
        time.sleep(3)
        result = requests.get("https://2captcha.com/res.php", params={
            "key": TWOCAPTCHA_API_KEY, "action": "get", "id": task_id, "json": 1
        }).json()
        if result["status"] == 1:
            return result["request"]  # {lot_number, captcha_output, pass_token, gen_time}
    raise Exception("GeeTest timeout")
```

**CapSolver task type**: `GeeTestTaskProxyLess`

See `galxe-automation` skill for full Galxe claim integration.

## Service Providers

| Service | API | Harga | Speed |
|---------|-----|-------|-------|
| 2captcha | REST | $2.99/1k | 15-60s |
| CapSolver | REST | $2.50/1k | 5-30s |
| AntiCaptcha | REST | $2/1k | 10-40s |
| DeathByCaptcha | REST | $1.39/1k | 15-90s |

## GeeTest v4 (Galxe Claim — LEGACY, pre Jun 2026)

⚠️ **Galxe migrated to WASM captcha (Jun 2026).** GeeTest v4 no longer works for Galxe claims. See `galxe-automation` skill for WASM captcha details. GeeTest v4 info below is for other platforms still using it.

## Galxe WASM Captcha (Jun 2026+)

Galxe now uses a Rust→WASM captcha instead of GeeTest v4. **Can be solved locally with Chromium headless** (no third-party API needed).

**Key insight:** Camoufox FAILS (anti-fingerprinting breaks WASM), but Playwright Chromium headless WORKS. Nodriver also FAILS for WASM (binary doesn't auto-load — lazy loading), but is best for anti-detect browsing.

**Browser selection for captcha:**
| Browser | WASM | Turnstile | Anti-detect |
|---------|------|-----------|-------------|
| Chromium | ✅ | ❌ | ❌ |
| Camoufox | ❌ | ✅ | ✅ |
| Nodriver | ❌ | ❌ | ✅✅ |

```python
# Quick solve via galxe_captcha_solver.py
from galxe_captcha_solver import GalxeCaptchaSolver
solver = GalxeCaptchaSolver()
await solver.init()  # Load Galxe page + scripts in Chromium
captcha = await solver.solve("PrepareParticipate")
# Returns: {ok, lotNumber, captchaOutput, passToken, genTime, encryptedData}
await solver.close()
```

Script: `~/airdrop-agent/scripts/galxe_captcha_solver.py`

### WASM Captcha Parsing (Pitfall!)
Output is **multiline JSON** (not single-line). Parse with regex:
```python
import re, json
# Method 1: regex
match = re.search(r'\{[^{}]*"lotNumber"[^{}]*\}', stdout, re.DOTALL)
captcha = json.loads(match.group())

# Method 2: line-by-line
lines = stdout.split('\n')
json_lines, in_json = [], False
for line in lines:
    if line.strip().startswith('{'): in_json = True
    if in_json: json_lines.append(line)
    if in_json and line.strip().endswith('}'):
        captcha = json.loads('\n'.join(json_lines)); break
```

### CaptchaInput Schema (Galxe GraphQL)
Fields: `lotNumber` (String!), `captchaOutput` (String!), `passToken` (String!), `genTime` (String!), `encryptedData` (String).
⚠️ **NO `ok` field** — solver output has `ok: true` but Galxe rejects it. Strip before sending:
```python
captcha = {k: raw[k] for k in ["lotNumber","captchaOutput","passToken","genTime","encryptedData"] if k in raw}
```

### Galxe Social Task Verification Flow
Twitter tasks use `syncCredentialValue` with `twitter` field:
```python
gql("""mutation SyncCredentialValue($input: SyncCredentialValueInput!) {
    syncCredentialValue(input: $input) { message value { allow } }
}""", {
    "input": {
        "syncOptions": {
            "credId": cred_id,
            "address": f"EVM:{address}",
            "twitter": {
                "captcha": captcha,      # CaptchaInput (required!)
                "campaignID": campaign_id  # ID! (required!)
            }
        }
    }
}, token)
```
Without `twitter` field → `"missing twitter args"` error.
Without `captcha` inside twitter → `"must be defined"` error.

### Mock Mode Detection
Check `twitterOauth2Status` query:
```python
r = gql("""query { twitterOauth2Status {
    oauthRateLimited activeTokenDepleted serviceDown
    mockFollow mockLike mockRetweet mockQuote
}}""", token=token)
```
`mockFollow: true` = Galxe not actually checking Twitter API (mock mode).
**BUT**: mock mode does NOT bypass expired OAuth token validation!
If connected Twitter's OAuth2 token is expired → `allow: false` even in mock mode.
This is the #1 reason for silent `allow: false` with no error message.

### Galxe Social Account Management API
```graphql
# Get OAuth URL for connecting social account
query { getSocialAuthUrl(schema: "https://app.galxe.com", type: TWITTER) }
# Disconnect social account
mutation { deleteSocialAccount(input: {address, type: TWITTER, sig}) }
# Check connected Twitter
query { addressInfo(address: "EVM:0x...") { twitterUserID twitterUserName hasTwitter } }
# Verify with OAuth2 token directly
mutation { VerifyTwitterOauth2Token(input: {address, token}) }
```

**⚠️ CRITICAL: `deleteSocialAccount` is a SCHEMA GHOST.** The mutation exists in `__schema` introspection but ALL calls return `GRAPHQL_VALIDATION_FAILED`. Tested every format. NOT callable via public API.

**⚠️ `getSocialAuthUrl` requires browser session JWT**, NOT the API `signin` JWT. Returns "Invalid JWT token" from curl/requests.

**Result: Social account switching CANNOT be done programmatically.** User must manually disconnect/reconnect in browser.

Full API reference: `references/galxe-social-api.md`

### GeeTest v4 Flow (gcaptcha4.geetest.com)
(Source: `C0mbustibll/galxe_claimer` ⭐53)

### GeeTest v4 Flow (gcaptcha4.geetest.com)
```python
from uuid import uuid4
import time, requests, json

GEETEST_ID = "244bcb8b9846215df5af4c624a750db4"
call = int(time.time() * 1e3)

# Step 1: Load challenge
resp = requests.get('https://gcaptcha4.geetest.com/load', params={
    'captcha_id': GEETEST_ID, 'challenge': str(uuid4()),
    'client_type': 'web', 'lang': 'et', 'callback': f'geetest_{call}',
})
js_data = json.loads(resp.text.strip(f'geetest_{call}(').strip(')'))['data']

# Step 2: Verify with W (solution from solver)
resp2 = requests.get('https://gcaptcha4.geetest.com/verify', params={
    'captcha_id': GEETEST_ID, 'client_type': 'web',
    'lot_number': js_data['lot_number'], 'payload': js_data['payload'],
    'process_token': js_data['process_token'],
    'payload_protocol': '1', 'pt': '1', 'w': W, 'callback': f'geetest_{call}',
})
completed = json.loads(resp2.text.strip(f'geetest_{call}(').strip(')'))['data']
# completed has: lot_number, seccode.{captcha_output, pass_token, gen_time}
```

### Solve W via 2captcha
```python
resp = requests.post("https://api.2captcha.com/createTask", json={
    "clientKey": API_KEY,
    "task": {"type": "GeeTestTaskProxyless", "websiteURL": "https://app.galxe.com",
             "gt": "244bcb8b9846215df5af4c624a750db4", "version": 4}
}).json()
# Poll getTaskResult → solution: {lot_number, captcha_output, pass_token, gen_time}
```

### Solve W via CapSolver
```python
resp = requests.post("https://api.capsolver.com/createTask", json={
    "clientKey": API_KEY,
    "task": {"type": "GeeTestTaskProxyLess", "websiteURL": "https://app.galxe.com",
             "gt": "244bcb8b9846215df5af4c624a750db4", "version": 4}
}).json()
# Poll getTaskResult → solution: {captcha_id, lot_number, pass_token, gen_time, captcha_output}
```

### Map ke Galxe CaptchaInput
- `lotNumber` ← `solution.lot_number`
- `captchaOutput` ← `solution.captcha_output`
- `passToken` ← `solution.pass_token`
- `genTime` ← `solution.gen_time`

### References
- `C0mbustibll/galxe_claimer` — complete GeeTest + Galxe claim flow (Python)
- Galxe GraphQL: `__type(name: "CaptchaInput")` for field discovery

## Cloudflare Turnstile via Camoufox (GRATIS, tanpa API key!)

**Turnstile bisa di-solve lokal** menggunakan Camoufox anti-detection browser. Tidak perlu third-party API.

### Cara Kerja
Camoufox adalah Firefox-based anti-detection browser yang bisa melewati Turnstile secara internal. Turnstile mengecek browser fingerprint + behavior — Camoufox meniru manusia dengan sempurna.

### Dua Metode Solve

#### Method 1: Direct Widget (Standalone)
Render Turnstile widget di halaman HTML kosong, ambil token:
```python
from camoufox.sync_api import Camoufox
import time

def solve_turnstile_camoufox(url, sitekey, timeout=30):
    html = f'''<!DOCTYPE html>
    <html><head><script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async></script></head>
    <body><div class="cf-turnstile" data-sitekey="{sitekey}"></div></body></html>'''
    
    browser = Camoufox(headless=True).start()
    page = browser.new_page()
    page.route(url + "/", lambda route: route.fulfill(body=html, status=200))
    page.goto(url + "/")
    
    for _ in range(timeout):
        inp = page.query_selector("[name=cf-turnstile-response]")
        if inp and inp.get_attribute("value"):
            token = inp.get_attribute("value")
            browser.close()
            return token
        time.sleep(1)
    
    browser.close()
    return None
```

Script: `~/airdrop-agent/scripts/turnstile_solver.py`

#### Method 2: Privy SDK Internal (Recommended untuk Web3 apps)
Privy SDK menangani Turnstile secara internal — cukup gunakan Camoufox untuk navigate + interact:
```python
from camoufox.sync_api import Camoufox

browser = Camoufox(headless=True).start()
page = browser.new_page()
page.goto("https://target-site.com/play", wait_until="commit", timeout=60000)
time.sleep(8)

# Click Login → enter email → Privy SDK handles Turnstile internally!
page.locator("button:has-text('Login')").first.click(timeout=5000)
time.sleep(4)

# Find email input in Privy iframe
for frame in page.frames:
    inp = frame.query_selector("input[type='email']")
    if inp and inp.is_visible():
        inp.fill("user@email.com")
        inp.press("Enter")  # Turnstile solved automatically!
        break

# OTP sent to email, retrieve via himalaya/imap
```

**Kelebihan:** Tidak perlu sitekey, tidak perlu API key, Turnstile solved otomatis oleh Privy SDK.
**Kekurangan:** Hanya works untuk app yang pakai Privy auth.

### Known Pitfalls

#### ⚠️ Domain Mismatch (CRITICAL!)
Turnstile token **terikat domain**. Jika solve di domain A, token TIDAK bisa dipakai di domain B:
```
❌ Solve di "localhost" → token untuk localhost
❌ Pakai token di "pixiechess.xyz" → REJECTED

✅ Solve di "pixiechess.xyz" → token untuk pixiechess.xyz
✅ Pakai token di "pixiechess.xyz" → ACCEPTED
```

**Fix:** Selalu solve Turnstile di domain target yang sama. Jangan render widget di halaman kosong lalu pakai token di site lain.

#### ⚠️ Sitekey Discovery
Turnstile sitekey bisa ditemukan di:
1. HTML: `data-sitekey="0x4AAAAAAA..."`
2. JS bundle: search `0x4AAAAAAA` di assets/*.js
3. Network: intercept Turnstile API calls

#### ⚠️ Camoufox Startup Time
Camoufox butuh **2-3 menit** untuk startup pertama. Jangan kill process terlalu awal.

#### ⚠️ Headless Detection
Turnstile bisa detect headless browser biasa. Camoufox dirancang khusus untuk bypass ini. **Jangan gunakan Playwright/Chromium biasa** untuk Turnstile.

## Local CAPTCHA Solving (Tanpa Third-Party)

**Bisa lokal:**
- Text/Image CAPTCHA → Tesseract OCR
- Simple math CAPTCHA → Regex parsing
- Slide CAPTCHA → OpenCV image detection
- **Cloudflare Turnstile → Camoufox (GRATIS!)** ← NEW

**Tidak bisa lokal (butuh ML/training):**
- reCAPTCHA v2/v3 → Behavioral analysis + browser fingerprint
- hCaptcha → Advanced ML detection
- FunCaptcha → Image recognition challenges

### Tesseract OCR (Text CAPTCHA)
```bash
apt-get install tesseract-ocr
pip install pytesseract pillow
```

```python
import pytesseract
from PIL import Image

def solve_text_captcha(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, config='--psm 7')
    return text.strip()
```

**Realita:** Modern CAPTCHAs (reCAPTCHA, hCaptcha) dirancang untuk tidak bisa di-solve lokal. Butuh ribuan training images + GPU. Third-party service ($2-3/1000) lebih murah daripada setup GPU server.

## Scripts
- `~/airdrop-agent/scripts/turnstile_solver.py` — Cloudflare Turnstile solver via Camoufox (standalone + Privy mode)

## Nodriver + Captcha Combo (Jun 2026)

Best approach: **nodriver** for anti-detect navigation + **Chromium** for WASM captcha.

```python
# 1. Navigate with nodriver (undetected)
import nodriver as uc
browser = await uc.start(headless=True, browser_executable_path=CHROME, browser_args=['--no-sandbox'])
tab = await browser.get("https://target-site.com")
# navigator.webdriver = false ✅

# 2. Solve captcha with Chromium (separate process)
import subprocess
result = subprocess.run(['python3', 'scripts/galxe_captcha_solver.py'], capture_output=True, text=True, timeout=90)
captcha = parse_captcha_output(result.stdout)

# 3. Use captcha in API call
requests.post(api_url, json={"captcha": captcha}, headers={"Authorization": token})
```

**Why hybrid:** nodriver can't run WASM captcha (lazy loading), Chromium can't bypass bot detection. Together = 100% coverage.

- [ ] API key terisi
- [ ] Balance mencukupi
- [ ] Test solve manual dulu
- [ ] Handle timeout/error
- [ ] Log solve rate

## Pitfalls

⚠️ **JANGAN:**
- Solve terlalu cepat (deteksi bot)
- Skip error handling
- Lupa cek balance API

✅ **LAKUKAN:**
- Delay antar solve
- Rotate solver service jika error
- Monitor success rate
- Fallback ke manual jika gagal

## Tool Comparison for Captcha Solving

| Captcha Type | Best Tool | Fallback |
|--------------|-----------|----------|
| Galxe WASM | Chromium (Playwright) | 2captcha/CapSolver |
| Cloudflare Turnstile | Camoufox | nodriver |
| reCAPTCHA v2/v3 | 2captcha/CapSolver | - |
| hCaptcha | 2captcha/CapSolver | - |
| GeeTest v4 | 2captcha/CapSolver | - |
| FunCaptcha | 2captcha/AntiCaptcha | - |
| Generic image | Tesseract OCR | - |

**For Cloudflare-heavy sites:** Use `nodriver` (anti-detect, bypasses Turnstile). See `unified-auth-manager` skill for nodriver integration.
