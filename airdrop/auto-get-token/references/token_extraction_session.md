# Token Extraction Learnings - Session Mei 2026

## Twitter Bearer Token

### Cara Capture
Twitter menggunakan public Bearer token untuk API requests. Bisa di-capture dari network traffic:

```python
captured_tokens = []

def handle_request(request):
    headers = request.headers
    if "authorization" in headers:
        captured_tokens.append({
            "type": "authorization",
            "value": headers["authorization"][:100],
            "url": request.url[:80]
        })
```

### Contoh Hasil
```json
{
  "type": "authorization",
  "value": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA3",
  "url": "https://api.x.com/1.1/hashflags.json"
}
```

### Endpoint yang Menggunakan Bearer Token
- `https://api.x.com/1.1/hashflags.json`
- `https://api.x.com/1.1/graphql/user_flow.json`
- `https://x.com/i/jfapi/onboarding/web?mode=login`

## Gmail IMAP

### App Password
Google memerlukan App Password untuk IMAP login dengan 2FA:

```python
import imaplib
mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login("otamaagent7@gmail.com", "ryjb fmjb mcny rzbq")  # App Password
```

### Generate App Password
1. Buka: https://myaccount.google.com/apppasswords
2. Pilih App: Mail
3. Generate 16 karakter

## Google OAuth Challenges

### Masalah
1. Google mendeteksi automated browser
2. Popup GSI tidak trigger di headless mode
3. Cookies tidak maintain session

### Solusi
1. Manual cookie export dari browser asli
2. App Password untuk layanan Google
3. Developer tools untuk extract token

## Penyimpanan Token

### Struktur Folder
```
~/airdrop-agent/config/credentials/
├── .env                    # Credentials sensitif
├── accounts.json           # Status akun
├── twitter_api.json        # Twitter API tokens
└── cookies/
    ├── google_cookies.json
    └── twitter_cookies.json
```

### Format JSON
```json
{
  "twitter": {
    "bearer_token": "Bearer ...",
    "api_base": "https://api.x.com",
    "captured_at": "2026-05-28T13:30:00Z",
    "type": "public_bearer_token"
  }
}
```
