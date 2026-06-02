---
name: unified-auth-manager
description: "Unified auth manager — autonomous token/auth extraction untuk semua platform. Gabungkan SIWE, cookies, API keys, captcha solving jadi satu flow terpadu."
tags: [airdrop, auth, token, automation, unified, autonomous, web3]
triggers:
  - auth
  - login
  - token
  - authenticate
  - session
  - credentials
---

# 🔐 Unified Auth Manager

Manager terpadu untuk semua autentikasi — autonomous tanpa login manual dimana bisa, semi-autonomous untuk platform yang protektif.

## User Preferences (WAJIB DIIKUTI)
- **Hacker mode:** Exploit, bypass, jangan pernah nyerah. Gak ada "gak bisa", cuma "belum nemu cara-nya."
- **No spam:** JANGAN kirim feedback Telegram saat sedang kerja. Diam, eksekusi, kirim hasil akhir aja.
- **Autonomous:** Eksekusi langsung, jangan tanya balik kecuali benar-benar perlu.

## Architecture

```
┌─────────────────────────────────────────────┐
│           UNIFIED AUTH MANAGER              │
├─────────────────────────────────────────────┤
│  CredentialStore (JSON, chmod 600)          │
│  ├── config/credentials/accounts.json       │
│  ├── config/credentials/galxe_token.json    │
│  ├── config/credentials/twitter_session.json│
│  ├── config/credentials/pixiechess_auth.json│
│  └── config/credentials/.env                │
├─────────────────────────────────────────────┤
│  Platform Adapters                          │
│  ├── EVMWalletAdapter    (fully autonomous) │
│  ├── GalxeAdapter        (fully autonomous) │
│  ├── JAYGamesAdapter     (fully autonomous) │
│  ├── TwitterAdapter      (semi-autonomous)  │
│  ├── GmailAdapter        (semi-autonomous)  │
│  ├── DiscordAdapter      (semi-autonomous)  │
│  └── GenericWeb3Adapter  (auto-detect)      │
├─────────────────────────────────────────────┤
│  CaptchaSolver                              │
│  ├── WASM (Chromium)     — Galxe, GRATIS   │
│  ├── Turnstile (Camoufox) — CF, GRATIS     │
│  └── ThirdParty (2captcha) — fallback, $   │
├─────────────────────────────────────────────┤
│  TokenManager                               │
│  ├── validate(token)     — check expiry     │
│  ├── refresh(token)      — auto-refresh     │
│  ├── save(platform, data) — encrypt+store   │
│  └── load(platform)      — decrypt+load     │
└─────────────────────────────────────────────┘
```

## Browser Options for Auth

| Browser | Best For | Anti-detect | WASM |
|---------|----------|-------------|------|
| Camoufox | Turnstile, general stealth | ✅✅ | ❌ |
| Nodriver | Token extract, Cloudflare bypass | ✅✅ | ❌ |
| Chromium | WASM captcha only | ❌ | ✅ |

### Nodriver Setup (Anti-detect Chromium)
```python
import nodriver as uc
CHROME = "/home/ubuntu/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome"

browser = await uc.start(
    headless=True,
    browser_executable_path=CHROME,
    browser_args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
)
# navigator.webdriver = False ✅ — truly undetected
```
- **Install:** `pip install nodriver` (v0.50+)
- **Chrome path:** `~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome`
- **Best for:** Twitter token extraction, Cloudflare-protected sites, anti-detect browsing

## Workflow Style (User Preference)

**Hacker mode:** Cari akal, exploit, bypass, jangan pernah nyerah. Autonomous total, creative bypass, stealth.

Rules:
1. **API first** — reverse engineer dulu, baru browser
2. **No spam** — diam saat kerja, cuma kirim hasil akhir
3. **Exploit celah** — mock mode, validation gap, API weakness

## Platform Auth Classification

### Tier 1: Fully Autonomous (tanpa input user)
| Platform | Method | Credential Needed | Auto-Refresh |
|----------|--------|-------------------|--------------|
| EVM Wallets | Private key → sign | master_seed atau private_key | N/A |
| Galxe | SIWE sign → JWT | private_key | ✅ (re-sign) |
| JAY Games | API session + wallet | private_key | ✅ (re-session) |
| Cosmos Wallets | Private key → sign | master_seed | N/A |
| Solana Wallets | Private key → sign | master_seed | N/A |

### Tier 2: Semi-Autonomous (1x manual setup)
| Platform | Method | Block Reason | Workaround |
|----------|--------|--------------|------------|
| Twitter | Cookies export | Phone verification dari VPS IP | User export cookies 1x |
| Gmail | App Password | Google blocks automated login | User generate App Password 1x |
| Discord | Cookies export | 2FA + captcha | User export cookies 1x |
| Telegram | API session | Phone verification | User login 1x via browser |

### Tier 3: Third-Party Service (bayar)
| Platform | Method | Harga |
|----------|--------|-------|
| reCAPTCHA v2/v3 | 2captcha/CapSolver | $2-3/1000 |
| hCaptcha | 2captcha/CapSolver | $3-4/1000 |
| FunCaptcha | 2captcha/AntiCaptcha | $2-3/1000 |

## Credential Store

