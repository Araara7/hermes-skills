# Nodriver Quick Reference

## Install
```bash
pip install nodriver
```

## Chrome Path
```
~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome
```

## Async Usage
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
    tab = await browser.get(url)
    await asyncio.sleep(5)
    title = await tab.evaluate("document.title")
    browser.stop()

asyncio.run(main())
```

## Key Features
- `navigator.webdriver = false` — undetected
- CDP-based (Chrome DevTools Protocol)
- Async-first (all calls are `await`)
- No Selenium dependency
- Bypass Cloudflare, Imperva, DataDome

## Limitations
- WASM binary doesn't auto-load (lazy loading)
- Requires `--no-sandbox` on VPS
- Chrome path must be specified explicitly
- Event loop errors on exit (harmless)

## Best Use Cases
1. Token extraction from anti-bot sites
2. Cloudflare-protected pages
3. Twitter/social media automation
4. General anti-detect browsing
