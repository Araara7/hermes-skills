---
name: auto-register
description: "Auto-register di website airdrop: isi form, handle CAPTCHA, submit, simpan data registrasi, ekstrak API"
version: 1.1.0
author: hermes-agent
license: MIT
tags: [airdrop, registration, automation, form-filling, browser, api-extraction]
metadata:
  hermes:
    tags: [airdrop, registration, automation, form-filling, browser, api-extraction]
---

# Auto-Register Website Airdrop

Skill ini mengotomatisasi proses registrasi di website airdrop. Mendukung:
- Isi form otomatis (text, email, wallet, social media, dropdown)
- Handle CAPTCHA (integrasi dengan skill auto-resolve-captcha)
- Multi-step registration
- Simpan data registrasi ke file
- Anti-detection menggunakan Camoufox
- **Ekstrak API endpoints dari website target**

## Prerequisites

1. Camoufox terinstall (`pip install camoufox`)
2. Skill `auto-resolve-captcha` untuk handle CAPTCHA
3. Data akun di `~/airdrop-agent/config/credentials/accounts.json`

## Cara Pakai

### Command Line

```bash
# Register di website dengan URL
python3 ~/.hermes/skills/airdrop/auto-register/register.py --url "https://example.com/register"

# Register dengan custom data
python3 ~/.hermes/skills/airdrop/auto-register/register.py --url "https://example.com/register" --data '{"email": "custom@email.com", "wallet": "0x123..."}'

# Register dengan config file
python3 ~/.hermes/skills/airdrop/auto-register/register.py --url "https://example.com/register" --config ~/airdrop-agent/config/register_config.json

# Register dengan screenshot
python3 ~/.hermes/skills/airdrop/auto-register/register.py --url "https://example.com/register" --screenshot ~/airdrop-agent/data/screenshots/
```

### Dalam Agent

```python
# Load skill
skill_view(name='auto-register')

# Jalankan registrasi
terminal(command="python3 ~/.hermes/skills/airdrop/auto-register/register.py --url 'https://avazaky.com/'")
```

## Config File Format

Buat file `~/airdrop-agent/config/register_config.json`:

```json
{
  "default_data": {
    "email": "otamaagent7@gmail.com",
    "wallet": "0x000C0e48DC08987954631249Cffba71B5EfaD263",
    "twitter": "@otama777A",
    "discord": "username#0000",
    "telegram": "@username",
    "name": "Otama",
    "age": "25",
    "country": "Indonesia",
    "timezone": "UTC+7"
  },
  "field_mapping": {
    "email": ["email", "e-mail", "correo", "メール"],
    "wallet": ["wallet", "address", "ethereum", "0x"],
    "twitter": ["twitter", "handle", "@"],
    "discord": ["discord", "discord username"],
    "telegram": ["telegram", "tg"],
    "name": ["name", "full name", "username"],
    "age": ["age", "how old"],
    "country": ["country", "nation", "location"],
    "timezone": ["timezone", "time zone", "gmt"]
  },
  "captcha": {
    "enabled": true,
    "service": "2captcha",
    "api_key": ""
  },
  "anti_detection": {
    "use_camoufox": true,
    "random_delay": true,
    "min_delay": 1,
    "max_delay": 3
  }
}
```

## OTP / Segmented Code Input (CRITICAL)

Many airdrop sites use segmented OTP input (6 individual boxes, `maxlength="1"`). **`fill()` does NOT work** on these — the input framework (often `input-otp` or custom React) ignores programmatic fills.

**Working pattern:**
```python
# 1. Click first box to focus
first_input = page.locator("input[aria-label='Character 1 of 6']").first
first_input.click(force=True)
time.sleep(0.3)

# 2. Type digits via keyboard (NOT fill!)
for digit in code:
    page.keyboard.press(digit)
    time.sleep(0.2)
```