### Structure
```json
// ~/airdrop-agent/config/credentials/accounts.json
{
  "email": {
    "address": "otamaagent7@gmail.com",
    "app_password": "xxxx xxxx xxxx xxxx",
    "imap_host": "imap.gmail.com",
    "smtp_host": "smtp.gmail.com",
    "status": "active",
    "last_check": "2026-06-01T10:00:00Z"
  },
  "twitter": {
    "username": "@otama777A",
    "user_id": "2059872573077561345",
    "auth_token": "5c433f...",
    "ct0": "3a6090...",
    "bearer_token": "AAAAAAAAAAAAAAAAAAAAANRILg...",
    "status": "active",
    "last_check": "2026-06-01T10:00:00Z"
  },
  "discord": {
    "username": "...",
    "token": "...",
    "status": "active"
  },
  "wallet": {
    "address": "0xb01Eaede24ad33b820f8c1bD35eA9324230Ede3E",
    "private_key_ref": "wallets.json:master_seed",
    "status": "active"
  },
  "galxe": {
    "username": "Aphrodite7",
    "wallet_address": "0xb01Eaede24ad33b820f8c1bD35eA9324230Ede3E",
    "token_file": "galxe_token.json",
    "status": "active"
  },
  "captcha": {
    "twocaptcha_key": "",
    "capsolver_key": "",
    "local_solver": "chromium_wasm",
    "status": "active"
  }
}
```

### Security Rules
```bash
chmod 600 ~/airdrop-agent/config/credentials/*.json
chmod 600 ~/airdrop-agent/config/credentials/.env
# NEVER commit to git
echo "*.json" >> ~/airdrop-agent/.gitignore
echo ".env" >> ~/airdrop-agent/.gitignore
```

## Auto-Auth Functions

### EVM Wallet (Fully Autonomous)
```python
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from eth_account import Account

def get_evm_wallet():
    """Derive EVM wallet from master seed — FULLY AUTONOMOUS"""
    with open("config/wallets.json") as f:
        data = json.load(f)
    seed_bytes = Bip39SeedGenerator(data['master_seed']).Generate()
    bip44 = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
    acc = bip44.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
    return acc.PrivateKey().Raw().ToHex(), acc.PublicKey().ToAddress()

def sign_message(private_key, message):
    """Sign arbitrary message with EVM key"""
    from eth_account.messages import encode_defunct
    msg = encode_defunct(text=message)
    signed = Account.sign_message(msg, private_key)
    return "0x" + signed.signature.hex()
```

### Galxe Auth (Fully Autonomous — SIWE)
```python
import time, random, string, requests

def galxe_auth(address, priv_key):
    """Galxe SIWE auth → JWT token — FULLY AUTONOMOUS"""
    nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=17))
    ts = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
    exp = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(time.time() + 7*24*3600))

    siwe = f"app.galxe.com wants you to sign in with your Ethereum account:\n{address}\n\nSign in with Ethereum to the app.\n\nURI: https://app.galxe.com\nVersion: 1\nChain ID: 1\nNonce: {nonce}\nIssued At: {ts}\nExpiration Time: {exp}"

    sig = sign_message(priv_key, siwe)

    r = requests.post("https://graphigo.prd.galaxy.eco/query", json={
        "query": 'mutation SignIn($input: Auth) { signin(input: $input) }',
        "variables": {"input": {"address": address, "addressType": "EVM", "publicKey": "1", "message": siwe, "signature": sig}}
    }, headers={"Content-Type": "application/json", "Origin": "https://app.galxe.com"})

    token = r.json().get("data", {}).get("signin")
    if token:
        # Save to credential store
        save_credential("galxe", {"token": token, "address": address, "created": ts})
    return token
```

### Twitter Auth (Semi-Autonomous — Cookies)
```python
def twitter_auth_check():
    """Check Twitter session validity — SEMI-AUTONOMOUS"""
    creds = load_credential("twitter")
    if not creds or not creds.get("auth_token"):
        return {"status": "need_setup", "action": "User must export cookies from browser"}

    cookies = {"auth_token": creds["auth_token"], "ct0": creds["ct0"]}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    resp = requests.get("https://x.com/home", cookies=cookies, headers=headers, allow_redirects=True)

    if resp.status_code == 200 and "login" not in resp.url:
        username = re.search(r'"screen_name":"([^"]+)"', resp.text)
        return {"status": "valid", "username": username.group(1) if username else "unknown"}
    return {"status": "expired", "action": "User must re-export cookies"}

def twitter_api_call(endpoint, method="GET", data=None):
    """Make authenticated Twitter API call"""
    creds = load_credential("twitter")
    cookies = {"auth_token": creds["auth_token"], "ct0": creds["ct0"]}
    headers = {
        "Authorization": f"Bearer {creds.get('bearer_token', 'AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA3')}",
        "x-csrf-token": creds["ct0"][:32],
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    if method == "GET":
        return requests.get(f"https://api.x.com{endpoint}", cookies=cookies, headers=headers)
    elif method == "POST":
        return requests.post(f"https://api.x.com{endpoint}", cookies=cookies, headers=headers, json=data)
```

### Gmail Auth (Semi-Autonomous — App Password)
```python
import imaplib, smtplib
from email.mime.text import MIMEText

def gmail_auth():
    """Gmail IMAP auth — SEMI-AUTONOMOUS (App Password)"""
    creds = load_credential("email")
    if not creds or not creds.get("app_password"):
        return {"status": "need_setup", "action": "User must generate App Password at myaccount.google.com/apppasswords"}

    try:
        mail = imaplib.IMAP4_SSL(creds.get("imap_host", "imap.gmail.com"))
        mail.login(creds["address"], creds["app_password"])
        return {"status": "valid", "connection": mail}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def gmail_send(to, subject, body):
    """Send email via SMTP"""
    creds = load_credential("email")
    smtp = smtplib.SMTP(creds.get("smtp_host", "smtp.gmail.com"), 587)
    smtp.starttls()
    smtp.login(creds["address"], creds["app_password"])

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = creds["address"]
    msg["To"] = to
    smtp.send_message(msg)
    smtp.quit()
```

