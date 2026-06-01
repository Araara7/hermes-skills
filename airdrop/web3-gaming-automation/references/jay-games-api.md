# JAY Games API Documentation

Base URL: `https://games.thejaynetwork.com/`

## Authentication

All API calls require User-Agent header:
```bash
-H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
```

## Endpoints

### QR Code Connection

#### Create QR Session
```bash
curl -s "https://games.thejaynetwork.com/api.php?api=qr_create"
```

Response:
```json
{
  "session_id": "abc123...",
  "qr_data": "https://wallet.thejaynetwork.com/qr_connect.php?sid=abc123&app=games",
  "expires": 1779959573
}
```

#### Poll QR Status
```bash
curl -s "https://games.thejaynetwork.com/api.php?api=qr_poll&sid=SESSION_ID"
```

Response (waiting):
```json
{"status": "waiting"}
```

Response (connected):
```json
{"status": "connected", "wallet": "yjay..."}
```

Response (expired):
```json
{"status": "expired"}
```

### Wallet Statistics

#### Get Stats
```bash
curl -s "https://games.thejaynetwork.com/api.php?api=stats&wallet=WALLET_ADDRESS"
```

Response:
```json
{
  "claims": 0,
  "total_ujay": "0",
  "max_claims": 15,
  "max_ujay": "50000000",
  "x_verified": false
}
```

### Twitter Verification

#### Check Twitter Status
```bash
curl -s "https://games.thejaynetwork.com/api.php?api=x_check&wallet=WALLET_ADDRESS"
```

Response:
```json
{"verified": false, "x_handle": ""}
```

or when verified:
```json
{"verified": true, "x_handle": "username"}
```

#### Connect Twitter
```bash
curl -s "https://games.thejaynetwork.com/api.php?api=x_connect&wallet=WALLET_ADDRESS"
```

Response: OAuth redirect to Twitter

### Admin Check

```bash
curl -s "https://games.thejaynetwork.com/api.php?api=check_admin&wallet=WALLET_ADDRESS"
```

Response:
```json
{"admin": false}
```

### Claim Reward (UNVERIFIED - Missing Params)

```bash
curl -s -X POST \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Content-Type: application/json" \
  -H "Origin: https://games.thejaynetwork.com" \
  -d '{"wallet":"yjay...","game":"chess","score":100}' \
  "https://games.thejaynetwork.com/api.php?api=claim"
```

Response: `{"error":"Missing params"}`

**STATUS:** Endpoint exists but requires unknown parameters. Need further investigation.

### Traffic Logging

```bash
curl -s -X POST "https://control.thejaynetwork.com/api.php?act=traffic_log" \
  -H "Content-Type: application/json" \
  -d '{"service": "JAY Games"}'
```

## Game URLs

| Game | Preview URL | Game URL | ID |
|------|-------------|----------|-----|
| Tower Defense | `preview.php?f=tower-defense.html` | `game.php?id=151` | 151 |
| Crypto Racer | `preview.php?f=crypto-racer.html` | `game.php?id=152` | 152 |
| Runner | `preview.php?f=neon-runner.html` | `game.php?id=163` | 163 |
| Chess | `preview.php?f=chess.html` | `game.php?id=154` | 154 |
| JAY Sudoku | `preview.php?f=jay-sudoku.html` | - | - |
| JAY Squad | `preview.php?f=jay-squad.html` | - | - |
| 2048 | `preview.php?f=neon-2048.html` | - | - |
| Breaker | `preview.php?f=neon-breaker.html` | - | - |
| Flow Arena | `preview.php?f=flow_arena.html` | - | - |
| Othello Arena | `preview.php?f=othello_arena.html` | - | - |
| Stack | `preview.php?f=neon-stack.html` | - | - |
| Block | `preview.php?f=neon-block.html` | - | - |
| Cryptogram | `preview.php?f=cryptogram.html` | - | - |
| Janggi Arena | `preview.php?f=janggi_arena.html` | - | - |

## Wallet Types

JAY Games uses two wallet formats:
1. **EVM Address**: `0x...` (42 characters)
2. **JAY Wallet**: `yjay...` (44 characters, starts with "yjay")

The QR code connection returns a JAY Wallet address.

## Rate Limits

- API calls: No explicit rate limit observed
- QR sessions: Expire after ~10 minutes
- Twitter OAuth: Rate limited by Twitter (15-30 min cooldown)

## Bot Detection

The platform has bot detection:
- Requires valid User-Agent header
- May block requests without proper headers
- Use Camoufox for anti-detection
- protect.js blocks DevTools and right-click

## Game Architecture

### iframe Structure
- Main page: `https://games.thejaynetwork.com/`
- Game page: `game.php?id=XXX`
- Preview page: `preview.php?f=XXX.html`

### Score Submission
- Games send score via `window.parent.postMessage({score: score}, '*')`
- Games send game over via `window.parent.postMessage({gameOver: true, score: score}, '*')`
- Parent page does NOT have handler for gameOver messages
- Claim API exists but requires unknown parameters

### Wallet Connection
```javascript
// Set wallet via sessionStorage
sessionStorage.setItem('jay_games_wallet', 'yjay...');
location.reload();
```

## Known Issues

1. **Claim API Missing Params**: Endpoint exists but returns `{"error":"Missing params"}`
2. **Score Not Auto-Submitted**: Game score doesn't automatically become UJAY points
3. **QR Code May Fail**: QR generation can fail if wallet not connected
4. **Context Destroyed**: Canvas games may reload, destroying JavaScript context
