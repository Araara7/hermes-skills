---
name: airdrop-manager
description: Master orchestrator for web3 airdrop agent — project setup, credential management, wallet operations, task automation, reporting to user
tags: [airdrop, web3, automation, wallet, credentials]
---

# 🎯 Airdrop Manager

Orchestrator skill untuk mengelola airdrop web3 secara otomatis. Mengkoordinasi semua skill airdrop lainnya.

## User Preferences (WAJIB DIIKUTI)

- **Bahasa**: Selalu gunakan Bahasa Indonesia
- **Browser**: MINIMALISIR penggunaan browser — hanya untuk ekstraksi token/cookies, lalu tutup
- **Reporting**: Kirim laporan berkala ke user (Telegram)
- **Credentials**: Simpan di `~/airdrop-agent/config/credentials/` dengan chmod 600
- **1 Akun Only**: Tidak ada multi-akun/sybil —gunakan 1 akun asli user
- **Workflow**: Selalu cek `skills_list` dulu sebelum eksekusi tugas → load skill relevan → eksekusi → rekomendasikan skill tambahan jika perlu
- **Telegram Output**: HANYA kirim hasil akhir/summary ke Telegram. JANGAN kirim raw terminal commands, sleep output, debug logs. Proses debugging = diam di background, kirim summary saja. **JANGAN spam Telegram saat sedang kerja** — diam, eksekusi, kirim report final aja.
- **GitHub Research**: Saat stuck, cari repository GitHub yang berkaitan untuk memudahkan pekerjaan. Jangan hanya coba sendiri — research solusi yang sudah ada.
- **Install Repo**: Boleh install repo bagus untuk project airdrop tanpa minta izin. Cukup laporan ke user setelah install: "Installed: [nama repo] — [fungsi]"

## Alur Kerja

### 0. API-First Principle (CRITICAL)

**Selalu test API dulu sebelum buka browser!**

```bash
# Test koneksi API dengan User-Agent
curl -s -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  "https://platform.com/api.php?api=stats&wallet=WALLET"

# Browser HANYA untuk:
# - QR code scanning (wallet connect)
# - OAuth flows (Twitter, Discord)
# - Data extraction (cookies, tokens)
# Setelah selesai → TUTUP browser, pakai API
```

**Pitfall: Browser timeout pada gaming sites**
- Gaming sites punya JS/canvas berat → browser sering timeout
- API endpoints ringan dan respons instan
- Jika `curl -I` timeout tapi API work → site blokir IP datacenter di WAF level

### 1. Setup Project (Sekali)
```
~/airdrop-agent/
├── config/
│   ├── settings.json
│   ├── wallets.json          ← Multi-chain wallet addresses (chmod 600)
│   ├── register_config.json  ← Auto-fill data untuk registrasi
│   └── credentials/
│       ├── accounts.json
│       └── .env
├── scripts/
│   ├── jay_sudoku_solver.py  ← Main earner (JAY Games)
│   ├── wallet_module.py      ← Multi-chain wallet (Cosmos/EVM/Solana)
│   ├── vpn_manager.sh        ← Cloudflare WARP manager
│   ├── _deprecated/          ← Old chess scripts
│   └── _archive/             ← Old umbra, twitter scripts
├── data/
│   └── projects/
│       └── _index.json       ← Master project tracker
└── logs/
```

### 2. Credential Flow (SECURITY-CRITICAL)

**⚠️ LESSON LEARNED (1 Jun 2026):** Private key di plain text di script = wallet compromised. User marah besar. JANGAN ulangi.

**Step-by-step:**
1. User berikan credentials
2. **LANGSUNG simpan ke `.env`** — JANGAN pernah hardcode di script
3. Jalankan `chmod 600` pada semua `.env` dan `config/credentials/*.json`
4. Pastikan `.gitignore` blokir `.env`, `config/credentials/*.json`, `*.key`, `*.pem`
5. Simpan metadata ke `accounts.json` (tanpa secrets)
6. Login sekali → ambil token/cookies
7. Simpan token → tidak perlu buka browser lagi
8. Gunakan token untuk automasi

