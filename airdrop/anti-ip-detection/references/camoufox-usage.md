# Camoufox Reference

## Overview
Camoufox is an anti-detect browser based on Firefox. It randomizes fingerprint per session and sets `navigator.webdriver = False`.

## Installation
```bash
pip install camoufox
apt-get install -y xvfb  # for non-headless with popup support
```

## Usage Modes

### Headless (no popup support)
```python
from camoufox.sync_api import Camoufox

with Camoufox(headless=True) as browser:
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://example.com")
```

### With xvfb (popup support)
```bash
xvfb-run -a -s "-screen 0 1920x1080x24" python3 script.py
```
```python
with Camoufox(headless=False) as browser:
    # Supports popups, but Google OAuth still unreliable
```

## Google Login
- Works for direct login (email + password)
- Cookies can be saved: `context.cookies()`
- OAuth popups in iframes are very hard to automate
- Better to use IMAP App Password for Gmail

## Anti-Detection Verification
```python
# Check webdriver flag
webdriver = page.evaluate("navigator.webdriver")
# Should be False

# Check user agent
ua = page.evaluate("navigator.userAgent")
# Should show Firefox
```

## Limitations
- Google's advanced detection may still catch it
- OAuth popup handling is unreliable
- Session cookies may not include all httpOnly cookies
- Requires xvfb for non-headless on headless servers
