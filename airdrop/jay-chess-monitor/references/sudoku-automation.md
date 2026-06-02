# JAY Sudoku Automation — Expert Mode (Full API Integration)

## Status: ✅ WORKING (v6 — api.php + PoW claim, QR confirm wallet)

Script: `~/airdrop-agent/scripts/jay_sudoku_solver.py`

## Flow (Updated 31 Mei 2026)

1. **Connect wallet** via QR confirm flow (`api.php?api=qr_create` + `qr_confirm`)
2. **Get session token** via `api.php?api=session_token` (game_id=155)
3. **Load game** iframe (`/games/jay-sudoku.html`)
4. **Select Expert** difficulty (×3.5 multiplier)
5. **Read puzzle** from DOM cells (`#board .cell`)
6. **Solve Sudoku** in Python (backtracking algorithm)
7. **Fill cells** via DOM clicks (cell click → number pad click)
8. **Win** → score ~3400-3500
9. **Submit score** via claim flow (PoW challenge → solve → submit)
10. **Repeat** until 15 claims/day max, with 330s cooldown between games

## Performance

- Time: ~26-47 detik per game
- Success rate: 100%
- Cells to fill: ~57 (Expert has 23-24 clues)
- Score range: 3400-3500 (Expert ×3.5)
- Reward: 0.25 JAY per game (unverified)

## API Endpoints (UPDATED 31 Mei 2026 — Use api.php, NOT /api/)

**⚠️ v5 `/api/` REST endpoints are DEAD (return HTML). All endpoints now use `api.php`.**

```
GET  api.php?api=stats&wallet=WALLET     → {claims, total_ujay, max_claims, max_ujay, x_verified}
POST api.php?api=qr_create               → {session_id, qr_data, expires}
POST api.php?api=qr_confirm              → {session_id, wallet} → wallet connect
GET  api.php?api=qr_poll&sid=SID         → {status:"connected", wallet}
POST api.php?api=session_token           → {game_id:"155"} → {token}
POST api.php?api=claim_nonce             → {wallet, game_id:155} → {nonce, pow_challenge, difficulty}
POST api.php?api=claim                   → {wallet, game_id, score, session_token, claim_nonce, pow_answer}
```

**Dead endpoints (DO NOT USE):**
- `/api/wallet/nonce`, `/api/wallet/connect`, `/api/play/start`, `/api/score/submit`, `/api/claim`

## Wallet Connection (v6 — QR Confirm Flow)

```python
import json, hashlib, base64, requests
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes, Bech32Encoder
import hashlib as hl

SEED_PHRASE = "*** # Load from wallets.json, NEVER hardcode"

seed_bytes = Bip39SeedGenerator(SEED_PHRASE).Generate()
bip44 = Bip44.FromSeed(seed_bytes, Bip44Coins.COSMOS)
acc = bip44.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)

# CORRECT: RIPEMD160(SHA256(pubkey)) → 43-char address
pub_bytes = acc.PublicKey().RawCompressed().ToBytes()
sha_hash = hashlib.sha256(pub_bytes).digest()
ripemd_hash = hashlib.new('ripemd160', sha_hash).digest()
WALLET = Bech32Encoder.Encode('yjay', ripemd_hash)  # yjay1aervd...vnf6 (43 chars)

# WRONG (v5): raw pubkey → 64-char address (server rejects with regex /^yjay1[a-z0-9]{38}$/)
# WALLET = Bech32Encoder.Encode('yjay', pub_bytes)  # yjay1qdt88...xj0r (64 chars) ❌

api = requests.Session()
api.headers.update({"User-Agent": "Mozilla/5.0 ...", "Origin": "https://games.thejaynetwork.com"})

# QR Confirm flow
r = api.post(f"{SITE}/api.php?api=qr_create")
sid = r.json()["session_id"]
api.post(f"{SITE}/api.php?api=qr_confirm", json={"session_id": sid, "wallet": WALLET})
```

**⚠️ CRITICAL PITFALL: Wallet Address Derivation**
- Server validates with regex `/^yjay1[a-z0-9]{38}$/` (43 chars total)
- Must use `RIPEMD160(SHA256(compressed_pubkey))`, NOT raw pubkey
- Raw pubkey → 64-char address → **REJECTED by server**

## Claim Flow (v6 — PoW Challenge)