**Config Loader Pattern (WAJIB dipakai di semua script):**
```python
# config_loader.py — single source of truth untuk semua secrets
import os
from pathlib import Path

def get_config():
    env_paths = [
        Path(__file__).parent / ".env",
        Path(__file__).parent / "config" / "credentials" / ".env",
    ]
    config = {}
    for env_path in env_paths:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        key, value = key.strip(), value.strip().strip('"').strip("'")
                        if value and not value.startswith("<") and value != "***":
                            config[key.lower()] = value
    return {
        "wallet_private_key": config.get("new_wallet_private_key") or config.get("wallet_private_key", ""),
        "galxe_wallet_key": config.get("galxe_wallet_key", ""),
        "gmail_user": config.get("gmail_user", ""),
        # ... tambahkan sesuai kebutuhan
    }

def get_key(name: str) -> str:
    return get_config().get(name, "")
```

**Usage di script:**
```python
from config_loader import get_key
PRIV_KEY = get_key("wallet_private_key")  # ← dari .env, bukan hardcoded
```

**Audit command (jalankan berkala):**
```bash
grep -rn "0x[0-9a-fA-F]\{60,\}\|private_key.*=.*['\"]" ~/airdrop-agent/scripts/ --include="*.py" | grep -v "config_loader\|import\|#\|0x0000"
```

### 3. Wallet Management (SECURITY-HARDENED)

Gunakan `wallet_module.py` untuk semua wallet operations:

```python
from wallet_module import derive_all, cosmos_sign, evm_sign, solana_sign

# Get all wallets from single seed
wallets = derive_all()
# wallets["cosmos"]["address"]  → yjay1aervd...
# wallets["evm"]["address"]     → 0xb01Eaede...
# wallets["solana"]["address"]  → D98Jh6rr2gtc...

# Sign messages
cosmos_sig = cosmos_sign(message, priv_key, wallet, pub_key_b64)
evm_sig = evm_sign(message, priv_key_hex)
solana_sig = solana_sign(message, keypair)
```

**Config:** `~/airdrop-agent/config/wallets.json` (chmod 600)
**Addresses:** Cosmos, EVM, Solana — all derived from single seed phrase.

**⚠️ SECURITY RULES (post-compromise, 1 Jun 2026):**
- Private key JANGAN pernah di-hardcode di script — ambil dari `config_loader.py` → `.env`
- Config files → `chmod 600`, JANGAN world-readable
- Hot wallet (farming) ≠ cold wallet (storage) — pisahkan!
- Auto-sweep: kalau wallet terima dana, langsung pindah ke cold wallet
- Audit berkala: `grep -rn "priv.*key\|seed\|0x[0-9a-f]\{64\}" ~/airdrop-agent/scripts/`
- Full security guide: `airdrop-wallet-connect` skill → Key Management Security section
- **Config loader template:** `templates/config_loader.py` — copy ke project root, semua script import dari sana

### 4. Task Execution
1. Cek task baru dari trackers
2. Eksekusi task (swap, bridge, stake, dll)
3. Update progress
4. Simpan buti (screenshot/hash)
5. Kirim laporan ke user

### 5. Reporting Format
```
📊 LAPORAN AIRDROP [TANGGAL]

✅ Task Selesai:
- [task1]
- [task2]

⏳ Dalam Progress:
- [task3]

📅 Deadline Mendekati:
- [project] - [deadline]

💰 Claimable:
- [project] - [amount]
```

### Galxe Automation

**Auth:** SIWE wallet sign → JWT (no browser). Full API reference: `references/galxe-api.md`

