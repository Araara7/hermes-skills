# Twitter Cookie Extraction Guide

## Cara Mendapatkan Twitter Cookies

### Method 1: Application Tab (Recommended)

1. Buka https://twitter.com/home (pastikan sudah login)
2. Tekan **F12** → Tab **Application**
3. Klik **Cookies** → `https://twitter.com`
4. Filter dengan ketik: `auth`
5. Copy `auth_token` (40 karakter hex)
6. Filter: `ct0`
7. Copy `ct0` (biasanya 32 karakter, bisa lebih)

### Method 2: Console (Hanya Non-httpOnly)

```javascript
// Hanya bisa akses cookies yang bukan httpOnly
document.cookie.split(';').filter(c => c.includes('ct0')).join('\n')
```

**Catatan:** `auth_token` bersifat httpOnly, TIDAK bisa diakses via JavaScript!

## Twitter API Testing

### Public Bearer Token
```
AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA3
```

### Test dengan curl
```bash
curl -s -b "auth_token=XXX; ct0=XXX" \
  -H "Authorization: Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA3" \
  -H "x-csrf-token: CT0_VALUE" \
  "https://api.x.com/1.1/account/verify_credentials.json"
```

### Test Session Validity (Web)
```python
import requests

cookies = {"auth_token": "...", "ct0": "..."}
resp = requests.get("https://x.com/home", cookies=cookies, allow_redirects=True)

if resp.status_code == 200 and "login" not in resp.url:
    print("Session valid!")
```

## Pitfalls

- `auth_token` httpOnly → harus pakai Application tab
- `ct0` bisa >32 karakter di某些浏览器
- v1.1 API sering return 401 walau session valid
- Web scraping (x.com/home) lebih reliable untuk verifikasi
- Guest cookies (`guest_id`, `gt`) bukan auth cookies

## Durasi Token

| Token | Durasi |
|-------|--------|
| auth_token | ~2 tahun |
| ct0 | Session-based |
| guest_id | ~2 tahun |

Session bisa dibatalkan jika:
- User logout dari device lain
- Password diubah
- Twitter detect suspicious activity