**Why it fails with fill():**
- OTP libraries listen for `keydown`/`input` events, not value changes
- `fill()` sets value but doesn't fire the right events
- Each box auto-advances focus on `keydown` — must simulate real keystrokes

**Verification:** After typing, check button text changes (e.g., "Verifying...") to confirm input was accepted.

## Obfuscated/Behind-Modal Button Clicks

When Playwright reports `subtree intercepts pointer events`, the target element is behind another overlay. Don't retry with `force=True` on the locator — use JavaScript:

```python
page.evaluate("""() => {
    const buttons = document.querySelectorAll('button');
    for (const b of buttons) {
        if (b.textContent.includes('Already have an access code')) {
            b.click();
            return true;
        }
    }
    return false;
}""")
```

This bypasses z-index/overlay issues entirely.

## Field Detection Logic

Script mendeteksi field berdasarkan:
1. **Label text** - Cari label yang mengandung keyword
2. **Placeholder text** - Cari placeholder yang mengandung keyword
3. **Name attribute** - Cari name attribute yang mengandung keyword
4. **ID attribute** - Cari ID yang mengandung keyword
5. **Type attribute** - Deteksi type (email, text, tel, dll)

## Supported Field Types

- `text` - Text input
- `email` - Email input
- `tel` - Phone input
- `url` - URL input
- `number` - Number input
- `select` - Dropdown select
- `checkbox` - Checkbox
- `radio` - Radio button
- `textarea` - Textarea

## CAPTCHA Integration

Mendukung:
- reCAPTCHA v2/v3
- hCaptcha
- Turnstile (Cloudflare)

Dengan integrasi skill `auto-resolve-captcha`.

## Multi-Step Registration

Script mendeteksi:
1. Tombol "Next", "Continue", "Submit"
2. Step indicators
3. Form sections
4. Progress bar

## API Extraction

Skill ini juga bisa mengekstrak API endpoints dari website target. Lihat:
- `references/api-extraction.md` - Teknik ekstrak API
- `references/jay-games-api.md` - Contoh hasil ekstrak

### Quick API Extraction
```bash
# Cari semua API endpoints
curl -s "https://target.com/" | grep -oE "api\.php\?[a-z_]+=[^\"'&]+" | sort | uniq

# Cari fetch patterns
curl -s "https://target.com/" | grep -oE "fetch\([^)]+\)" | head -20
```

## Output

```
~/airdrop-agent/data/registrations/
├── {website_name}_{timestamp}.json    # Data registrasi
├── {website_name}_{timestamp}.png     # Screenshot
└── registrations_log.json             # Log semua registrasi
```

## Error Handling

- CAPTCHA gagal → Retry 3x
- Form tidak ditemukan → Cari alternatif selector
- Timeout → Screenshot + log error
- Network error → Retry dengan backoff

## Pitfalls

### Bot Detection (CRITICAL)
Many airdrop sites block requests without proper User-Agent header.

**Curl works:**
```bash
curl -s -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" "https://example.com/api"
```

**Browser fetch fails from headless:**
```javascript
// Returns {error: "bot blocked"} without proper context
fetch('api.php?api=stats')
```

**Solution:** Always use browser with User-Agent set, or use curl with proper headers.

### JAY Wallet vs EVM Addresses
Some platforms (like JAY Games) use their own wallet format (e.g., `yjay...`), not EVM addresses (`0x...`). The API will return "Invalid wallet" if you use the wrong format.

### Twitter Rate Limits
Twitter OAuth can rate-limit login attempts. If you see "We've temporarily limited your login":
- Wait 15-30 minutes before retrying
- Use a device that's already logged into Twitter
- Open the OAuth URL directly in a logged-in browser

### Waitlist Registration Pattern
Many airdrop platforms use "waitlist" instead of direct registration:
- Umbra Privacy, Layer3 early access, etc.
- Flow: Email → Referral code → "Join waitlist" → Email verification
- Submit button may be DISABLED until email field is filled
- Referral codes often auto-fill from URL parameter `?ref=XXXXX`
- No wallet connection needed for waitlist