### Discord Auth (Semi-Autonomous — Cookies)
```python
def discord_auth_check():
    """Check Discord session validity"""
    creds = load_credential("discord")
    if not creds or not creds.get("token"):
        return {"status": "need_setup", "action": "User must export cookies or provide bot token"}

    headers = {"Authorization": creds["token"], "User-Agent": "Mozilla/5.0"}
    resp = requests.get("https://discord.com/api/v10/users/@me", headers=headers)

    if resp.status_code == 200:
        user = resp.json()
        return {"status": "valid", "username": f"{user['username']}#{user.get('discriminator', '0')}"}
    return {"status": "expired", "action": "User must re-export token"}
```

### JAY Games Auth (Fully Autonomous)
```python
def jay_games_auth():
    """JAY Games session — FULLY AUTONOMOUS via wallet sign"""
    # JAY Games uses wallet-based auth (no QR needed for API)
    # Session derived from wallet address + API call
    wallet = get_evm_wallet()
    UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    # Create session via API
    r = requests.get(f"https://jay.games/api.php?api=session&wallet={wallet[1]}",
                     headers={"User-Agent": UA})
    session = r.json()

    save_credential("jay_games", {
        "session_token": session.get("session_token"),
        "wallet": wallet[1],
        "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    })
    return session
```

### Pixie Chess Auth (Semi-Autonomous — Privy)
```python
def pixie_chess_auth(email):
    """
    Pixie Chess auth via Privy — SEMI-AUTONOMOUS.
    Needs email OTP (retrieve via IMAP) + wallet sign.
    Token stored at config/credentials/pixiechess_auth.json.
    """
    from camoufox.sync_api import Camoufox

    with Camoufox(headless=True) as browser:
        page = browser.new_page()
        page.goto("https://pixiechess.xyz", wait_until="commit", timeout=60000)
        time.sleep(8)

        # Privy handles Turnstile internally
        result = privy_auth_email(email, page)

        # OTP sent — retrieve from Gmail via IMAP
        # Then enter OTP
        otp = get_latest_otp_from_email(email)  # via himalaya/imap
        if otp:
            privy_enter_otp(page, otp)
            time.sleep(5)

            # Extract session token
            session_data = page.evaluate("""() => {
                return {
                    localStorage: {...localStorage},
                    sessionStorage: {...sessionStorage}
                }
            }""")

            save_credential("pixiechess", session_data)
            return {"status": "authenticated", "data": session_data}

    return {"status": "otp_sent", "action": "Check email for OTP code"}
```

## Captcha Solving Integration

### Unified Captcha Solver
```python
def solve_captcha(captcha_type, **kwargs):
    """
    Unified captcha solver — auto-select best method

    captcha_type: 'wasm', 'turnstile', 'recaptcha_v2', 'hcaptcha', 'geetest_v4'
    """
    if captcha_type == "wasm":
        # Galxe WASM — Chromium headless (GRATIS)
        return solve_wasm_captcha(**kwargs)
    elif captcha_type == "turnstile":
        # Cloudflare Turnstile — Camoufox (GRATIS)
        return solve_turnstile_camoufox(**kwargs)
    elif captcha_type in ["recaptcha_v2", "recaptcha_v3", "hcaptcha", "geetest_v4"]:
        # Third-party service (bayar)
        creds = load_credential("captcha")
        if creds.get("capsolver_key"):
            return solve_with_capsolver(captcha_type, **kwargs)
        elif creds.get("twocaptcha_key"):
            return solve_with_2captcha(captcha_type, **kwargs)
        else:
            return {"error": "No captcha API key configured"}
    else:
        return {"error": f"Unknown captcha type: {captcha_type}"}
```

### WASM Captcha (Galxe — Chromium)
```python
def solve_wasm_captcha(api_name="PrepareParticipate"):
    """Solve Galxe WASM captcha via Chromium headless — GRATIS"""
    import subprocess, re, json

    result = subprocess.run(
        ['python3', 'scripts/galxe_captcha_solver.py'],
        capture_output=True, text=True, timeout=60
    )

    # Parse multiline JSON
    lines = result.stdout.split('\n')
    json_lines, in_json = [], False
    for line in lines:
        if line.strip().startswith('{'): in_json = True
        if in_json: json_lines.append(line)
        if in_json and line.strip().endswith('}'):
            try:
                raw = json.loads('\n'.join(json_lines))
                # Strip 'ok' field — not part of CaptchaInput
                return {k: raw[k] for k in ["lotNumber", "captchaOutput", "passToken", "genTime", "encryptedData"] if k in raw}
            except: continue
    return {"error": "Failed to parse captcha output"}
```

### Turnstile (Cloudflare — Camoufox)
```python
def solve_turnstile_camoufox(url, sitekey, timeout=30):
    """Solve Cloudflare Turnstile via Camoufox — GRATIS"""
    from camoufox.sync_api import Camoufox

    html = f'''<!DOCTYPE html>
    <html><head><script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async></script></head>
    <body><div class="cf-turnstile" data-sitekey="{sitekey}"></div></body></html>'''

    with Camoufox(headless=True) as browser:
        page = browser.new_page()
        page.route(url + "/", lambda route: route.fulfill(body=html, status=200))
        page.goto(url + "/")

        for _ in range(timeout):
            inp = page.query_selector("[name=cf-turnstile-response]")
            if inp and inp.get_attribute("value"):
                return {"token": inp.get_attribute("value")}
            time.sleep(1)
    return {"error": "Turnstile timeout"}
```

