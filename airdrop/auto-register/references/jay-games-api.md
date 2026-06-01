# JAY Games API Reference

Platform: https://games.thejaynetwork.com/
Type: Web3 Gaming Platform (Play & Earn)
Token: JAY (UJAY)

## API Endpoints

### QR Code Wallet Connection

**Create QR Session:**
```bash
curl -s -H "User-Agent: Mozilla/5.0" "https://games.thejaynetwork.com/api.php?api=qr_create"
```
Response:
```json
{
  "session_id": "abc123...",
  "qr_data": "https://wallet.thejaynetwork.com/qr_connect.php?sid=abc123&app=games",
  "expires": 1779959573
}
```

**Poll QR Status:**
```bash
curl -s -H "User-Agent: Mozilla/5.0" "https://games.thejaynetwork.com/api.php?api=qr_poll&sid=SESSION_ID"
```
Response (waiting):
```json
{"status": "waiting"}
```
Response (connected):
```json
{"status": "connected", "wallet": "yjay..."}
```

### Wallet Statistics

**Get Stats:**
```bash
curl -s -H "User-Agent: Mozilla/5.0" "https://games.thejaynetwork.com/api.php?api=stats&wallet=WALLET_ADDRESS"
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

### Admin Check

```bash
curl -s -H "User-Agent: Mozilla/5.0" "https://games.thejaynetwork.com/api.php?api=check_admin&wallet=WALLET_ADDRESS"
```
Response:
```json
{"admin": false}
```

### Twitter/X Verification

**Check Status:**
```bash
curl -s -H "User-Agent: Mozilla/5.0" "https://games.thejaynetwork.com/api.php?api=x_check&wallet=WALLET_ADDRESS"
```
Response:
```json
{"verified": false, "x_handle": ""}
```

**Initiate Connection:**
```bash
curl -s -H "User-Agent: Mozilla/5.0" "https://games.thejaynetwork.com/api.php?api=x_connect&wallet=WALLET_ADDRESS"
```
This opens Twitter OAuth page for authorization.

## Key Learnings

1. **User-Agent Required** - All API calls need proper User-Agent header
2. **Wallet Format** - JAY Games uses `yjay...` format, NOT EVM `0x...` addresses
3. **Session Storage** - Wallet stored in `sessionStorage` key `jay_games_wallet`
4. **Rate Limits** - Twitter OAuth can rate-limit login attempts
5. **Games** - 14 games available, each gives 5 JAY token reward
6. **Daily Limits** - Max 15 claims, max 50,000,000 UJAY per day

## JavaScript Integration

From browser context:
```javascript
// Create QR session
const qr = await fetch('api.php?api=qr_create').then(r => r.json());

// Poll for connection
const status = await fetch(`api.php?api=qr_poll&sid=${qr.session_id}`).then(r => r.json());

// Get stats
const stats = await fetch(`api.php?api=stats&wallet=${wallet}`).then(r => r.json());

// Check Twitter verification
const xStatus = await fetch(`api.php?api=x_check&wallet=${wallet}`).then(r => r.json());
```
