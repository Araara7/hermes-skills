---
name: jay-chess-monitor
description: "JAY Games automation & monitoring — Next.js site, Sudoku Expert auto-solver, full API flow working (connect→play→submit→claim), 0.25 JAY/game unverified, cron automated"
tags: [airdrop, jay-games, chess, monitoring]
---

# JAY Games Chess Monitor

## 🚨 SITE UPDATE STATUS (30 Mei 2026)

**JAY Games site structure (updated 31 Mei 2026):**
- Main site: `https://games.thejaynetwork.com/` (hybrid PHP + Next.js frontend)
- Game pages: `game.php?id=155` (Sudoku), `game.php?id=77` (Chess), etc — **STILL PHP**
- Game iframes: `g/jay-sudoku.html`, `g/chess.html`, etc
- **api.php endpoints STILL WORK** (stats, claim, session_token, claim_nonce, qr_create, qr_confirm)
- `/api/` REST endpoints are **DEAD** (return HTML) — do NOT use
- 14 games available (not 12 as previously reported)

**Games yang tersedia (12):**
- Tower Defense, JAY Sudoku, JAY Squad, JAY Cresta, JAY Tank
- Othello Arena, **Janggi Arena** (Korean chess), Connect Four
- JAY Tetris, Cryptogram, JAY Outpost, JAY Picross

**Reward system baru:**
- Unverified: 0.05× reward
- Verified (X/Twitter): up to 250 JAY/hari
- Per game: 5 JAY (verified)

**Action needed:** Script chess v5 TIDAK BISA DIPAKAI lagi. Perlu buat automation baru untuk game yang tersedia.

---

**⚠️ CRITICAL: Security Fix (2 Juni 2026)**
Seed phrase was hardcoded in `jay_sudoku_solver.py` line 34. Fixed to load from wallets.json:
```python
# SEBELUM (Bocor!):
SEED_PHRASE = "museum length cake oven wasp..."

# SEKARANG (Aman):
_wallets_path = Path.home() / "airdrop-agent" / "config" / "wallets.json"
with open(_wallets_path) as _f:
    SEED_PHRASE = json.load(_f)["master_seed"]
```
Also check: cron output logs may contain seed phrase from previous runs. Delete any log files containing the seed.

## ⚠️ ATURAN KETAT (WAJIB DIKUTI)

