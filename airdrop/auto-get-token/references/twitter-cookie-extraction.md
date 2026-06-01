# Twitter Cookie Extraction Guide

## Problem: auth_token is httpOnly

`auth_token` cannot be accessed via `document.cookie` because it's httpOnly.

## Solution: Use DevTools Application Tab

### Step-by-Step:

1. Login to Twitter at https://twitter.com/home
2. Press **F12** to open DevTools
3. Go to **Application** tab
4. Click **Cookies** → `https://twitter.com`
5. Filter by typing `auth`
6. Click on `auth_token` value → **Ctrl+C** to copy

### What You Need:

| Cookie | Length | Format | Access Method |
|--------|--------|--------|---------------|
| `auth_token` | 40 chars | hex | DevTools only (httpOnly) |
| `ct0` | 32 chars | hex | `document.cookie` OR DevTools |

### Quick ct0 Extraction (Console):

```javascript
document.cookie.match(/ct0=([^;]+)/)?.[1]
```

## Verification Methods

### Method 1: Home Page Access (Most Reliable)

```python
import requests

cookies = {"auth_token": "...", "ct0": "..."}
headers = {"User-Agent": "Mozilla/5.0 ..."}

resp = requests.get("https://x.com/home", cookies=cookies, headers=headers, allow_redirects=True)

if resp.status_code == 200 and "login" not in resp.url:
    print("✅ Session valid!")
    # Extract username from HTML
    import re
    username = re.search(r'"screen_name":"([^"]+)"', resp.text)
    print(f"Username: @{username.group(1)}")
```

### Method 2: API Verification

```python
cookies = {"auth_token": "...", "ct0": "..."}
headers = {
    "Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA3",
    "x-csrf-token": ct0[:32],
}

resp = requests.get("https://api.x.com/1.1/account/verify_credentials.json", cookies=cookies, headers=headers)
# Note: May return 401 even with valid session
```

## Common Issues

### 1. Token Expired
- **Symptom**: 401 error on all API calls
- **Solution**: Login again and get fresh cookies

### 2. Wrong Token Copied
- **Symptom**: Token length not 40 chars
- **Solution**: Make sure you're copying `auth_token`, not other cookies

### 3. Session Valid but API Returns 401
- **Symptom**: Home page works (200) but API returns 401
- **Solution**: Use home page verification instead of API

### 4. ct0 Too Long
- **Symptom**: ct0 is 160+ chars instead of 32
- **Solution**: You might be copying the wrong cookie. ct0 should be exactly 32 hex characters.

## Cookie Export with Extension

### Cookie-Editor Extension

1. Install: https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicbahaaabklfkp
2. Click icon → **Export** → **JSON**
3. Copy the JSON array

### Expected Format:

```json
[
  {
    "domain": ".twitter.com",
    "name": "auth_token",
    "value": "74d10c74c6bce67fcae2efa0dce027077380e7f7",
    "path": "/",
    "secure": true,
    "httpOnly": true
  },
  {
    "domain": ".twitter.com",
    "name": "ct0",
    "value": "3636e181846afd4ff04b52c308bd8865",
    "path": "/",
    "secure": true,
    "httpOnly": false
  }
]
```

## Session Duration

| Token | Duration | Notes |
|-------|----------|-------|
| `auth_token` | ~2 years | Until logout/revoke |
| `ct0` | Session-based | Regenerates on login |

## Security Notes

- Never share auth_token publicly
- Store in encrypted file (chmod 600)
- Don't commit to git
- Rotate if compromised