## Unified Auth Flow

### Main Auth Function
```python
def auth_platform(platform, force_refresh=False):
    """
    Unified auth entry point — auto-detect platform, auto-auth

    Returns: {"status": "valid"|"need_setup"|"error", "data": {...}}
    """
    # Load cached credentials
    creds = load_credential(platform)
    if creds and not force_refresh:
        # Validate existing token
        validation = validate_token(platform, creds)
        if validation["status"] == "valid":
            return {"status": "valid", "data": creds, "cached": True}

    # Auto-auth based on platform type
    if platform == "galxe":
        wallet = get_evm_wallet()
        token = galxe_auth(wallet[1], wallet[0])
        return {"status": "valid" if token else "error", "data": {"token": token}}

    elif platform == "twitter":
        check = twitter_auth_check()
        if check["status"] == "valid":
            return {"status": "valid", "data": load_credential("twitter")}
        return {"status": "need_setup", "action": "Export cookies from browser (Cookie-Editor extension)"}

    elif platform == "gmail":
        check = gmail_auth()
        if check["status"] == "valid":
            return {"status": "valid", "data": load_credential("email")}
        return {"status": "need_setup", "action": "Generate App Password at myaccount.google.com/apppasswords"}

    elif platform == "discord":
        check = discord_auth_check()
        if check["status"] == "valid":
            return {"status": "valid", "data": load_credential("discord")}
        return {"status": "need_setup", "action": "Export cookies or provide bot token"}

    elif platform == "wallet":
        priv, addr = get_evm_wallet()
        return {"status": "valid", "data": {"address": addr, "private_key": priv}}

    else:
        # Generic Web3 — try to detect auth method
        return detect_and_auth(platform)
```

### Token Validation
```python
def validate_token(platform, creds):
    """Validate token for platform"""
    import time, base64, json

    if platform == "galxe":
        token = creds.get("token", "")
        if not token:
            return {"status": "invalid", "reason": "no_token"}
        # Check JWT expiry
        try:
            payload = token.split(".")[1]
            payload += "=" * (4 - len(payload) % 4)
            decoded = json.loads(base64.b64decode(payload))
            if decoded.get("exp", 0) < time.time():
                return {"status": "expired", "reason": "jwt_expired"}
            return {"status": "valid"}
        except:
            return {"status": "invalid", "reason": "decode_failed"}

    elif platform == "twitter":
        return twitter_auth_check()

    elif platform == "gmail":
        return gmail_auth()

    elif platform == "discord":
        return discord_auth_check()

    return {"status": "unknown", "reason": "no_validator"}
```

## Credential CRUD

```python
import json, os
from pathlib import Path

CRED_DIR = Path.home() / "airdrop-agent" / "config" / "credentials"

def save_credential(platform, data):
    """Save credential to store"""
    CRED_DIR.mkdir(parents=True, exist_ok=True)
    filepath = CRED_DIR / f"{platform}_auth.json" if platform != "email" else CRED_DIR / "accounts.json"

    # Load existing, merge
    existing = {}
    if filepath.exists():
        with open(filepath) as f:
            existing = json.load(f)

    existing.update(data)
    existing["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    with open(filepath, "w") as f:
        json.dump(existing, f, indent=2)
    filepath.chmod(0o600)

def load_credential(platform):
    """Load credential from store"""
    # Check multiple locations
    locations = [
        CRED_DIR / f"{platform}_auth.json",
        CRED_DIR / f"{platform}_session.json",
        CRED_DIR / f"{platform}_token.json",
        CRED_DIR / "accounts.json",
    ]

    for filepath in locations:
        if filepath.exists():
            with open(filepath) as f:
                data = json.load(f)
            if platform in data:
                return data[platform]  # Nested format
            return data  # Flat format
    return None
```

## Pitfalls

### General
- **NEVER** store credentials in plain text in scripts — always use credential store
- **NEVER** commit credentials to git — add to .gitignore
- **ALWAYS** chmod 600 on credential files
- **ALWAYS** validate token before use — don't assume cached token is valid
- **ALWAYS** set User-Agent header — empty UA = blocked by most platforms

### Twitter
- `auth_token` is httpOnly — cannot access via `document.cookie`, must use DevTools Application tab
- VPS IP triggers phone verification — use cookies export, not browser login
- v1.1 API may return 401 even with valid session — test with `/home` page access
- `ct0` should be ~32 hex chars — longer = wrong cookie copied

### Galxe
- SIWE message MUST include `Expiration Time` field — without → "expirationTime must not be empty"
- Use `Authorization: <token>` header — NOT `Bearer <token>`
- `campaignID` (capital D) — NOT `campaignId`
- WASM captcha FAILS in Camoufox — use Chromium headless
- Captcha `ok` field must be stripped before API call

### Gmail
- App Password ≠ account password — must generate at myaccount.google.com/apppasswords
- App Password is 16 chars with spaces — strip spaces before use
- IMAP: `imap.gmail.com:993` — SMTP: `smtp.gmail.com:587`

### Captcha
- WASM captcha output is multiline JSON — parse with regex or line-by-line
- Turnstile token is domain-bound — solve on target domain, not localhost
- Camoufox startup takes 2-3 minutes — don't kill too early
- Third-party captcha: check balance before submitting

### Token Refresh
- Galxe JWT expires ~7 days — re-sign with SIWE when expired
- Twitter cookies last ~2 years (auth_token) — ct0 regenerates on login
- Gmail App Password doesn't expire — unless user revokes
- Discord token expires on password change — user must re-export

