# Nodriver — Anti-detect Chromium Browser

## Overview
Nodriver (⭐4.3K) is the successor to undetected-chromedriver. CDP-based, async-first, no Selenium dependency.

## Install
```bash
pip install nodriver  # v0.50+
```

## Chrome Path (Playwright's Chromium)
```
~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome
```

## Basic Usage
```python
import asyncio
import nodriver as uc

CHROME = "/home/ubuntu/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome"

async def main():
    browser = await uc.start(
        headless=True,
        browser_executable_path=CHROME,
        browser_args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    )
    
    tab = await browser.get("https://target.com")
    await asyncio.sleep(5)
    
    # Check stealth
    webdriver = await tab.evaluate("navigator.webdriver")  # False
    ua = await tab.evaluate("navigator.userAgent")
    
    # Interact
    title = await tab.evaluate("document.title")
    
    # Click element
    element = await tab.find("button", best_match=True)
    await element.click()
    
    # Type text
    input_field = await tab.select("input[type=text]")
    await input_field.send_keys("hello")
    
    browser.stop()

asyncio.run(main())
```

## Network Interception
```python
async def intercept(request):
    if 'auth' in request.url.lower():
        print(f"Auth request: {request.url}")

tab = await browser.get(url)
tab.add_handler(uc.cdp.network.RequestWillBeSent, intercept)
```

## Cookie Management
```python
# Add cookies
await tab.send(uc.cdp.network.set_cookie(
    name="auth_token",
    value="xxx",
    domain=".target.com"
))

# Get cookies
cookies = await tab.send(uc.cdp.network.get_all_cookies())
```

## Pitfalls
- **VPS requires `--no-sandbox`** — without it, "Failed to connect to browser"
- **WASM binary doesn't auto-load** — Galxe WASM captcha lazy loads only on claim/verify action
- **Async only** — all calls are `await`, can't use sync API
- **Chrome path required** — no auto-detect, must specify Playwright's Chromium path
- **Event loop errors on exit** — harmless cleanup noise, ignore

## When to Use Nodriver vs Camoufox vs Chromium
| Task | Use | Why |
|------|-----|-----|
| Token extraction | Nodriver | Fast, undetected |
| Cloudflare bypass | Nodriver | Best CF bypass |
| Turnstile captcha | Camoufox | Built-in bypass |
| WASM captcha | Chromium | Only one that works |
| General stealth | Camoufox | Anti-fingerprint |
| Twitter login | Nodriver | Undetected, fast |
