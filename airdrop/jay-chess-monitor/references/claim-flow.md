# JAY Games — Claim Flow (Detail)

## ⚠️ JANGAN gunakan raw curl untuk claim!

Claim butuh PoW (Proof of Work) challenge yang di-serve server secara dinamis.
Harus dilakukan via page's `claimReward()` JS function atau equivalent Playwright evaluate.

## Claim Flow (3 steps)

### Step 1: Get Nonce + PoW Challenge
```javascript
const nr = await fetch('api.php?api=claim_nonce', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({wallet, game_id: 77})
});
const nd = await nr.json();
// nd = {nonce: "...", pow_challenge: "...", difficulty: N}
```

### Step 2: Solve PoW
```javascript
async function solvePoW(challenge, difficulty) {
    const prefix = '0'.repeat(difficulty);
    let nonce = 0;
    while (true) {
        const data = challenge + nonce.toString();
        const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(data));
        const hex = Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
        if (hex.startsWith(prefix)) return nonce.toString();
        nonce++;
        if (nonce % 10000 === 0) await new Promise(r => setTimeout(r, 0)); // yield
    }
}
```

### Step 3: Submit Claim
```javascript
const r = await fetch('api.php?api=claim', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        wallet: "yjay19t8u26z70aeqvuj28y3jlnqznzh57vzcqc8tr9",
        game_id: 77,
        score: currentScore,        // must be >= 200
        session_token: sessionToken, // from api.php?api=session_token
        claim_nonce: nd.nonce,       // from step 1
        pow_answer: powAnswer        // from step 2
    })
});
const d = await r.json();
```

## Required Variables

| Variable | Source | Notes |
|----------|--------|-------|
| wallet | sessionStorage('jay_games_wallet') | Must set BEFORE page load |
| game_id | Hardcoded: 77 | |
| score | From chess game postMessage | Must be >= MIN_SCORE (200) |
| session_token | POST api.php?api=session_token | Auto-fetched by page on load |
| claim_nonce | From step 1 | One-time use |
| pow_answer | From step 2 | SHA-256 prefix mining |

## Prerequisites

1. **Wallet in sessionStorage**: `sessionStorage.setItem('jay_games_wallet', WALLET)`
   - Must be set BEFORE page loads (via `context.add_init_script`)
2. **sessionToken**: Fetched by page IIFE on load. If missing, fetch manually:
   ```javascript
   const r = await fetch('api.php?api=session_token', {
       method: 'POST', headers: {'Content-Type': 'application/json'},
       body: JSON.stringify({game_id: 77})
   });
   const d = await r.json();
   sessionToken = d.token;
   ```
3. **Score >= 200**: Via chess game captures
4. **Claim button enabled**: Auto-enabled when score >= 200 via postMessage listener

## Response Formats

### Success
```json
{
    "success": true,
    "txhash": "63018D3A...",
    "reward": "250000",      // ujay earned (unverified = 250000 = 0.25 JAY)
    "full_reward": "5000000", // full reward if X verified
    "x_verified": false,
    "error": ""
}
```

### Errors
```json
{"error": "Play longer before claiming"}     // RETRYABLE — play more moves first
{"error": "Transaction failed"}              // RETRYABLE — server-side tx issue
{"error": "Unexpected token '<'..."}         // Server returned HTML — RETRYABLE
{"error": "Score too low!"}                  // Score < 200
{"error": "Connect wallet first!"}           // No wallet in sessionStorage
{"error": "Session error, refresh page"}     // No sessionToken
{"error": "bot blocked"}                     // Anti-bot detection (stats API)
```

## Reward Calculation

- **X Verified**: 5 JAY (5,000,000 ujay)
- **X Not Verified**: 0.25 JAY (250,000 ujay) = 5,000,000 / 20

To get full reward, user must verify X/Twitter via `connectX()` flow.

## Error Recovery

| Error | Action |
|-------|--------|
| "Play longer" | Continue playing, retry after more moves (don't count as claim fail) |
| "Transaction failed" | **RETRIABLE** — wait 3s, retry (don't count as claim fail). Proven pattern: attempts 1-3 fail, attempt 4+ succeeds |
| HTML response ("Unexpected token") | **RETRIABLE** — server returned HTML, wait 3s, retry (don't count as claim fail) |
| "bot blocked" | Anti-bot detected, may need fresh browser context |
| Score too low | Continue playing until score >= 200 |

**Max claim attempts**: 5 (increased from 3 to accommodate retriable errors)
**Delay between retries**: 3 seconds

**⚠️ PENTING**: Jangan stop terlalu awal! Claim sering gagal di attempt 1-3 tapi sukses di attempt 4-5. Ini normal behavior server JAY Games.