## Nodriver Integration (Anti-Detect Browser)

`nodriver` (⭐4.3K) is an async CDP-based browser framework with built-in anti-detection. **`navigator.webdriver: false`** out of the box.

### Setup
```python
# Install: pip install nodriver
# Chrome: ~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome
import nodriver as uc

CHROME = "/home/ubuntu/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome"

browser = await uc.start(
    headless=True,
    browser_executable_path=CHROME,
    browser_args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
)
```

### Key Features
- `navigator.webdriver: false` — passes bot detection
- Async CDP-based — no Selenium dependency
- Can load Galxe, access webpack modules, intercept network
- **Limitation**: async `evaluate` returns `None` for Promises

### Pitfalls
- **`--no-sandbox` required on VPS**: Without → "Failed to connect to browser"
- **async evaluate returns None**: `await tab.evaluate("async () => { ... }")` → `None`. Workaround: store result in `window.__result`, poll with sync evaluate.
- **WASM binary lazy-loads**: Module 95088 (`Ay`, `Qc` exports) found but WASM binary not fetched until claim/verify action. Don't try to call WASM directly from page load.
- **Galxe AppKit not bypassable**: Even with nodriver's anti-detect, Galxe's `@appkit` SDK (WalletConnect v2) won't connect to injected `window.ethereum`. Wallet auth still requires real browser.
- **Use for**: anti-detect browsing, Cloudflare bypass, network interception, Twitter actions. NOT for Galxe wallet connect.

### When to Use nodriver vs Camoufox vs Chromium
| Task | Best Tool | Why |
|------|-----------|-----|
| WASM captcha | Chromium | nodriver lazy-loads WASM, Camoufox breaks fingerprinting |
| Cloudflare bypass | nodriver | `webdriver: false`, undetected |
| Twitter actions | nodriver | anti-detect, persistent sessions |
| Galxe wallet auth | Real browser | AppKit requires WalletConnect, can't inject |
| Turnstile | Camoufox | purpose-built for Turnstile |
| General stealth | nodriver | best anti-detection of the three |

## Nodriver Adapter (Anti-Detect Browser)

**nodriver** (⭐4.3K) — Python anti-detect browser, CDP-based, no Selenium dependency.
Best for: anti-detect navigation, Cloudflare bypass, persistent sessions.

```python
import asyncio
import nodriver as uc

CHROME = "/home/ubuntu/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome"

async def nodriver_session(url, cookies=None):
    """Start anti-detect browser session"""
    browser = await uc.start(
        headless=True,
        browser_executable_path=CHROME,
        browser_args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    )
    
    # Set cookies if provided
    if cookies:
        tab = await browser.get("https://example.com")
        for name, value in cookies.items():
            await tab.send(uc.cdp.network.set_cookie(
                name=name, value=value, domain=".example.com", path="/"
            ))
    
    # Navigate to target
    page = await browser.get(url)
    await asyncio.sleep(10)
    
    return browser, page
```

**When to use nodriver vs others:**
- **nodriver** → anti-detect navigation, Cloudflare bypass, bot detection bypass
- **Playwright Chromium** → WASM captcha solving, JavaScript-heavy tasks
- **Camoufox** → Turnstile solving, general stealth, fingerprint protection

**Pitfall:** nodriver `evaluate()` with async Promises returns None. Use sync evaluation or store results in `window.__result` then read.

## Related Skills
- `auto-get-token` — Deep dive: network interception, localStorage extraction
- `automation-login` — Platform-specific login pitfalls
- `background-browser-workflow` — Browser → API workflow pattern
- `galxe-automation` — Galxe-specific API, campaigns, verification
- `auto-resolve-captcha` — Captcha solving (WASM, Turnstile, third-party)
- `airdrop-wallet-connect` — Wallet signing patterns
- `himalaya` — Gmail CLI (IMAP/SMTP)

## References
- `references/nodriver-integration.md` — nodriver setup, usage, pitfalls, webpack module access

## Recommended Tool: nodriver (Anti-Detect Browser)
**GitHub:** `ultrafunkamsterdam/nodriver` ⭐4.3K
**Why:** Async, CDP-based, no Selenium, undetected by Cloudflare/Captcha/Imperva. Best fit for our VPS airdrop automation stack.

```bash
pip install nodriver
```

```python
import nodriver as uc

async def background_browser(url, actions=None):
    """Run undetected browser in background"""
    browser = await uc.start(headless=True)
    page = await browser.get(url)
    
    # Perform actions
    if actions:
        for action in actions:
            if action["type"] == "click":
                elem = await page.find(action["selector"], best_match=True)
                await elem.click()
            elif action["type"] == "fill":
                elem = await page.find(action["selector"], best_match=True)
                await elem.send_keys(action["value"])
            await page.sleep(action.get("wait", 2))
    
    # Extract cookies/localStorage
    cookies = await page.send(uc.cdp.network.get_all_cookies())
    storage = await page.evaluate("({...localStorage})")
    
    await browser.stop()
    return {"cookies": cookies, "localStorage": storage}
```

**Use cases:**
- Twitter/Discord login (bypass phone verification from VPS IP)
- Cloudflare-protected sites
- Captcha-heavy platforms
- Persistent session extraction

## Scripts
- `~/airdrop-agent/scripts/galxe_captcha_solver.py` — WASM captcha solver (Chromium)
- `~/airdrop-agent/scripts/turnstile_solver.py` — Turnstile solver (Camoufox)
- `~/airdrop-agent/scripts/browser_auth.py` — Universal auth extractor
- `~/airdrop-agent/scripts/token_interceptor.py` — Network token interceptor
- `~/airdrop-agent/scripts/twitter_login_helper.py` — Twitter login helper
- `~/airdrop-agent/scripts/galxe_nodriver_connect.py` — Galxe nodriver connect attempt (partial)

