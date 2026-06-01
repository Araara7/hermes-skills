# Twitter Cookie Validation & Usage

## Required Cookies

| Cookie | Length | Format |
|--------|--------|--------|
| `auth_token` | 40 chars | hex string |
| `ct0` | 32 chars | hex string |

## Validation Script

```python
import requests

TWITTER_BEARER = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA3"

def validate_twitter_cookies(auth_token, ct0):
    cookies = {"auth_token": auth_token, "ct0": ct0}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
        "Authorization": TWITTER_BEARER,
        "x-csrf-token": ct0,
    }
    
    resp = requests.get(
        "https://api.x.com/1.1/account/verify_credentials.json",
        cookies=cookies, headers=headers
    )
    
    if resp.status_code == 200:
        data = resp.json()
        return {"valid": True, "username": data.get("screen_name")}
    return {"valid": False, "error": resp.text[:100]}

# Usage
result = validate_twitter_cookies("your_auth_token", "your_ct0")
print(result)
```

## Common Issues

1. **ct0 too long** — Should be exactly 32 hex chars, not 160
2. **auth_token invalid** — Expired or wrong value copied
3. **401 error** — Login expired, need fresh cookies

## How User Should Export

1. Login to twitter.com/home
2. F12 → Application → Cookies → twitter.com
3. Filter for `auth_token` → double-click value → copy (40 chars)
4. Filter for `ct0` → double-click value → copy (32 chars)
