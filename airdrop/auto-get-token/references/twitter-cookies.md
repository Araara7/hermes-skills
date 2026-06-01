# Twitter Session Management

## Cookie-Based Authentication

Twitter uses cookie-based auth for web sessions. Key cookies:

| Cookie | Type | Access | Format |
|--------|------|--------|--------|
| `auth_token` | httpOnly | Application tab only | 40 hex chars |
| `ct0` | accessible | document.cookie | 32+ hex chars |
| `twid` | accessible | document.cookie | `u%3D{user_id}` |

## Extraction Process

1. User logs in to Twitter manually
2. F12 → Application → Cookies → `https://twitter.com`
3. Copy `auth_token` (httpOnly, must use Application tab)
4. Copy `ct0` via Console: `document.cookie.match(/ct0=([^;]+)/)?.[1]`

## Verification

```python
import requests

cookies = {"auth_token": "...", "ct0": "..."}
headers = {
    "Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA3",
    "x-csrf-token": ct0[:32],
}

# Most reliable: check home page
resp = requests.get("https://x.com/home", cookies=cookies, headers=headers, allow_redirects=True)
# 200 = valid session
```

## Common Issues

- **401 on API but 200 on home page**: Session is valid, API Bearer token may be wrong
- **auth_token not in document.cookie**: It's httpOnly, use Application tab
- **ct0 too long**: ct0 can be 32-160+ chars, use full value for x-csrf-token header
- **Redirect to /login**: Cookies expired or invalid

## Token Storage

Store in `~/airdrop-agent/config/credentials/twitter_session.json`:
```json
{
  "twitter": {
    "auth_token": "...",
    "ct0": "...",
    "user_id": "...",
    "username": "...",
    "status": "active"
  }
}
```