## References
- `references/nodriver-guide.md` — nodriver setup, usage, pitfalls, when to use vs Camoufox/Chromium

---

## Advanced Features

### Generic SIWE Auth (Any Web3 Platform)
```python
def generic_siwe_auth(domain, address, priv_key, chain_id=1, extra_fields=None):
    """
    Generic SIWE (Sign-In with Ethereum) — works on ANY SIWE-compatible platform.
    Used by: Galxe, Pixie Chess, most Web3 dApps.
    """
    import time, random, string
    from eth_account import Account
    from eth_account.messages import encode_defunct

    nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=17))
    ts = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
    exp = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(time.time() + 7*24*3600))

    siwe = f"""{domain} wants you to sign in with your Ethereum account:
{address}

Sign in with Ethereum to the app.

URI: https://{domain}
Version: 1
Chain ID: {chain_id}
Nonce: {nonce}
Issued At: {ts}
Expiration Time: {exp}"""

    msg = encode_defunct(text=siwe)
    signed = Account.sign_message(msg, priv_key)
    return {
        "message": siwe,
        "signature": "0x" + signed.signature.hex(),
        "address": address,
        "nonce": nonce,
        "issued_at": ts,
        "expires_at": exp
    }
```

### Privy Auth (Web3 dApps — Email OTP)
```python
def privy_auth_email(email, page):
    """
    Privy SDK auth via email OTP — works on Pixie Chess, many Web3 games.
    Flow: Enter email → Privy sends OTP → Enter OTP → authenticated.
    
    Requires: Camoufox browser with page object.
    Turnstile is handled automatically by Privy SDK.
    """
    import time

    # Click login button
    page.locator("button:has-text('Login'), button:has-text('Sign In')").first.click(timeout=5000)
    time.sleep(3)

    # Find email input in Privy iframe
    for frame in page.frames:
        inp = frame.query_selector("input[type='email']")
        if inp and inp.is_visible():
            inp.fill(email)
            time.sleep(0.5)
            inp.press("Enter")  # Turnstile solved automatically by Privy
            break

    # OTP sent to email — retrieve via IMAP/himalaya
    # Then enter OTP in browser
    return {"status": "otp_sent", "email": email}

def privy_enter_otp(page, otp_code):
    """Enter OTP code for Privy auth"""
    import time

    # Find OTP inputs (6-digit boxes)
    otp_inputs = page.locator("input[maxlength='1'], input[aria-label*='Character']")
    if otp_inputs.count() >= 6:
        otp_inputs.first.click(force=True)
        time.sleep(0.3)
        for digit in otp_code:
            page.keyboard.press(digit)
            time.sleep(0.2)
    else:
        # Single OTP field
        otp_input = page.locator("input[type='text'], input[type='number']").first
        otp_input.fill(otp_code)
        otp_input.press("Enter")

    time.sleep(5)
    return {"status": "authenticated"}
```

### Cookie Import Helper
```python
def import_cookies_from_json(platform, cookies_json):
    """
    Import cookies from Cookie-Editor extension JSON format.
    Works for Twitter, Discord, and any platform.
    """
    import json

    if isinstance(cookies_json, str):
        cookies = json.loads(cookies_json)
    else:
        cookies = cookies_json

    # Extract auth-relevant cookies
    auth_data = {}
    for cookie in cookies:
        name = cookie["name"].lower()
        if name in ["auth_token", "ct0", "token", "session", "sessionid", "jwt"]:
            auth_data[cookie["name"]] = cookie["value"]

    # Platform-specific extraction
    if platform == "twitter":
        return {
            "auth_token": auth_data.get("auth_token", ""),
            "ct0": auth_data.get("ct0", ""),
            "status": "imported"
        }
    elif platform == "discord":
        return {
            "token": auth_data.get("token", ""),
            "status": "imported"
        }
    else:
        return {"cookies": auth_data, "status": "imported"}
```

### Auth Status Dashboard
```python
def auth_dashboard():
    """Check all platform auth status at once — run daily"""
    platforms = ["galxe", "twitter", "gmail", "discord", "wallet"]
    results = {}

    for platform in platforms:
        try:
            result = auth_platform(platform)
            results[platform] = {
                "status": result["status"],
                "cached": result.get("cached", False),
                "action": result.get("action", "none")
            }
        except Exception as e:
            results[platform] = {"status": "error", "error": str(e)}

    # Summary
    valid = sum(1 for r in results.values() if r["status"] == "valid")
    need_setup = sum(1 for r in results.values() if r["status"] == "need_setup")
    errors = sum(1 for r in results.values() if r["status"] == "error")

    return {
        "summary": f"{valid} valid, {need_setup} need setup, {errors} errors",
        "platforms": results
    }
```

### Auto-Refresh Token Manager
```python
def auto_refresh_all():
    """Auto-refresh all tokens before expiry — run in cron"""
    import time

    # Galxe: re-sign if JWT expires in < 1 day
    galxe = load_credential("galxe")
    if galxe and galxe.get("token"):
        try:
            import base64
            payload = galxe["token"].split(".")[1]
            payload += "=" * (4 - len(payload) % 4)
            decoded = json.loads(base64.b64decode(payload))
            if decoded.get("exp", 0) - time.time() < 86400:  # < 1 day
                wallet = get_evm_wallet()
                galxe_auth(wallet[1], wallet[0])
                print("✅ Galxe token refreshed")
        except:
            wallet = get_evm_wallet()
            galxe_auth(wallet[1], wallet[0])

    # Twitter: check session validity
    tw = twitter_auth_check()
    if tw["status"] == "expired":
        print(f"⚠️ Twitter expired — {tw.get('action', 're-export cookies')}")

    # Gmail: check App Password
    gm = gmail_auth()
    if gm["status"] != "valid":
        print(f"⚠️ Gmail issue — {gm.get('error', gm.get('action', 'unknown'))}")

    return {"status": "refresh_complete"}
```