### Safety Rules:
1. **Error Limit**: Jika game reset/error **3x berturut-turut** → **STOP bermain**
2. **Game Over Limit**: Jika game over **5x** → **STOP bermain**
3. **Claim Fail Limit**: Jika claim gagal **3x berturut-turut** → **STOP bermain** (kecuali retriable errors: "Play longer", "Transaction failed", "Unexpected token")
4. **Max Claim Attempts**: **5 attempts** per claim cycle (retriable errors don't count)
4. **No Restart Loop**: JANGAN terus-menerus restart game
5. **Max Moves**: Maksimal **50 moves** per session
6. **Points Check**: Jika points >= 200 → **CLAIM REWARD**, jangan main lagi

### Error Handling:
```
error_count = 0
claim_fail_count = 0
max_errors = 3
max_claim_fails = 3
max_claim_attempts = 5  # Increased from 3 — retriable errors need more attempts

RETRIABLE_ERRORS = ["play longer", "play more", "transaction failed", "unexpected token"]
DAILY_LIMIT_ERRORS = ["daily claim limit reached", "claim limit"]  # normal exit, not a failure
RATE_LIMIT_ERRORS = ["too many requests"]  # rate-limited after retries — permanent fail for THIS game, but DON'T count toward 3-fail-stop

for each game_session:
    if error:
        error_count++
        if error_count >= max_errors:
            STOP - jangan restart
            report "Stopped due to errors"
    else:
        error_count = 0  // reset on success
    
    if claim_failed:
        if any(kw in error.lower() for kw in DAILY_LIMIT_ERRORS):
            STOP immediately — daily limit hit, report final stats, exit cleanly
        elif any(kw in error.lower() for kw in RATE_LIMIT_ERRORS):
            SKIP this game — rate-limited after retries, continue to next game
        elif any(kw in error.lower() for kw in RETRIABLE_ERRORS):
            DON'T count — retriable, wait 3s, retry
        else:
            claim_fail_count++
            if claim_fail_count >= max_claim_fails:
                STOP - jangan main lagi
                report "Stopped due to claim failures"
    else:
        claim_fail_count = 0  // reset on success
```

**⚠️ Claim Retriable Errors (PENTING):**
- `"Play longer before claiming"` — server butuh lebih banyak moves, lanjut main
- `"Transaction failed"` — server-side tx issue, retry setelah 3s (biasanya sukses di attempt 2-4)
- `"Unexpected token '<'"` — server returned HTML instead of JSON, retry setelah 3s
- `"Daily claim limit reached"` — **NORMAL EXIT**, bukan error. Daily limit (15 claims) sudah habis. Script akan stop otomatis. Report final stats (claims today, total earned). No fix needed — just wait until tomorrow.
- `"Too many requests, try again later"` — **RATE-LIMIT EXIT**. Happens after multiple "Transaction failed" retries exhaust the server's patience. NOT retriable — skip this game and move to next. Observed pattern: 4× "Transaction failed" → 1× "Too many requests" (Game #11, 2 June 2026). Script continues to next game normally.
- Pattern yang terbukti: attempt 1-3 gagal → attempt 4 sukses. JANGAN stop terlalu awal!

### Setup: venv Required
Ubuntu uses externally-managed Python. Must use venv:
```bash
cd ~/airdrop-agent
python3 -m venv .venv
# Install from PyPI (Tencent mirror may be unreachable — use --index-url fallback)
.venv/bin/pip install --index-url https://pypi.org/simple/ playwright requests bip_utils ecdsa
.venv/bin/playwright install chromium
```

**⚠️ CRITICAL: Seed Phrase Security**
NEVER hardcode seed phrase in script source. Always load from wallets.json:
```python
import json
from pathlib import Path
with open(Path.home() / "airdrop-agent" / "config" / "wallets.json") as f:
    SEED_PHRASE = json.load(f)["master_seed"]
```
This was a real incident — seed was hardcoded in jay_sudoku_solver.py and a skill reference file. Fixed 2 June 2026.

**⚠️ Full dependency list for script v6:**
- `playwright` — browser automation for Sudoku solving
- `requests` — HTTP client for api.php endpoints
- `bip_utils` — wallet derivation (BIP44, RIPEMD160, Bech32). Transitively installs: `ecdsa`, `pycryptodome`, `coincurve`, `pynacl`, etc.
- `ecdsa` — secp256k1 signing for Cosmos TX (explicit dep, needed for send_jay)

**⚠️ Venv recovery — if `.venv` is missing or broken:**
Cron jobs may fail with `No such file or directory` if the venv was deleted or corrupted. The fix is to recreate it:
```bash
cd ~/airdrop-agent && rm -rf .venv && python3 -m venv .venv
.venv/bin/pip install --index-url https://pypi.org/simple/ playwright requests bip_utils
.venv/bin/playwright install chromium
```
The venv is NOT tracked in git — it must exist on the host filesystem.

### Playwright Page Load Pitfall
**JANGAN pakai `wait_until="networkidle"`** — gaming sites sering timeout.
Gunakan:
```python
await page.goto(url, wait_until="domcontentloaded", timeout=120000)
await asyncio.sleep(10)  # tunggu render + session token fetch
```
⚠️ Timeout 60s terlalu pendek untuk games.thejaynetwork.com — gunakan 120s.
⚠️ Site response time ~45 detik — normal, bukan error.

### Playwright DISPLAY Pitfall (EPIPE Error)
Jika muncul `Error: write EPIPE` dari Node.js/Playwright, penyebabnya Xvfb sudah running tapi `DISPLAY` tidak diset.
```bash
# Cek Xvfb running
ps aux | grep Xvfb

# Set DISPLAY sebelum run
export DISPLAY=:99
cd ~/airdrop-agent && .venv/bin/python3 scripts/jay_chess_auto_play_v5.py

# Atau gunakan xvfb-run (TAPI gagal jika Xvfb sudah ada)
# Lebih baik: export DISPLAY=:99 saja
```
**JANGAN** `xvfb-run` jika Xvfb sudah running — akan error `Xvfb failed to start`.

### Playwright Subprocess Output Buffering Pitfall
Jalankan Python dengan `-u` flag untuk unbuffered output. Tanpa flag ini, output dari subprocess tidak muncul sampai selesai:
```bash
# ❌ WRONG — output buffered, tidak terlihat sampai selesai
cd ~/airdrop-agent && .venv/bin/python3 scripts/jay_sudoku_solver.py

# ✅ CORRECT — unbuffered, output real-time
cd ~/airdrop-agent && .venv/bin/python3 -u scripts/jay_sudoku_solver.py
```

Juga berlaku untuk subprocess.run() di dalam script — child process perlu `-u` flag juga.

### Hermes Terminal Tool 600s Timeout Pitfall
When running the solver from Hermes agent (not direct shell), the terminal tool has a **600s foreground max timeout**. The solver takes ~75-82 min for 15 games, so foreground mode WILL timeout.

**Solution:** Use background mode with tee for logging:
```bash
# ✅ CORRECT — background mode, log to file, notified on complete
cd ~/airdrop-agent && DISPLAY=:99 timeout 5400 .venv/bin/python3 -u scripts/jay_sudoku_solver.py 2>&1 | tee /tmp/jay_sudoku_run.log
# Set: background=true, notify_on_complete=true

# Monitor progress:
tail -50 /tmp/jay_sudoku_run.log
```

**❌ WRONG** — foreground with timeout 5400 will silently cap at 600s and kill the process mid-game.

**Observed:** Cron jobs use `timeout 5400` which works fine. Only the Hermes interactive terminal tool has this 600s limit.

### Site Unreachable Detection
```bash
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "https://games.thejaynetwork.com/game.php?id=155"
```
Jika HTTP 200 → OK. Jika timeout/403 → site down atau anti-bot, STOP.
**Note:** Without User-Agent header, site returns "bot blocked" (403). Always include UA.

## ⚠️ PENTING: URLs (UPDATED — Next.js Site)

- **Main site**: `https://games.thejaynetwork.com` (PHP + JS frontend)
- **Game pages**: `game.php?id=155` (Sudoku), `game.php?id=151` (Tower Defense), etc
- **Game iframes**: `g/jay-sudoku.html`, `g/tower-defense.html`, etc
- **Stats API**: ✅ `api.php?api=stats&wallet=WALLET` — works
- **Claim API**: ✅ `api.php?api=claim` — works (with PoW)
- **Session token**: ✅ `api.php?api=session_token` — works (needs Origin header)
- **Claim nonce**: ✅ `api.php?api=claim_nonce` — works (needs Origin header)
- **QR create/confirm/poll**: ✅ Wallet connection via QR flow
- **❌ DEAD**: `/api/wallet/nonce`, `/api/wallet/connect`, `/api/wallet/session`, `/api/play/start`, `/api/score/submit`, `/api/claim` — all return HTML

**Available games (14):**
- Tower Defense (#1), 2048 (#2), Runner (#3), Crypto Racer (#4), JAY Sudoku (#5)
- Flow Arena (#6), JAY Squad (#7), Chess (#8), Breaker (#9)
- Othello Arena (#10), Stack (#11), Block (#12), Cryptogram (#13), Janggi Arena (#14)

## Workflow

### 1. Cek Games Available
```bash
curl -s -H "User-Agent: Mozilla/5.0" "https://games.thejaynetwork.com/" | grep -oE 'href="/play/[^"]+' | sort -u
```

### 2. Run Sudoku Automation
```bash
cd ~/airdrop-agent && DISPLAY=:99 .venv/bin/python3 -u scripts/jay_sudoku_solver.py
```

### 3. Cek Stats (WORKING as of 31 Mei 2026)
Stats API works — returns daily claim count, total earned, and limits:
```bash
curl -s -H "User-Agent: Mozilla/5.0" -H "Origin: https://games.thejaynetwork.com" \
  "https://games.thejaynetwork.com/api.php?api=stats&wallet=WALLET"
# Returns: {"claims":15,"total_ujay":"3750000","max_claims":15,"max_ujay":"50000000","x_verified":false}
```
Use to check if daily limit is already hit before running the solver (avoids wasted Playwright launches).

### 4. (Deprecated) Main Chess — NO LONGER WORKS
Chess game removed from site. Use Sudoku or other games instead.

## Claim Mechanism (Current — api.php + PoW)

### Working API Endpoints (verified 31 Mei 2026)
All endpoints require `Origin: https://games.thejaynetwork.com` header.
```
api.php?api=qr_create              → POST, returns {session_id, qr_data, expires}
api.php?api=qr_confirm             → POST, needs {session_id, wallet} → {success:true}
api.php?api=qr_poll&sid=SID        → GET, returns {status:"connected", wallet}
api.php?api=session_token          → POST, needs {game_id:"155"} → {token}
api.php?api=claim_nonce            → POST, needs {wallet, game_id:155} → {nonce, pow_challenge, difficulty}
api.php?api=claim                  → POST, needs {wallet, game_id, score, session_token, claim_nonce, pow_answer} → {success, reward, x_verified}
api.php?api=stats&wallet=WALLET    → GET, returns {claims, total_ujay, max_claims, max_ujay, x_verified}
api.php?api=x_check&wallet=WALLET  → GET, returns {verified, x_handle}
```

### ❌ DEAD Endpoints (return HTML or empty, do NOT use)
```
/api/wallet/nonce     /api/wallet/connect     /api/wallet/session
/api/play/start       /api/score/submit       /api/claim
/api/rewards/pending
api.php?api=nonce     ← returns 0 bytes (empty response)
```

### Wallet Connection Flow (QR Confirm — WORKING)

```python
# 1. Derive wallet with RIPEMD160(SHA256(pubkey)) — MUST be 43 chars!
seed_bytes = Bip39SeedGenerator(SEED_PHRASE).Generate()
bip44 = Bip44.FromSeed(seed_bytes, Bip44Coins.COSMOS)
acc = bip44.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
pub_compressed = acc.PublicKey().RawCompressed().ToBytes()
ripemd_hash = hashlib.new('ripemd160', hashlib.sha256(pub_compressed).digest()).digest()
WALLET = Bech32Encoder.Encode('yjay', ripemd_hash)  # 43 chars

# 2. Connect via QR confirm
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 ...", "Origin": SITE, "Referer": GAME_PAGE})
r = session.post(f"{SITE}/api.php?api=qr_create")
sid = r.json()["session_id"]
r = session.post(f"{SITE}/api.php?api=qr_confirm", json={"session_id": sid, "wallet": WALLET})
# → {"success": true}

# 3. Load game page to get PHPSESSID cookie
session.get(f"{SITE}/game.php?id=155")

# 4. Get session token
r = session.post(f"{SITE}/api.php?api=session_token", json={"game_id": "155"})
session_token = r.json()["token"]
```

**⚠️ CRITICAL PITFALL — Wallet Address:**
- MUST use `RIPEMD160(SHA256(pubkey))` → 43-char address
- WRONG: `Bech32Encoder.Encode('yjay', pub_compressed)` → 64-char address, INVALID
- The server validates with regex `/^yjay1[a-z0-9]{38}$/` (exactly 43 chars)
- Old (broken) address: `yjay1qdt88wegxa6rk2ehferrr60s7zrqfnnnxltp9dht5vs67paed05czq4xj0r` (64 chars)
- Correct address: `yjay1aervdugs5rngpq3frszvtvsc6v6afwchatvnf6` (43 chars)

### Wallet Connection Flow (DEPRECATED — /api/ endpoints are DEAD)

**⚠️ The old Cosmos Amino signing flow below NO LONGER WORKS.**
**Use QR Confirm flow above instead.**

<details>
<summary>Old flow (for reference only)</summary>

```python
# THIS NO LONGER WORKS — /api/wallet/nonce returns HTML
WALLET = Bech32Encoder.Encode('yjay', acc.PublicKey().RawCompressed().ToBytes())  # WRONG: 64 chars
PRIV_KEY = bytes.fromhex(acc.PrivateKey().Raw().ToHex())
PUB_KEY_B64 = base64.b64encode(acc.PublicKey().RawCompressed().ToBytes()).decode()

resp = session.get(f"{API_BASE}/wallet/nonce?address={WALLET}")
nd = resp.json()["data"]
# ... signing ...
resp = session.post(f"{API_BASE}/wallet/connect", json={...})
```

</details>

**⚠️ CRITICAL LESSON LEARNED (31 Mei 2026):**
- The `/api/` REST endpoints were introduced with the "Next.js migration" but have been **removed/reverted**
- The site still uses the old `api.php` endpoints
- The wallet address derivation was wrong for months: raw pubkey (64 chars) vs RIPEMD160 (43 chars)
- The 64-char address passed old API validation but fails new api.php validation (regex `/^yjay1[a-z0-9]{38}$/`)

### Full Game Flow (api.php — WORKING)

```python
# 1. Connect wallet via QR confirm (see above)

# 2. Load game page + get session token
session.get(f"{SITE}/game.php?id=155")
r = session.post(f"{SITE}/api.php?api=session_token", json={"game_id": "155"})
session_token = r.json()["token"]

# 3. Play Sudoku via Playwright (load game page, solve in iframe, fill cells)
score = 3472  # from win overlay

# 4. Get claim nonce + solve PoW
r = session.post(f"{SITE}/api.php?api=claim_nonce", json={"wallet": WALLET, "game_id": 155})
nd = r.json()
# nd = {nonce, pow_challenge, difficulty}

# Solve PoW: find nonce where SHA256(pow_challenge + nonce) starts with '0'*difficulty
prefix = '0' * nd["difficulty"]
nonce = 0
while True:
    h = hashlib.sha256((nd["pow_challenge"] + str(nonce)).encode()).hexdigest()
    if h.startswith(prefix):
        break
    nonce += 1

# 5. Submit claim
r = session.post(f"{SITE}/api.php?api=claim", json={
    "wallet": WALLET, "game_id": 155, "score": score,
    "session_token": session_token, "claim_nonce": nd["nonce"],
    "pow_answer": str(nonce)
})
# → {"success": true, "reward": 250000, "x_verified": false}
# reward is in uJAY (÷1000000 for JAY)
```

### Cooldown Issue (CRITICAL)

**"cooldown active (layer 4)"** — CDN/proxy rate limit between score submissions.

| Delay | Result |
|-------|--------|
| 30-60s | ❌ Cooldown |
| 90-150s | ❌ Cooldown |
| 300s (5 min) | ✅ Works (sometimes) |
| 330s (5.5 min) | ✅ Reliable |

**Tested pattern (30 Mei 2026):**
- Game 1: success immediately after connect
- Game 2: needs 300-330s wait after Game 1 submit
- Game 3: needs 300-330s wait after Game 2 submit
- Total for 4 games: ~17-20 menit

**Script v5 uses 330s (5.5 min) COOLDOWN_SECONDS.** On cooldown hit, retries in 60s.

### Reward System (VERIFIED WORKING — 31 Mei 2026)
- Unverified: 0.25 JAY/game (reward/20)
- Verified (X/Twitter): 5 JAY/game (reward full)
- Each game claims individually (no pending accumulation needed)
- Daily limits from API: `max_claims: 15`, `max_ujay: 50,000,000` (50 JAY)
- Max daily unverified: 15 × 0.25 = **3.75 JAY**
- Max daily verified: 15 × 5 = **75 JAY** (requires Twitter verify — not yet available)
- Claim returns `{success, reward, x_verified}` — reward in uJAY (÷1000000 for JAY)
- Use `api.php?api=stats&wallet=WALLET` to check current claims/ujay for the day

### Cron Automation (ACTIVE)
Two daily runs to maximize rewards:
- `jay-sudoku-auto` — `0 8 * * *` (08:00 WIB)
- `jay-sudoku-auto-sore` — `0 15 * * *` (15:00 WIB)
Each run: up to 15 games with 5.5 min cooldown, auto-claims at 1 JAY pending.
Expected: ~3.75 JAY/day (unverified).

**⚠️ Timeout Optimization:**
- Each game ~5.5 min (330s cooldown) → 15 games = ~82 min
- Cron timeout MUST be ≥5400s (90 min) to complete all 15 games in one run
- If timeout=3600s (60 min), only ~10 games complete → need backup run at 15:00
- Recommended: set timeout to 5400s for morning run, 5400s for afternoon backup

**⚠️ CRITICAL: Timeout Optimization**
15 games × 5.5 min cooldown = **~82 menit**. Default timeout 3600s (60 mnt) **TIDAK CUKUP**.

| Timeout | Games per run | Notes |
|---------|---------------|-------|
| 3600s (60 mnt) | ~10 game | ❌ Kebutuhan: 2 run/hari |
| 5400s (90 mnt) | ~15 game | ✅ Optimal: 1 run pagi selesai semua |
| 7200s (120 mnt) | ~20 game | Overkill, tapi aman |

**Recommended:** Timeout 5400s, 1 run pagi (08:00) cukup untuk semua 15 game. Run sore (15:00) jadi backup.

**Cron update command:**
```bash
# Update timeout dari 3600s ke 5400s
# Via cronjob action=update, prompt: "cd ~/airdrop-agent && DISPLAY=:99 timeout 5400 .venv/bin/python3 -u scripts/jay_sudoku_solver.py 2>&1"
```

**Daily limit API response:**
- `max_claims`: 15/hari
- `max_ujay`: 50,000,000 (= 50 JAY, reward in uJAY ÷ 1000000)
- Unverified: 15 × 0.25 = 3.75 JAY max/hari
- Verified: 15 × 5 = 75 JAY max/hari (butuh Twitter verify yang belum tersedia)

### Script v6 (`jay_sudoku_solver.py`) — Current
Full automation with:
- QR confirm wallet connection (api.php endpoints)
- PoW challenge solving for claims
- RIPEMD160(SHA256(pubkey)) wallet derivation (43-char address)
- Playwright for Sudoku solving only (~26s per game)
- Auto-cooldown management (330s between claims)
- Auto-claim after each game
- Failure detection (3 consecutive fails → stop)
- Report saved to `~/airdrop-agent/data/sudoku_reports/`

**⚠️ v5 → v6 Breaking Changes (31 Mei 2026):**
- Wallet address: 64 chars (raw pubkey) → 43 chars (RIPEMD160)
- API: `/api/` REST → `api.php` endpoints
- Auth: Cosmos Amino signing → QR confirm flow
- Claim: simple POST → PoW challenge + solve + submit

### 6. Report Format

## Security Fix (2 June 2026)

**Issue:** Seed phrase was hardcoded in `jay_sudoku_solver.py` line 34.
**Fix:** Changed to load from `wallets.json` at runtime:
```python
# BEFORE (INSECURE):
SEED_PHRASE = "museum length cake oven wasp..."

# AFTER (SECURE):
_wallets_path = Path.home() / "airdrop-agent" / "config" / "wallets.json"
with open(_wallets_path) as _f:
    SEED_PHRASE = json.load(_f)["master_seed"]
```

**Also fixed:**
- Removed seed phrase from skill reference file `sudoku-automation.md`
- Deleted cron output that contained leaked seed phrase

**Lesson:** NEVER hardcode seed phrases or private keys. Always load from `wallets.json` or `.env` via `config_loader.py`.

## Security Fix (2 June 2026)
```
📊 JAY Games Chess Monitor
🔌 Koneksi: ✅/❌
🪙 UJAY: X
💰 Claims: X/15
🐦 Twitter: ✅/❌
♟️ Chess: [played/not played/stopped]
⚠️ Errors: X/3
⏰ Next: 6 jam lagi
```

## Twitter Verification

Twitter verify via site's `x_connect` API returns `{"error":"X not configured"}` — server-side OAuth not set up. Verified reward (5 JAY vs 0.25 JAY) currently tidak bisa didapat via automation.

**Status check:**
```bash
curl -s "https://games.thejaynetwork.com/api.php?api=x_check&wallet=WALLET"
# Response: {"verified":false,"x_handle":""} atau {"error":"bot blocked"}
```

**Known Issues (2026-05-30):**
- `x_connect` → `"X not configured"` — OAuth integration broken di server
- `x_check` → `"bot blocked"` jika dari headless browser — gunakan curl
- Manual verification: user buka site di browser sendiri → profile → Verify button
- Reward tanpa verify = 0.25 JAY per claim (÷20)

## Claim Retry Formula (TERRAPAT)

Claim sering gagal di attempt pertama, tapi sukses di attempt ke-3/4. Pola:

**Retriable errors (JANGAN hitung sebagai permanent failure):**
- `"Play longer before claiming"` → main 2-3 moves lagi, retry
- `"Transaction failed"` → tunggu 3s, retry
- `"Unexpected token '<'"` → server hiccup, tunggu 3s, retry

**Non-retriable errors (count as failure):**
- `"Score too low!"` → main lagi sampai score >= 200
- `"Connect wallet first!"` → setup issue
- `"Session error"` → refresh page
- `"bot blocked"` → anti-bot detected
- `"Too many requests, try again later"` → rate-limited after multiple retries, skip game (observed after 4× Transaction failed)

**Settings yang terbukti work:**
- `MAX_CLAIM_ATTEMPTS = 5` (bukan 3)
- Delay 3s antara retry
- Claim SEBELUM game over (score >= 200, moves >= 20)

**Pola sukses yang terobservasi:**
```
Attempt 1: "Play longer" → main lagi
Attempt 2: "Transaction failed" → retry (3s)
Attempt 3: "Transaction failed" → retry (3s)
Attempt 4: ✅ SUCCESS
```

## Game Architecture

Lihat `references/game-architecture.md` untuk detail teknis.

**Key facts:**
- Game page (`game.php?id=77`) punya iframe ke `g/chess.html`
- Chess game punya global JS: `board[][]`, `score`, `playerTurn`, `gameOver`
- Functions: `doMove(fr,fc,tr,tc)`, `getMoves(r,c)`, `aiMove()`, `checkEnd()`, `draw()`
- Board: row 0 = top (black), row 7 = bottom (white). White plays first.
- Score: `VALS[captured]*10` per capture. Pawn=10, Knight/Bishop=30, Rook=50, Queen=90, King=high
- Pawn promotion to Queen adds +8 score
- Score propagates to parent via `window.parent.postMessage({score:score},'*')`
- MIN_SCORE = 200 (site requires min 200 to claim)
- Reward: 5 JAY (verified) atau 0.25 JAY (unverified, ÷20)
- "Play longer before claiming" = server-side check, retriable error

## Anti-Bot Random Delays

Untuk menghindari deteksi bot, gunakan random delays:

| Action | Delay Range |
|--------|-------------|
| Antara moves | 1.5 - 4.0 detik |
| Sebelum claim | 3 - 8 detik |
| Antara games | 30 - 120 detik |
| Page load wait | 8 - 15 detik |
| Cooldown antara game | 3 - 10 detik |

**Implementation:**
```python
import random
delay = random.uniform(1.5, 4.0)
await asyncio.sleep(delay)
```

## JAY Sudoku Automation (Expert Mode)

**Status: ✅ FULLY WORKING (v6 — 31 Mei 2026)** — QR confirm + api.php + PoW claim all confirmed

Script: `~/airdrop-agent/scripts/jay_sudoku_solver.py` (v6)

**Full flow (api.php-based + Playwright):**
1. Derive wallet from seed → RIPEMD160(SHA256(pubkey)) → 43-char address
2. Load game page → PHPSESSID cookie
3. QR confirm → connect wallet
4. POST `api.php?api=session_token` → get session token
5. Playwright: load game.php?id=155 → find sudoku iframe → read puzzle → solve in Python → fill cells → win
6. POST `api.php?api=claim_nonce` → get PoW challenge
7. Solve PoW (SHA256 prefix matching)
8. POST `api.php?api=claim` → +0.25 JAY (unverified)
9. Wait 330s cooldown → repeat

**Performance:** ~26s per game solve, ~5.8 min per game (with cooldown). Claim success rate ~92% (12/13 in 2 June run — 1 game rate-limited by "Too many requests").

**Key pitfalls:**
- `state` is inside IIFE, not accessible via `page.evaluate`. Must solve puzzle independently.
- Sudoku is in an iframe (`g/jay-sudoku.html`), must access via `page.frames` not `page`
- Cooldown 330s between claims (shorter = "cooldown active layer 4")
- First game after connect usually works immediately; subsequent games need cooldown wait
- Score minimum is 10 (MIN_SCORE from game page JS)
- Wallet address MUST be 43 chars (RIPEMD160), NOT 64 chars (raw pubkey)
- All api.php POST endpoints need `Origin: https://games.thejaynetwork.com` header
- PoW difficulty is 4 (find SHA256 hash starting with "0000")

## Background Play

Playwright headless works dengan `DISPLAY=:99` jika Xvfb sudah running:
```bash
cd ~/airdrop-agent && DISPLAY=:99 timeout 300 .venv/bin/python3 scripts/jay_chess_auto_play_v5.py
```

**Pitfall:** Site sangat lambat (~45s response). Timeout HARUS 120s, bukan 30s.

## JAY Token Transfer (Cosmos SDK)

Send JAY tokens between wallets on the JAY Network blockchain. Uses protobuf encoding + secp256k1 signing.

**Full guide**: See `references/cosmos-sdk-signing.md` for complete tx building, signing, and broadcasting code.

Key points:
- Chain ID: `thejaynetwork` (NOT `jaynetwork-1`)
- Chain API: `https://api-jayn.winnode.xyz`
- Signature: 64-byte compact (NOT DER)
- PubKey: nested protobuf encoding required
- Address: RIPEMD160(SHA256(pubkey)) → 43 chars

## References

- `references/sudoku-automation.md` — JAY Sudoku Expert automation (solver, DOM patterns, claim status)
- `references/jay-games-api.md` — JAY Games API quick reference (⚠️ mostly deprecated)
- `references/game-architecture.md` — Chess game JS architecture (⚠️ deprecated, chess removed)
- `references/claim-flow.md` — Claim API detail (⚠️ deprecated, old PHP API)
- `references/site-migration-2026.md` — Site migration notes (PHP → Next.js)
- `references/mining-watchdog-pattern.md` — Mining watchdog cron template
- `references/cosmos-sdk-tx-signing.md` — Cosmos SDK protobuf tx signing (in testnet-operations skill)

## Educational Materials (Drainer/Attack)

Full educational content at `~/airdrop-agent/data/edukasi/`:
- `DrainSimulator.sol` — Smart contract showing approval/drain flow
- `drainer_bot.py` — Bot simulation (scan → detect → drain)
- `deploy_testnet.py` — Deploy to testnet for testing
- `README.md` — Complete guide with attack flow diagrams
- `~/airdrop-agent/data/edukasi_drainer.md` — Attack mechanics explained

## Scripts

### Active
- `~/airdrop-agent/scripts/jay_sudoku_solver.py` — Sudoku Expert v6 (api.php + PoW claim, QR confirm wallet, auto-cooldown)

### Deprecated (PHP site, 404)
- `~/airdrop-agent/scripts/jay_chess_auto_play_v5.py` — Chess automation (site removed)
- `~/airdrop-agent/scripts/jay_chess_auto_play_v4.py` — Old version (canvas-click based)
- `~/airdrop-agent/scripts/jay_chess_maximizer.py` — Multi-game loop (chess removed)
- `~/airdrop-agent/.venv/` — Python venv with playwright + requests installed

## Screen Session Management

**⚠️ USER PREFERENSI: JANGAN kill screen saat repair!**

Cara yang benar untuk restart proses di dalam screen:
1. Kirim Ctrl+C ke screen: `screen -S Jay -X stuff $'\003'`
2. Tunggu 3 detik
3. Jalankan ulang di screen yang sama: `screen -S Jay -X stuff "command\n"`

Cara yang SALAH (user tidak suka):
```bash
screen -S Jay -X quit  # ❌ JANGAN INI
screen -dmS Jay ...     # ❌ JANGAN buat screen baru
```

Capture output dari screen:
```bash
screen -S Jay -X hardcopy /tmp/jay_screen.txt && tail -30 /tmp/jay_screen.txt
```

## Mining Watchdog (Auto-Repair via Cron)

Set up cron job untuk monitor mining + auto-repair. Pola:
1. Cek screen ada atau tidak
2. Capture output, analisa error keywords
3. Jika error: `git pull` + restart di screen yang sama
4. Jika normal: **silent** (jangan kirim pesan)

Error keywords yang perlu diwaspadai:
- `error`, `failed`, `killed`, `terminated`, `connection lost`, `Traceback`, `Exception`
- Tidak ada share baru dalam >20 menit

Alert format:
```
🟢 JAY MINING REPAIRED → [masalah] + [status setelah fix]
🔴 JAY MINING GAGAL DIPERBAIKI → [masalah] + [error setelah fix]
✅ OK → silent
```

Lihat `references/mining-watchdog-pattern.md` untuk template cron job lengkap.

## JAY Mining Status (2 June 2026)

**Mining wallet:** `yjay1s4m4ujrhuda6tmlh9u0jxafgutfjzup55srq0t`
**Sudoku wallet:** `yjay1aervdugs5rngpq3frszvtvsc6v6afwchatvnf6` (RIPEMD160 derived, 43 chars)
**Chain:** `thejaynetwork`, API: `https://api-jayn.winnode.xyz`
**Mining balance:** ~2,572 JAY (pool internal + on-chain)
**Sudoku earnings:** 0.25 JAY/game unverified, max 3.75 JAY/day

## Cosmos SDK TX Signing (JAY Network)

**Critical**: JAY Network uses Cosmos SDK with specific protobuf encoding requirements. Standard approaches fail.

### Key Learnings (verified 2 June 2026):
1. **PubKey encoding**: Must use nested protobuf — `field_bytes(1, pub_compressed)` inside the PubKey Any value
2. **Signature format**: 64-byte compact (r+s), NOT 72-byte DER. Must enforce low-S.
3. **Chain ID**: `thejaynetwork` (not `jaynetwork-1`)
4. **Memo field**: Omit entirely if empty (don't encode empty string)
5. **Account info**: `pub_key: null` on first tx (normal — first tx sets it)

### Quick Reference:
```python
# PubKey (NESTED!)
pubkey_inner = field_bytes(1, pub_compressed)  # field 1 inside field 2
pub_any = field_bytes(1, "/cosmos.crypto.secp256k1.PubKey") + field_bytes(2, pubkey_inner)

# Signature (64-byte compact, low-S)
sig = sk.sign_digest(sign_hash, sigencode=ecdsa.util.sigencode_string)
r_val, s_val = sig[:32], sig[32:]
s_int = int.from_bytes(s_val, 'big')
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
if s_int > n // 2: s_int = n - s_int
signature = r_val + s_int.to_bytes(32, 'big')  # 64 bytes
```

See also: `references/cosmos-sdk-tx-signing.md` in testnet-operations skill for full working example.

## Related Skills
- `web3-gaming-automation` — Parent skill with full API docs, canvas patterns, and troubleshooting
- `anti-ip-detection` — VPN/proxy for IP rotation (Cloudflare WARP free)
- `airdrop-manager` — Master orchestrator for all airdrop tasks
- `testnet-operations` — Cosmos SDK tx signing, bulk transfers, Flashbots Protect