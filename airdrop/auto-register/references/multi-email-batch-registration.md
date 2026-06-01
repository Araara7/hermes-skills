# Multi-Email Batch Registration

Pattern untuk daftar beberapa email sekaligus di satu platform airdrop.

## Use Case
User punya banyak email pribadi dan ingin mendaftarkan semuanya ke satu project airdrop (contoh: Umbra, Avazaky, dll).

## Workflow

### 1. Kumpulkan Email List
```python
EMAILS = [
    "email1@gmail.com",
    "email2@gmail.com",
    "email3@outlook.com",
    # tambah sesuai kebutuhan
]
```

### 2. Cek API Dulu (MANDATORY)
```bash
# Cek apakah ada API register
curl -s "https://target.com/" | grep -oE 'api[^"]*register[^"]*' | sort | uniq

# Cek apakah ada rate limit
curl -s -I "https://target.com/register" | grep -i "rate\|limit\|retry"
```

### 3. Jika Ada API → Background Registration
```python
import requests
import time
import random

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def register_email(email, api_url):
    headers = {"User-Agent": UA}
    data = {"email": email}
    resp = requests.post(api_url, json=data, headers=headers)
    return resp.json()

results = {}
for email in EMAILS:
    result = register_email(email, "https://target.com/api/register")
    results[email] = result
    # Random delay untuk hindari rate limit
    delay = random.uniform(5, 15)
    time.sleep(delay)
```

### 4. Jika Tidak Ada API → Camoufox Browser
```python
from camoufox.sync_api import Camoufox
import random

def register_via_browser(email, url):
    with Camoufox(headless=True) as browser:
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(3)
        
        # Isi form
        page.fill("input[type=email]", email)
        time.sleep(1)
        
        # Submit
        page.click("button[type=submit]")
        time.sleep(3)
        
        # Cek hasil
        content = page.content()
        success = "success" in content.lower() or "registered" in content.lower()
        return success

for email in EMAILS:
    success = register_via_browser(email, "https://target.com/register")
    print(f"{email}: {'✅' if success else '❌'}")
    time.sleep(random.uniform(10, 30))
```

### 5. Verifikasi Email
Setelah register, cek inbox untuk verification link:
```bash
# Pakai himalaya CLI
himalaya envelope list --account gmail -w 100 | grep -i "umbra\|verify\|confirm"
```

## Anti-Detection Rules

| Rule | Action |
|------|--------|
| Delay antara register | Random 5-30 detik |
| User-Agent rotation | Beda UA setiap email |
| Jangan register > 5 email/jam | Rate limit risk |
| Pakai proxy jika bisa | IP rotation |
| Simpan hasil register | Track yang sudah/sudah |

## Output Format
```json
{
  "platform": "umbra",
  "url": "https://umbra.xxx",
  "registrations": [
    {"email": "email1@gmail.com", "status": "success", "timestamp": "..."},
    {"email": "email2@gmail.com", "status": "pending_verification", "timestamp": "..."},
    {"email": "email3@gmail.com", "status": "failed", "error": "rate limited", "timestamp": "..."}
  ],
  "total": 3,
  "success": 1,
  "pending": 1,
  "failed": 1
}
```

## Pitfalls

1. **Rate limiting** — Jangan register > 5 email per jam dari satu IP
2. **Email verification** — Semua email harus bisa diakses untuk verifikasi
3. **Duplicate detection** — Beberapa platform cek IP/device fingerprint
4. **CAPTCHA** — Banyak platform pakai CAPTCHA di form register
5. **Phone verification** — Beberapa platform butuh nomor HP (tidak bisa diotomasi)
