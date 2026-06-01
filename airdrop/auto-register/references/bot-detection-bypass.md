# Bot Detection Bypass Techniques

## Masalah
Banyak website memblokir request dari bot/headless browser. Contoh: JAY Games memblokir `fetch()` dari Playwright tetapi menerima curl.

## Solusi

### 1. Gunakan curl dengan User-Agent
```bash
curl -s -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" "https://example.com/api"
```

### 2. Headers yang Diperlukan
```bash
-H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
-H "Accept: application/json"
-H "Referer: https://example.com/"
```

### 3. Playwright dengan User-Agent
```python
context = await browser.new_context(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
```

### 4. Camoufox (Anti-Detection Browser)
```python
from camoufox.async_api import AsyncCamoufox

async with AsyncCamoufox(headless=True) as browser:
    page = await browser.new_page()
    # Sudah include anti-detection
```

## Pola Deteksi Bot

### Cek 1: User-Agent
- Bot tanpa User-Agent → Diblokir
- Bot dengan User-Agent biasa → Kadang diblokir
- Bot dengan User-Agent Chrome → Biasanya lolos

### Cek 2: Headers
- `Accept` header harus lengkap
- `Referer` harus sesuai domain
- `X-Requested-With` untuk AJAX

### Cek 3: Cookies/Session
- Beberapa API butuh session dari halaman utama
- Cookies harus dikirim dengan request

### Cek 4: JavaScript Execution
- `navigator.webdriver` harus `false`
- `window.chrome` harus ada
- Plugin dan bahasa harus lengkap

## Contoh: JAY Games API

### ❌ Gagal (diblokir)
```javascript
// Dari browser tanpa proper context
fetch('api.php?api=qr_create')
```

### ✅ Berhasil (lolos)
```bash
# Dengan curl dan User-Agent
curl -s -H "User-Agent: Mozilla/5.0 ..." "https://games.thejaynetwork.com/api.php?api=qr_create"
```

### ✅ Berhasil (dari Playwright)
```python
# Dari dalam halaman yang sudah load
await page.evaluate('''
    async () => {
        const response = await fetch("api.php?api=qr_create");
        return await response.json();
    }
''')
```

## Rekomendasi

1. **Selalu gunakan User-Agent** browser standar
2. **Cek dulu dengan curl** sebelum gunakan browser
3. **Gunakan Camoufox** untuk operasi sensitif
4. **Simpan cookies** dari session pertama
5. **Delay random** antara request