### Credential Backup & Migration
```python
def backup_credentials(output_path=None):
    """Backup all credentials to encrypted file"""
    import json, time
    from pathlib import Path

    CRED_DIR = Path.home() / "airdrop-agent" / "config" / "credentials"
    if not output_path:
        output_path = CRED_DIR / f"backup_{time.strftime('%Y%m%d_%H%M%S')}.json"

    backup = {}
    for f in CRED_DIR.glob("*.json"):
        if "backup" in f.name:
            continue
        with open(f) as fh:
            backup[f.name] = json.load(fh)

    with open(output_path, "w") as f:
        json.dump(backup, f, indent=2)
    output_path.chmod(0o600)

    return {"path": str(output_path), "files": len(backup)}

def restore_credentials(backup_path):
    """Restore credentials from backup"""
    import json, shutil
    from pathlib import Path

    CRED_DIR = Path.home() / "airdrop-agent" / "config" / "credentials"

    with open(backup_path) as f:
        backup = json.load(f)

    for filename, data in backup.items():
        filepath = CRED_DIR / filename
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        filepath.chmod(0o600)

    return {"restored": len(backup)}
```

## Wallet Security & Compromise Detection

### Detection Signals
```python
def check_wallet_compromise(wallet_address, chains=None):
    """
    Check if wallet is compromised by analyzing:
    1. Non-zero nonce but no expected TXs (someone else sending)
    2. Balance draining pattern
    3. Unknown recipients
    """
    if not chains:
        chains = [
            {"name": "Base", "rpc": "https://mainnet.base.org"},
            {"name": "Gnosis", "rpc": "https://rpc.gnosischain.com"},
            {"name": "Polygon", "rpc": "https://polygon-bor-rpc.publicnode.com"},
            {"name": "Optimism", "rpc": "https://mainnet.optimism.io"},
            {"name": "Arbitrum", "rpc": "https://arb1.arbitrum.io/rpc"},
        ]
    
    from web3 import Web3
    
    alerts = []
    for chain in chains:
        try:
            w3 = Web3(Web3.HTTPProvider(chain["rpc"], request_kwargs={'timeout': 10}))
            if not w3.is_connected():
                continue
            
            balance = w3.eth.get_balance(wallet_address)
            nonce = w3.eth.get_transaction_count(wallet_address)
            
            if balance > 0 and nonce > 0:
                alerts.append({
                    "chain": chain["name"],
                    "balance": Web3.from_wei(balance, 'ether'),
                    "nonce": nonce,
                    "status": "active"
                })
        except:
            continue
    
    return alerts

def emergency_drain(wallet_pk, new_address, chains=None):
    """
    Emergency: drain all funds from compromised wallet to new address.
    Priority: move highest-value chain first.
    """
    if not chains:
        chains = [
            {"name": "Base", "rpc": "https://mainnet.base.org", "chain_id": 8453},
            {"name": "Polygon", "rpc": "https://polygon-bor-rpc.publicnode.com", "chain_id": 137},
            {"name": "Optimism", "rpc": "https://mainnet.optimism.io", "chain_id": 10},
        ]
    
    from web3 import Web3
    from eth_account import Account
    
    acct = Account.from_key(wallet_pk)
    old_addr = acct.address
    results = []
    
    for chain in chains:
        try:
            w3 = Web3(Web3.HTTPProvider(chain["rpc"], request_kwargs={'timeout': 10}))
            if not w3.is_connected():
                continue
            
            balance = w3.eth.get_balance(old_addr)
            if balance < Web3.to_wei(0.0001, 'ether'):
                results.append({"chain": chain["name"], "status": "skip", "reason": "too low"})
                continue
            
            gas_price = w3.eth.gas_price
            gas_cost = 21000 * gas_price
            send_amount = balance - gas_cost
            
            if send_amount <= 0:
                results.append({"chain": chain["name"], "status": "skip", "reason": "gas too high"})
                continue
            
            nonce = w3.eth.get_transaction_count(old_addr)
            tx = {
                'nonce': nonce,
                'to': new_address,
                'value': send_amount,
                'gas': 21000,
                'gasPrice': gas_price,
                'chainId': chain['chain_id'],
            }
            
            signed = w3.eth.account.sign_transaction(tx, wallet_pk)
            tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
            
            results.append({
                "chain": chain["name"],
                "status": "sent",
                "amount": Web3.from_wei(send_amount, 'ether'),
                "tx": tx_hash.hex()
            })
        except Exception as e:
            results.append({"chain": chain["name"], "status": "error", "error": str(e)[:50]})
    
    return results
```

### Compromise Response Checklist
When wallet compromise detected:
1. **IMMEDIATELY** generate new wallet: `Account.create()`
2. **IMMEDIATELY** try emergency drain (attacker may be faster)
3. **STOP** all bots/cron using compromised wallet
4. **UPDATE** all config files (`.env`, `wallets.json`, `galxe_token.json`)
5. **REVOKE** approvals via Revoke.cash (if any funds remain)
6. **REPORT** to any connected services (Galxe, Hanafuda, etc.)
7. **ANALYZE** attack vector: leaked `.env`, shared private key, phishing

