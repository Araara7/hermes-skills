# Twitter Cookie Export Guide

## Cara Export Cookies Twitter

### Method 1: Cookie-Editor Extension (Recommended)

1. **Install Extension**
   - Chrome: [Cookie-Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicbahaaabklfkp)
   - Firefox: [Cookie-Editor](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/)

2. **Login ke Twitter**
   - Buka https://twitter.com/login
   - Login dengan akun kamu (Google OAuth atau username/password)

3. **Export Cookies**
   - Klik icon Cookie-Editor di toolbar
   - Klik tombol **Export**
   - Pilih **Export as JSON**
   - Copy hasil JSON

4. **Kirim ke Agent**
   - Paste JSON ke chat
   - Agent akan simpan dan gunakan untuk automasi

### Method 2: Developer Tools

1. **Buka Developer Tools**
   - Tekan F12 atau Ctrl+Shift+I
   - Tab **Application** (Chrome) atau **Storage** (Firefox)

2. **Navigate ke Cookies**
   - Klik **Cookies** di sidebar
   - Pilih `https://twitter.com`

3. **Export Cookies**
   - Klik kanan → **Select All**
   - Copy dan format sebagai JSON

### Method 3: JavaScript Console

```javascript
// Copy semua cookies sebagai JSON
copy(JSON.stringify(document.cookie.split(';').map(c => {
  const [name, ...value] = c.trim().split('=');
  return {name, value: value.join('='), domain: '.twitter.com'};
}), null, 2));
```

## Format Cookies yang Diharapkan

```json
[
  {
    "name": "auth_token",
    "value": "abc123...",
    "domain": ".twitter.com",
    "path": "/",
    "expires": 1234567890,
    "httpOnly": true,
    "secure": true,
    "sameSite": "None"
  },
  {
    "name": "ct0",
    "value": "xyz789...",
    "domain": ".twitter.com",
    "path": "/",
    "expires": 1234567890,
    "httpOnly": false,
    "secure": true,
    "sameSite": "Lax"
  }
]
```

## Cookies Penting untuk Twitter

| Cookie | Fungsi |
|--------|--------|
| `auth_token` | Authentication token utama |
| `ct0` | CSRF token |
| `guest_id` | Guest identifier |
| `personalization_id` | User preferences |

## Verifikasi Cookies

Setelah export, agent bisa test cookies:

```python
from camoufox.sync_api import Camoufox
import json

cookies = json.load(open("twitter_cookies.json"))

with Camoufox(headless=True) as browser:
    context = browser.new_context()
    context.add_cookies(cookies)
    
    page = context.new_page()
    page.goto("https://twitter.com/home")
    page.wait_for_load_state("networkidle")
    
    if "home" in page.url:
        print("✅ Cookies valid!")
    else:
        print("❌ Cookies expired")
```

## Troubleshooting

### Cookies Expired
- Export ulang dari browser
- Cookies biasanya expire setelah 2 minggu

### Login Required
- Pastikan kamu login di browser sebelum export
- Cek apakah 2FA aktif (mungkin perlu verifikasi ulang)

### Domain Mismatch
- Pastikan domain cookies adalah `.twitter.com` atau `twitter.com`
- Bukan domain lain

## Referensi

- [Twitter Cookie Policy](https://twitter.com/en/privacy)
- [Cookie-Editor Extension](https://cookie-editor.cgagnier.ca/)
