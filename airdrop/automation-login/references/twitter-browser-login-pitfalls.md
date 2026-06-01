# Twitter Browser Login via Playwright/Camoufox

## Problem
Twitter login from VPS IPs triggers phone verification, making automated browser login unreliable.

## What Happens
1. Enter username → click Continue → works fine
2. Password field appears BUT masked by `data-testid="mask"` overlay
3. Any click on password field → timeout (mask intercepts)
4. Using `force=True` → login proceeds but redirects to "Enter your phone number"
5. Phone verification required — app password alone insufficient

## Attempted Fixes (All Failed)
- Remove mask via JS → page resets to initial state
- Hide layers div → page resets
- Click back button on phone prompt → password field disappears
- Camoufox → crashes with TypeError on Continue click

## Root Cause
- Twitter detects VPS/datacenter IPs as suspicious
- Phone number must be linked to account BEFORE attempting login
- App passwords don't bypass phone verification

## Working Solutions
1. **Cookies export** (recommended) — user exports from their browser
2. **Add phone number** to Twitter account first, then try browser login
3. **Twitter API v2** with OAuth 2.0 PKCE — requires developer account

## Code Template (Cookies-based)
```python
from playwright.sync_api import sync_playwright
import json

# Load cookies from user export
with open("twitter_cookies.json") as f:
    cookies = json.load(f)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=["--no-sandbox"])
    context = browser.new_context()
    context.add_cookies(cookies)
    page = context.new_page()
    page.goto("https://x.com/home")
    # Now logged in!
```
