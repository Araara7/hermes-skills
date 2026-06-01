# Twitter Cookie Extraction Guide

## Required Cookies

| Cookie | Length | Format | Purpose |
|--------|--------|--------|---------|
| `auth_token` | 40 chars | hex string | Main auth token (2 year expiry) |
| `ct0` | 32 chars | hex string | CSRF token (session-based) |

## How to Extract (Step-by-Step)

### Method 1: Developer Tools

1. Login to https://twitter.com/home
2. Press **F12** → Tab **Application**
3. Left panel: **Cookies** → `https://twitter.com`
4. Filter by typing `auth_token` in filter box
5. **Double-click** the Value → Select All → Copy
6. Repeat for `ct0`

### Method 2: Console Command

```javascript
// Run in F12 → Console while on twitter.com
document.cookie.split(';')
  .filter(c => c.includes('auth_token') || c.includes('ct0'))
  .map(c => c.trim())
  .join('\n')
```

### Method 3: Cookie-Editor Extension

1. Install [Cookie-Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicbahaaabklfkp)
2. Click icon → **Export** → **JSON**
3. Find `auth_token` and `ct0` in the JSON

## Validation Script

```python
import requests

def validate_twitter_cookies(auth_token, ct0):
    """Validate Twitter cookies by calling verify_credentials API"""
    
    cookies = {"auth_token": auth_token, "ct0": ct0}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
        "Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA3",
        "x-csrf-token": ct0,
    }
    
    resp = requests.get(
        "https://api.x.com/1.1/account/verify_credentials.json",
        cookies=cookies,
        headers=headers
    )
    
    if resp.status_code == 200:
        data = resp.json()
        return {
            "valid": True,
            "username": data.get("screen_name"),
            "name": data.get("name"),
            "followers": data.get("followers_count"),
        }
    else:
        return {"valid": False, "error": resp.json().get("errors", [{}])[0].get("message")}
```

## Common Issues

### ct0 Too Long
- **Problem**: ct0 is 160+ characters
- **Cause**: Copying from wrong field or encoded value
- **Fix**: ct0 should be EXACTLY 32 hex characters

### auth_token Invalid (401)
- **Problem**: API returns "Invalid or expired token"
- **Causes**:
  1. Token expired (user logged out)
  2. Wrong value copied (not the actual cookie)
  3. Session ended before copy
- **Fix**: Login fresh, copy immediately

### No auth_token Cookie
- **Problem**: auth_token not in cookie list
- **Cause**: Not actually logged in
- **Fix**: Verify you can see timeline at twitter.com/home

## Token Format Reference

```
auth_token: 74d10c74c6bce67fcae2efa0dce027077380e7f7
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            40 hex characters

ct0: 3636e181846afd4ff04b52c308bd8865
     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
     32 hex characters
```

## Twitter Public Bearer Token

Can be captured from network traffic (used for public API calls):

```
Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA3
```

This is NOT a user token - it's Twitter's public API bearer token.