**Detection:** Look for "waitlist", "early access", "join the queue" in modal text.

### Session Storage
Many Web3 games store wallet connection in `sessionStorage`, not `localStorage`. Each browser session is isolated - wallet connected in one session won't persist to another.

## Multi-Email Batch Registration

Untuk daftar beberapa email ke satu platform (contoh: Umbra, Avazaky):
- Cek API dulu (MANDATORY)
- Background registration via curl/requests jika ada API
- Camoufox browser jika tidak ada API
- Random delay 5-30 detik antara register
- Max 5 email/jam untuk hindari rate limit

Detail lengkap: `references/multi-email-batch-registration.md`

## Best Practices

1. Selalu cek screenshot setelah registrasi
2. Verifikasi email jika diperlukan
3. Simpan data registrasi untuk tracking
4. Gunakan delay random untuk hindari deteksi
5. Monitor log untuk error
6. Selalu sertakan User-Agent di setiap request
7. Cek format wallet address (EVM vs platform-specific)
8. Simpan session ID untuk polling status

## Pitfalls

1. **Bot Detection** - Browser fetch sering diblokir. Gunakan curl dengan User-Agent untuk API calls
2. **CORS Issues** - API mungkin hanya bisa diakses dari domain tertentu
3. **Rate Limiting** - Tambah delay antara requests untuk hindari blokir
4. **Session Required** - Beberapa API butuh session/cookie dari browser
5. **Field Detection** - Tidak semua field terdeteksi otomatis, perlu manual mapping

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| Camoufox error | `pip install camoufox` |
| Form tidak terisi | Cek screenshot, mungkin field tidak dikenali |
| Submit tidak ditemukan | Cek screenshot, mungkin perlu manual click |
| CAPTCHA gagal | Pastikan skill auto-resolve-captcha terinstall |
| API bot blocked | Tambah User-Agent header |
| Invalid wallet | Cek format wallet (EVM vs platform-specific) |

## References

- `references/jay-games-api.md` — Complete JAY Games API documentation with endpoints, examples, and wallet format details.
- `references/umbra-privacy.md` — Umbra Privacy waitlist + access code flow, API endpoints, OTP input pitfalls.

## Security

- Jangan simpan password di config
- Gunakan environment variable untuk API key
- Rotate proxy untuk hindari IP ban
- Monitor akun untuk aktivitas mencurigakan

## Registration Type Detection

Before automating, detect the registration type:

| Type | Indicators | Approach |
|------|-----------|----------|
| **Email Waitlist** | "Join waitlist", email input, referral code | Fill email + referral, submit |
| **Wallet Connect** | "Connect Wallet", MetaMask/WalletConnect buttons | Inject wallet or WalletConnect |
| **Social Login** | "Continue with Google/Twitter/Discord" | OAuth flow |
| **Full Form** | Multiple fields (name, email, wallet, social) | Standard form fill |

**Detection script:**
```python
# Click primary CTA first
page.locator("button:has-text('Get Started'), button:has-text('Register'), button:has-text('Join')").first.click()
time.sleep(2)

# Check what modal/form appears
modal = page.locator("[class*='modal'], [role='dialog']").first
if modal.is_visible():
    text = modal.text_content().lower()
    if 'waitlist' in text or 'email' in text:
        return 'waitlist'
    elif 'wallet' in text or 'metamask' in text:
        return 'wallet'
    elif 'google' in text or 'twitter' in text:
        return 'social'
```

## References

- `references/privy-auth-patterns.md` — Privy auth provider patterns: SIWE flow, MetaMask injection failure, Terms modal handling
- `references/api-extraction.md` - Teknik ekstrak API dari website
- `references/jay-games-api.md` - Contoh API JAY Games
- `references/umbra-privacy-api.md` - Umbra Privacy waitlist registration (email + referral)