### Pitfalls
- **Attacker auto-sweep**: If attacker has bot monitoring wallet, funds drain within seconds. Speed is critical.
- **Blockscout stale data**: API may show cached balances. Always verify via RPC directly.
- **Nonce = high number**: Active bot wallets have high nonce. Don't assume compromise just from high nonce.
- **Contract interactions**: `withdraw()` method on contract doesn't mean wallet sent funds. Check decoded input.
- **Don't interact with spam tokens**: Honeypot tokens in compromised wallet — don't approve/swap them.

### Multi-Account Support
```python
def load_credential(platform, account="default"):
    """Load credential with multi-account support"""
    CRED_DIR = Path.home() / "airdrop-agent" / "config" / "credentials"

    # Check account-specific file first
    locations = [
        CRED_DIR / f"{platform}_{account}.json",
        CRED_DIR / f"{platform}_auth.json",
        CRED_DIR / f"{platform}_session.json",
        CRED_DIR / f"{platform}_token.json",
        CRED_DIR / "accounts.json",
    ]

    for filepath in locations:
        if filepath.exists():
            with open(filepath) as f:
                data = json.load(f)
            if account != "default" and account in data:
                return data[account]
            if platform in data:
                return data[platform]
            return data
    return None

def list_accounts(platform):
    """List all saved accounts for a platform"""
    CRED_DIR = Path.home() / "airdrop-agent" / "config" / "credentials"
    accounts = []
    for f in CRED_DIR.glob(f"{platform}_*.json"):
        account_name = f.stem.replace(f"{platform}_", "")
        if account_name not in ["auth", "session", "token", "backup"]:
            accounts.append(account_name)
    return accounts
```

### Auto-Detect Platform from URL
```python
def detect_platform(url):
    """Auto-detect platform from URL and return auth method"""
    url_lower = url.lower()

    if "galxe.com" in url_lower:
        return {"platform": "galxe", "method": "siwe", "autonomous": True}
    elif "twitter.com" in url_lower or "x.com" in url_lower:
        return {"platform": "twitter", "method": "cookies", "autonomous": False}
    elif "discord.com" in url_lower:
        return {"platform": "discord", "method": "cookies", "autonomous": False}
    elif "gmail.com" in url_lower or "google.com" in url_lower:
        return {"platform": "gmail", "method": "app_password", "autonomous": False}
    elif "pixiechess" in url_lower:
        return {"platform": "pixiechess", "method": "privy", "autonomous": False}
    elif "jay.games" in url_lower or "jaymining" in url_lower:
        return {"platform": "jay", "method": "api_session", "autonomous": True}
    else:
        # Generic Web3 — try SIWE
        return {"platform": "generic_web3", "method": "siwe_or_detect", "autonomous": None}
```

### Error Recovery Guide
```python
def get_latest_otp_from_email(email_address, sender_filter=None, max_age_seconds=300):
    """
    Get latest OTP code from email — works with Gmail App Password.
    Used by Privy auth, email verification flows.
    """
    import imaplib, email, re, time
    from email.header import decode_header

    creds = load_credential("email")
    if not creds or not creds.get("app_password"):
        return None

    try:
        mail = imaplib.IMAP4_SSL(creds.get("imap_host", "imap.gmail.com"))
        mail.login(creds["address"], creds["app_password"])
        mail.select("INBOX")

        # Search recent emails
        _, data = mail.search(None, "ALL")
        mail_ids = data[0].split()

        # Check last 10 emails
        for mail_id in reversed(mail_ids[-10:]):
            _, msg_data = mail.fetch(mail_id, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            # Filter by sender if specified
            if sender_filter:
                sender = msg.get("From", "")
                if sender_filter not in sender:
                    continue

            # Check age
            date_str = msg.get("Date", "")
            # ... parse date and check max_age_seconds

            # Get body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = msg.get_payload(decode=True).decode()

            # Extract OTP (6-digit code)
            otp_match = re.search(r'\b(\d{6})\b', body)
            if otp_match:
                mail.logout()
                return otp_match.group(1)

        mail.logout()
    except Exception as e:
        print(f"Email OTP error: {e}")
    return None

def get_recovery_action(platform, error):
    """Return specific recovery action for auth errors"""
    recovery = {
        "twitter": {
            "expired": "Re-export cookies from browser (Cookie-Editor extension)",
            "phone_verify": "Add phone number to Twitter account, then re-export cookies",
            "rate_limit": "Wait 15 minutes, then retry",
            "invalid_token": "auth_token must be 40 hex chars — re-copy from DevTools"
        },
        "galxe": {
            "jwt_expired": "Auto-recovered: re-sign SIWE (run auth_platform('galxe'))",
            "invalid_address": "Check wallet address in wallets.json",
            "captcha_fail": "Regenerate WASM captcha via Chromium",
            "social_expired": "Reconnect Twitter/Discord via browser OAuth"
        },
        "gmail": {
            "auth_failed": "Regenerate App Password at myaccount.google.com/apppasswords",
            "imap_blocked": "Enable 'Less secure apps' or use App Password",
            "quota_exceeded": "Wait 24 hours or use different account"
        },
        "discord": {
            "expired": "Re-export cookies or provide fresh bot token",
            "invalid_token": "Token format: 'Bot MT...' or user token"
        }
    }

    platform_recovery = recovery.get(platform, {})
    return platform_recovery.get(error, f"Check {platform} credentials in config/credentials/")

# === END ADVANCED FEATURES ===