```python
# 1. Get claim nonce + PoW challenge
r = api.post(f"{SITE}/api.php?api=claim_nonce", json={"wallet": WALLET, "game_id": 155})
nonce_data = r.json()
# → {nonce, pow_challenge, difficulty}

# 2. Solve PoW (find hash with required prefix)
challenge = nonce_data["pow_challenge"]
difficulty = nonce_data["difficulty"]
pow_nonce = 0
while True:
    data = challenge + str(pow_nonce)
    h = hashlib.sha256(data.encode()).hexdigest()
    if h.startswith("0" * difficulty):
        break
    pow_nonce += 1

# 3. Submit claim
r = api.post(f"{SITE}/api.php?api=claim", json={
    "wallet": WALLET,
    "game_id": 155,
    "score": score,
    "session_token": session_token,
    "claim_nonce": nonce_data["nonce"],
    "pow_answer": str(pow_nonce)
})
```

## Cooldown Issue

**"cooldown active (layer 4)"** — CDN/proxy rate limit between score submissions.

| Delay | Result |
|-------|--------|
| 30-60s | ❌ Cooldown |
| 90-150s | ❌ Cooldown |
| 300s (5 min) | ✅ Works (sometimes) |
| 330s (5.5 min) | ✅ Reliable |

**Script v6 uses 330s (5.5 min) COOLDOWN_SECONDS.** On cooldown hit, retries in 60s.

## Cron Optimization (Updated 31 Mei 2026)

- **Timeout**: 5400s (90 min) — needed for 15 games × 5.5 min = ~82 min
- Old timeout 3600s (60 min) was too short, only completed ~10 games
- Morning run (08:00) handles all 15 games; afternoon run (15:00) is backup
- Expected: **3.75 JAY/day** (15 × 0.25, unverified)

## Key Code Patterns

### Read Puzzle from DOM
```javascript
const cells = document.querySelectorAll("#board .cell");
const puzzle = [];
cells.forEach(cell => {
    let val = 0;
    for (const child of cell.childNodes) {
        if (child.nodeType === 3 && child.textContent.trim()) {
            val = parseInt(child.textContent.trim()) || 0;
            break;
        }
    }
    puzzle.push(val);
});
```

### Fill Cell
```javascript
// Click cell first
document.querySelectorAll("#board .cell")[index].click();
// Then click number pad
document.querySelectorAll("#pad .num")[value - 1].click();
```

### Check Win State
```javascript
const won = document.getElementById("winOverlay").classList.contains("show");
const score = document.getElementById("winScore").textContent;
```

## Pitfalls

1. **IIFE Scope**: `state` variable is inside IIFE, NOT accessible via `page.evaluate`. Must solve puzzle independently in Python.

2. **Frame Detection**: Main page loads iframe lazily. Wait 10s before checking frames. Match `/games/jay-sudoku` not just `jay-sudoku`.

3. **Cooldown**: First game works immediately. Subsequent games need 330s (5.5 min) delay. Script v6 handles this automatically.

4. **Cell Selection**: Must click cell first, then click number pad. Order matters.

5. **Session Persistence**: Use `requests.Session()` to persist cookies across API calls. Cookie name: `jay_session`.

6. **Score Minimum**: Server requires score >= 500 (not 200 as old chess). Expert Sudoku always scores 3400+, so no issue.

7. **Play Token Expiry**: `playToken` expires in 3600s (1 hour). If solving takes too long (unlikely), token may expire.

8. **Wallet Address**: MUST be 43 chars (RIPEMD160), NOT 64 chars (raw pubkey). Server validates with regex.

9. **PoW Claim**: Claim requires solving SHA256 PoW challenge. Typical difficulty=4, takes <1 second.

10. **API Endpoint**: Always use `api.php?api=...`, NOT `/api/...`. The REST endpoints are dead (return HTML).

## Claim Flow (VERIFIED WORKING — 31 Mei 2026)

**Key facts:**
- `simulated: true` — tx is simulated but reward is real
- Pending must be >= 1.0 JAY to claim
- Claim resets pending to 0
- Unverified max: 15 claims/day × 0.25 JAY = 3.75 JAY/day
- Verified max: 15 claims/day × 5 JAY = 75 JAY/day
- Daily reset: midnight (timezone unknown, likely UTC or WIB)

## Score Formula

```python
base = 1000
time_penalty = min(600, time_seconds * 0.8)
mistake_penalty = mistakes * 120
hint_penalty = hints * 90
raw = base - time_penalty - mistake_penalty - hint_penalty
score = max(50, round(raw * difficulty_multiplier))
```

Difficulty multipliers: Easy=1.0, Medium=1.6, Hard=2.4, Expert=3.5
