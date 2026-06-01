# nodriver — Anti-Detect Browser Framework

## Overview
`nodriver` (⭐4.3K, Python) — async CDP-based browser with built-in anti-detection. Successor to undetected-chromedriver.

## Install
```bash
pip install nodriver
```

## Chrome Path
```python
# Playwright's Chromium works:
CHROME = "/home/ubuntu/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome"
# Or system Chrome:
# CHROME = "/usr/bin/google-chrome"
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
    
    tab = await browser.get("https://example.com")
    await asyncio.sleep(5)
    
    title = await tab.evaluate("document.title")
    webdriver = await tab.evaluate("navigator.webdriver")  # False!
    
    browser.stop()

asyncio.run(main())
```

## Anti-Detection Results
| Check | nodriver | Playwright Chromium | Camoufox |
|-------|----------|---------------------|----------|
| navigator.webdriver | ✅ false | ❌ true | ✅ false |
| Cloudflare | ✅ bypass | ❌ blocked | ✅ bypass |
| Galxe load | ✅ works | ✅ works | ✅ works |
| WASM captcha | ❌ lazy load | ✅ works | ❌ fingerprinting |

## CDP Cookie Management
```python
# Set cookies (for Twitter session etc.)
await tab.send(uc.cdp.network.set_cookie(
    name="auth_token", value="...",
    domain=".x.com", path="/"
))
```

## Galxe Webpack Module Access
```python
# After page loads (wait 15s for hydration)
# Module 95088 has captcha exports: Ay (init), Qc (generate)
exports = await tab.evaluate("""
(() => {
    let __webpack_require__;
    window.webpackChunk_N_E.push([
        ['__test__'], {}, (req) => { __webpack_require__ = req; }
    ]);
    const mod = __webpack_require__('95088');
    return JSON.stringify(Object.keys(mod));
})()
""")
# Result: ["Ay", "Qc"]
```

## Critical Pitfalls

### 1. `--no-sandbox` required on VPS
Without: `Exception: Failed to connect to browser`

### 2. async evaluate returns None for Promises
```python
# ❌ Returns None
result = await tab.evaluate("(async () => { return await someAsync(); })()")

# ✅ Workaround: store and poll
await tab.evaluate("""
window.__result = 'pending';
someAsync().then(r => { window.__result = JSON.stringify(r); });
""")
for _ in range(10):
    await asyncio.sleep(1)
    result = await tab.evaluate("window.__result")
    if result != 'pending':
        break
```

### 3. WASM binary lazy-loads
Module 95088 found but WASM binary (`wasm_lib_bg.*.wasm`) not fetched until claim/verify action triggers it. Don't try to call WASM directly after page load.

### 4. Galxe AppKit not bypassable
Galxe uses `@appkit` SDK (WalletConnect v2), not direct `window.ethereum`. Even with perfect inject, AppKit won't detect it. localStorage key `@appkit/connection_status` tracks state.

### 5. Event loop cleanup noise
`RuntimeError: Event loop is closed` at script end is harmless — just cleanup noise from `browser.stop()`.

## When to Use
| Task | Use nodriver? | Better alternative |
|------|--------------|-------------------|
| Cloudflare bypass | ✅ Yes | — |
| Twitter actions | ✅ Yes | — |
| WASM captcha | ❌ No | Chromium (Playwright) |
| Turnstile | ❌ No | Camoufox |
| Galxe wallet auth | ❌ No | Real browser (user) |
| General stealth | ✅ Yes | — |
| Token extraction | ✅ Yes | Camoufox |