**Script:** `~/airdrop-agent/scripts/galxe_full_auto.py` (v9)
- Auto-auth via SIWE
- Scan 50 trending + 50 popular campaigns
- Verify API-only tasks (EVM_ADDRESS, BALANCE, GALXE_ID follow)
- **Verify Twitter social tasks** (follow, like, retweet, tweet) via `syncCredentialValue` + WASM captcha
- Auto-claim when all tasks eligible
- Skip VISIT_LINK tasks (server-side JWT, can't auto-visit)

**Cron:** Daily 10:00 WIB — scan + verify + claim + report

**Social Task Verification (Twitter):**
1. Generate WASM captcha via Chromium (`galxe_captcha_solver.py`)
2. Strip `ok` field from captcha output
3. Call `syncCredentialValue` with `syncOptions.twitter.captcha` + `syncOptions.twitter.campaignID`
4. Check `twitterOauth2Status` for mock mode (`mockFollow: true` = no Twitter API check)

**Critical Pitfall:** Mock mode does NOT bypass expired OAuth token. If connected Twitter's OAuth2 token is expired → all social verifies return `allow: false`. Solution: reconnect Twitter via browser OAuth or use `VerifyTwitterOauth2Token` mutation with fresh token.

**Social Account API:**
- `getSocialAuthUrl(schema, type: TWITTER)` → OAuth URL
- `deleteSocialAccount(input: {address, type: TWITTER})` → disconnect
- `addressInfo(address)` → `twitterUserID`, `twitterUserName`, `hasTwitter`
- Full reference: `auto-resolve-captcha` skill → `references/galxe-social-api.md`

**User:** Aphrodite7 (Twitter @agy_sabdany7 connected, @otama777A preferred)

## Skill Dependencies

| Skill | Fungsi |
|-------|--------|
| anti-ip-detection | Proxy rotation, fingerprinting, Cloudflare WARP |
| auto-resolve-captcha | Solve CAPTCHA otomatis (third-party) |
| auto-get-token | Ekstraksi JWT/API token |
| airdrop-api-discovery | Auto-detect API endpoints |
| airdrop-wallet-connect | Multi-chain wallet templates |
| airdrop-project-tracker | Track semua project, tasks, earnings |
| web3-airdrop-automation | Twitter/social automation patterns |

## Backup & Restore Strategy

Data airdrop agent terbagi 2 kategori:
- **Code/scripts** → Push ke GitHub public repo (`airdrop-agent`)
- **Sensitive data** → Encrypt + push ke GitHub private repo (`airdrop-agent-backup`)

### Backup Process
```bash
# 1. Pack sensitive data
tar -czf /tmp/backup.tar.gz config/credentials/ data/cookies/ data/umbra/ data/jay_games/ .env

# 2. Encrypt with password
openssl enc -aes-256-cbc -salt -pbkdf2 -in /tmp/backup.tar.gz -out backup-encrypted.tar.gz.enc -pass pass:$PASSWORD

# 3. Push to private repo
cd /tmp/backup_repo && git add backup-encrypted.tar.gz.enc && git commit -m "🔒 Backup $(date +%Y%m%d)" && git push
```

### Restore Process
```bash
# 1. Clone both repos
git clone git@github.com:<user>/airdrop-agent.git
git clone git@github.com:<user>/airdrop-agent-backup.git /tmp/backup

# 2. Decrypt & extract
openssl enc -aes-256-cbc -d -salt -pbkdf2 -in /tmp/backup/backup-encrypted.tar.gz.enc -out /tmp/backup.tar.gz -pass pass:$PASSWORD
cd ~/airdrop-agent && tar -xzf /tmp/backup.tar.gz

# 3. Restore skills (if backed up)
openssl enc -aes-256-cbc -d -salt -pbkdf2 -in /tmp/backup/skills-all-encrypted.tar.gz.enc -out /tmp/skills.tar.gz -pass pass:$PASSWORD
cd / && tar -xzf /tmp/skills.tar.gz && cp -r /tmp/skills_backup/* ~/.hermes/skills/
```

### What to Backup
| File/Dir | Repo | Encrypted? |
|----------|------|-----------|
| `scripts/`, `config/settings.json`, `templates/` | public `airdrop-agent` | No |
| `config/credentials/`, `data/cookies/`, `.env` | private `airdrop-agent-backup` | Yes |
| `data/umbra/`, `data/jay_games/`, `data/projects/` | private `airdrop-agent-backup` | Yes |
| `~/.hermes/skills/` (all skills) | private `airdrop-agent-backup` | Yes |

Quick-restore script (1 command VPS setup): `scripts/quick-restore.sh`
Full backup reference: `references/backup-restore-guide.md`

### Auto-Sync Skills via Cron
Skills bisa di-auto-backup setiap hari via cron job:
```
schedule: 0 10 * * *  (jam 10 pagi)
```
Pattern: encrypt ~/.hermes/skills/ → push ke backup repo → kirim laporan Telegram.
Lihat `references/backup-restore-guide.md` section "Skills Auto-Sync Cron".

### 6. Daily Briefing Automation

User ingin briefing harian otomatis jam 7 pagi via Telegram. Pattern:

```
Cron: "0 7 * * *"
Skills: ["airdrop-manager", "jay-chess-monitor"]
```

Briefing harus mencakup:
1. **JAY Games** — claims X/15, UJAY, status Sudoku auto-solver
2. **JAY Mining** — hash rate, earnings, screen status
3. **Umbra** — email terbaru via himalaya
4. **Projects** — baca ~/airdrop-agent/data/projects/, deadline mendekati
5. **Cron Jobs** — cek semua cron aktif, apakah ada error

Format:
```
📊 BRIEFING AIRDROP — [TANGGAL]
🎮 JAY Games: [claims/15, UJAY, verified]
⛏️ JAY Mining: [status]
📧 Umbra: [status]
🎯 Projects: [list + deadline]
⏰ Cron Jobs: [status]
📋 Task Hari Ini: [list]
```

### 7. VPS Lifecycle Management

User VPS aktif 1 bulan. Set reminder sebelum expired:
- **3 hari sebelum** — warning perpanjang
- **1 hari sebelum** — urgent reminder

Pattern cron (one-shot):
```
schedule: "2026-06-10T08:00:00"  (sesuaikan tanggal)
repeat: once
```

Selalu cek `uptime -s` untuk tahu tanggal mulai VPS.

## Research

- **GitHub repos untuk web3 automation**: `references/github-repos-web3.md` — multicall, testnet bots, bridge automation, mining bots. Update berkala.

### GitHub Research Workflow (SAAT STUCK)

Ketika stuck di suatu task, langsung cari solusi di GitHub:

```bash
# Search repos via GitHub API
curl -s "https://api.github.com/search/repositories?q=QUERY+language:python&sort=stars&per_page=5" | \
  jq '.items[] | {name, full_name, description, stars: .stargazers_count, updated: .updated_at}'

# Clone & inspect
git clone https://github.com/USER/REPO.git /tmp/repo_inspect
ls /tmp/repo_inspect/
cat /tmp/repo_inspect/README.md | head -50
```

**Search patterns:**
- `[platform] bot automation` — e.g. "pixiechess bot", "airdrop bot"
- `[protocol] api python` — e.g. "privy api python", "cosmos signing"
- `[game] websocket automation` — e.g. "chess websocket stockfish"
- `captcha solver camoufox` — anti-detection CAPTCHA solving

**Jika repo bagus ditemukan:**
1. Baca README — pastikan relevan
2. Cek stars, issues, last update
3. Clone ke `/tmp/` → inspect kode
4. Jika berguna → install/dependensi + inform user
5. Tambahkan ke skill references jika pattern-nya reusable

## Related References
- `references/github-repos-airdrop.md` — GitHub repos untuk improve airdrop automation (updated Juni 2026, termasuk Galxe)
- `references/galxe-api.md` — Galxe GraphQL API: auth, queries, task types, pitfalls
- Galxe automation: `~/airdrop-agent/galxe-autocomplete-tasks/` — browser console script, perlu adaptasi ke Camoufox

### GitHub Skills Repo Auto-Sync
Skills di-push otomatis ke `github.com/Araara7/hermes-skills` setiap hari jam 10 WIB.
Cron job: `skills-github-sync` (job_id: `025d10ecbce5`)
Pattern: rsync ~/.hermes/skills/ → clone repo → diff → commit → push

### Wallet Security Monitoring
**PENTING:** Monitor wallet activity secara berkala. Jika wallet mengirim token tanpa inisiasi dari script kita → kemungkinan private key compromised.

**Full investigation workflow:** `references/wallet-security-monitoring.md` — includes multi-chain check, attacker profiling, EIP-7702 detection, VPS leak audit.

**Quick check:**
```bash
for chain in base gnosis optimism arbitrum; do
  curl -s "https://${chain}.blockscout.com/api/v2/addresses/<WALLET>/transactions" | \
    python3 -c "import sys,json; d=json.load(sys.stdin); items=d.get('items',[]); print(f'{chain}: {len(items)} txs, latest: {items[0][\"timestamp\"][:19] if items else \"none\"}')" 2>/dev/null
done
```

**Jika terdeteksi unauthorized TX:**
1. Jangan panic — cek dulu apakah TX berasal dari script kita
2. Build timeline across all chains (lihat reference)
3. Profile attacker address (balance, victims, infrastructure)
4. Cek VPS untuk leak source: `grep -rn "priv.*key\|seed\|0x[0-9a-f]\{64\}" ~/airdrop-agent/`
5. Jika confirmed compromised → segera generate wallet baru, update semua config
6. Report ke user dengan detail attacker

### Compromised Wallet Airdrop Recovery

Ketika wallet compromised (attacker punya private key) tapi wallet masih eligible airdrop:

**Race Condition:** User DAN attacker punya akses sama. Klaim airdrop = siapa cepat dia dapat.

**Strategy (Flashbots Protect):**
1. Monitor eligibility — `earni.fi`, `airdrops.io`, official claim pages
2. Deposit gas via **Flashbots Protect** (private RPC) — attacker tidak bisa lihat TX
3. Klaim airdrop via Flashbots Protect
4. Transfer hasil ke wallet baru — semua dalam private mempool

**Protected RPC Endpoints:**
```python
PROTECTED_RPCS = {
    "ethereum": "https://rpc.mevblocker.io",
    "arbitrum": "https://rpc.flashbots.net/arbitrum",
    "optimism": "https://rpc.flashbots.net/optimism",
    "base": "https://rpc.flashbots.net/base",
    "polygon": "https://rpc.flashbots.net/polygon",
    "bsc": "https://bsc.meowrpc.com",
}
```

**Critical:** JANGAN deposit gas ke wallet lama tanpa langsung klaim! Attacker bisa sweep gas yang di-deposit. Deposit + klaim harus secepat mungkin, ideally dalam block yang sama.

**Scripts:**
- `~/airdrop-agent/scripts/flashbots_protect.py` — TX sender via private RPC
- `~/airdrop-agent/scripts/airdrop_protect.py` — full claim workflow

Full reference: `testnet-operations` skill → "Private RPC / Flashbots Protect" section.
See also: `references/flashbots-protect.md` — endpoints, usage, BscScan V2 migration.
See also: `references/airdrop-recovery-compromised.md` — full recovery workflow for compromised wallets.

### Nodriver (Anti-Detect Browser)
Python anti-detect browser, CDP-based, no Selenium. Best untuk bypass bot detection.
```python
import nodriver as uc
CHROME = "/home/ubuntu/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome"
browser = await uc.start(headless=True, browser_executable_path=CHROME,
    browser_args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'])
# navigator.webdriver = false (undetected!)
```
Combo: **nodriver** (anti-detect navigate) + **Chromium** (WASM captcha) = full coverage.

## Pitfalls

⚠️ **JANGAN:**
- Buka browser terus-menerus
- **Simpan private key di plain text di script** ← PENYEBAB WALLET COMPROMISE 1 JUN 2026
- Hardcode key di `PRIV_KEY = "0x..."` — selalu pakai `config_loader.py` + `.env`
- Multi-akun/sybil attack
- Share credentials
- Pakai free proxy (90%+ dead, blacklisted)
- Coba inject auth ke Galxe browser (server-side JWT, tidak bisa)
- Simpan seed phrase di `.json` file — pindahkan ke `.env`
- Skip `chmod 600` pada credential files

✅ **LAKUKAN:**
- Login sekali → simpan token
- Gunakan API/token untuk automasi
- Encrypt sensitive data
- Kirim laporan ke user
- Pakai wallet_module.py untuk semua chain signing
- Pakai Cloudflare WARP atau hide.me untuk ganti IP (bukan free proxy)
- Pakai subprocess untuk Camoufox jika nested call (sync API tidak bisa re-enter)
- **Semua secret lewat `.env` + `config_loader.py`** — TIDAK ADA EXCEPTION
