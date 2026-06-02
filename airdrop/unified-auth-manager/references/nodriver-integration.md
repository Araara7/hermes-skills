# Nodriver Integration Details (Jun 2026)

## Installation
```bash
pip install nodriver
```

## Chrome Path (Playwright's Chromium)
```python
CHROME = "/home/ubuntu/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome"
```

## Basic Usage
```python
import asyncio
import nodriver as uc

async def main():
    browser = await uc.start(
        headless=True,
        browser_executable_path=CHROME,
        browser_args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    )
    
    tab = await browser.get("https://target.com")
    await asyncio.sleep(10)
    
    # Sync evaluate works
    title = await tab.evaluate("document.title")
    
    # Async evaluate returns None — DON'T use
    # result = await tab.evaluate("(async () => { ... })()")  # Returns None!
    
    # Instead: store result in window, then read
    await tab.evaluate("window.__result = 'pending'; someAsyncFn().then(r => window.__result = JSON.stringify(r))")
    await asyncio.sleep(5)
    result = await tab.evaluate("window.__result")
    
    browser.stop()

asyncio.run(main())
```

## Anti-Detection Results
| Test | nodriver | Playwright | Camoufox |
|------|----------|------------|----------|
| navigator.webdriver | false ✅ | true ❌ | false ✅ |
| Cloudflare bypass | ✅ | ❌ | ✅ |
| Galxe loads | ✅ | ✅ | ✅ |
| WASM captcha | ❌ (lazy) | ✅ | ❌ (fingerprint) |

## Webpack Module Access (Galxe)
```python
# Access webpack modules via webpackChunk_N_E
exports = await tab.evaluate("""
(() => {
    let __webpack_require__;
    window.webpackChunk_N_E.push([
        ['__test__'], {}, (req) => { __webpack_require__ = req; }
    ]);
    const mod = __webpack_require__('95088');  // WASM captcha module
    return JSON.stringify(Object.keys(mod));
})()
""")
# Returns: ["Ay", "Qc"] — Ay = init, Qc = generate
```

## CDP Cookie Management
```python
# Set cookies for authenticated sessions
await tab.send(uc.cdp.network.set_cookie(
    name="auth_token", value="...",
    domain=".x.com", path="/"
))
```

## Pitfalls
- **Async evaluate returns None** — use window.__result pattern
- **WASM binary lazy loading** — doesn't load on page load, only on action trigger
- **Module 95088** — `Ay()` returns WASM memory object, `Qc` needs WASM initialized first
- **Event loop errors on exit** — harmless cleanup noise, ignore
- **No sandbox required** — VPS/root needs `--no-sandbox` flag
