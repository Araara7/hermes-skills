# Browser Auth Extractor

Universal token/cookie/auth harvester. Like pressing F12 on any website.

## Usage

```bash
cd ~/airdrop-agent

# Interactive mode — opens browser, waits for you to login, extracts everything
python3 scripts/browser_auth.py https://pixiechess.xyz

# Custom output path
python3 scripts/browser_auth.py https://example.com --output config/credentials/example.json

# Load existing cookies first
python3 scripts/browser_auth.py https://example.com --cookies cookies.json

# Increase wait time (default 120s)
python3 scripts/browser_auth.py https://example.com --timeout 300
```

## What It Extracts

- **Cookies** — all cookies with name, value, domain, httpOnly, secure, sameSite
- **localStorage** — all key-value pairs (truncated to 500 chars each)
- **sessionStorage** — all key-value pairs
- **JWT tokens** — regex scan for `eyJ...` patterns
- **Auth headers** — intercepts `authorization`, `x-api-key`, etc. from network requests
- **URL tokens** — extracts `token=`, `access_token=` from URLs
- **Auth method detection** — identifies Privy, Firebase, Auth0, Supabase, Clerk, NextAuth, etc.

## Output Format

```json
{
  "url": "https://pixiechess.xyz",
  "domain": "pixiechess_xyz",
  "extracted_at": "2026-05-31T15:30:00",
  "cookies": [...],
  "local_storage": [...],
  "session_storage": [...],
  "tokens_found": [{"type": "JWT", "value": "eyJ...", "source": "storage"}],
  "headers": {"authorization": "Bearer eyJ..."},
  "auth_method": ["Privy", "JWT"]
}
```

## Limitations

- Cannot bypass CAPTCHA (Turnstile, reCAPTCHA) — user must complete manually
- Cannot inject wallet providers — detects real browser extensions only
- Headless browser may be detected by anti-bot systems
- Some sites block datacenter IPs entirely

## Dependencies

- playwright (pip install playwright && playwright install chromium)
- eth_account (pip install eth-account)
