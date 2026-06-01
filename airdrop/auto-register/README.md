# Auto-Register Skill

Otomatisasi registrasi di website airdrop.

## File Structure

```
auto-register/
├── SKILL.md              # Dokumentasi skill
├── register.py           # Script registrasi lengkap
├── quick_register.py     # Registrasi cepat
├── config_template.json  # Template config
└── README.md             # File ini
```

## Cara Pakai

### 1. Quick Register (Paling Mudah)

```bash
# Register dengan data default
python3 ~/.hermes/skills/airdrop/auto-register/quick_register.py "https://example.com/register"

# Register dengan custom data
python3 ~/.hermes/skills/airdrop/auto-register/quick_register.py "https://example.com/register" '{"email":"custom@email.com","wallet":"0x123..."}'
```

### 2. Full Register (Lebih Lengkap)

```bash
# Dengan config file
python3 ~/.hermes/skills/airdrop/auto-register/register.py --url "https://example.com/register" --config ~/airdrop-agent/config/register_config.json

# Dengan custom data
python3 ~/.hermes/skills/airdrop/auto-register/register.py --url "https://example.com/register" --data '{"email":"custom@email.com"}'

# Tanpa screenshot
python3 ~/.hermes/skills/airdrop/auto-register/register.py --url "https://example.com/register" --no-screenshot
```

### 3. Dalam Agent

```python
# Quick register
terminal(command='python3 ~/.hermes/skills/airdrop/auto-register/quick_register.py "https://avazaky.com/"')

# Dengan custom data
terminal(command='python3 ~/.hermes/skills/airdrop/auto-register/quick_register.py "https://example.com" \'{"email":"test@test.com"}\'')
```

## Default Data

```json
{
  "email": "otamaagent7@gmail.com",
  "wallet": "0x000C0e48DC08987954631249Cffba71B5EfaD263",
  "twitter": "@otama777A",
  "name": "Otama",
  "age": "25",
  "country": "Indonesia",
  "timezone": "UTC+7"
}
```

## Output

- **Screenshot:** `~/airdrop-agent/data/screenshots/`
- **Registrasi data:** `~/airdrop-agent/data/registrations/`
- **Log:** `~/airdrop-agent/data/registrations/registrations_log.json`

## Field Detection

Script mendeteksi field berdasarkan keyword:

| Field | Keywords |
|-------|----------|
| email | email, e-mail, mail |
| wallet | wallet, address, ethereum, 0x, evm |
| twitter | twitter, handle, x.com |
| name | name, username, full name |
| age | age, umur |
| country | country, nation, location |
| timezone | timezone, time zone, gmt |

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| Camoufox error | `pip install camoufox` |
| Form tidak terisi | Cek screenshot, mungkin field tidak dikenali |
| Submit tidak ditemukan | Cek screenshot, mungkin perlu manual click |
| CAPTCHA gagal | Pastikan skill auto-resolve-captcha terinstall |

## Tips

1. Selalu cek screenshot setelah registrasi
2. Verifikasi email jika diperlukan
3. Gunakan config file untuk registrasi berulang
4. Monitor log untuk track semua registrasi
