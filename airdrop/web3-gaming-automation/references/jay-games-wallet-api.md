# JAY Games API & Wallet Connection (Mei 2026)

## API Endpoints (Next.js Site)

Site migrated from PHP to Next.js. New API endpoints:

```
GET  /api/wallet/nonce?address=WALLET  → {nonce, message, chainId}
POST /api/wallet/connect               → {address, nonce, signature} → session
GET  /api/wallet/session                → {connected, address, verified, pending}
POST /api/score/submit                 → submit game score
POST /api/claim                        → claim reward
GET  /api/rewards/pending              → check pending rewards (needs session)
```

## Wallet Connection Flow

### Step 1: Get Nonce
```bash
curl -s "https://games.thejaynetwork.com/api/wallet/nonce?address=yjay19t8u26z70aeqvuj28y3jlnqznzh57vzcqc8tr9"
```
Response:
```json
{
  "ok": true,
  "data": {
    "nonce": "e2a539647e30cda366123b552f91b3ad",
    "message": "Sign in to JAY Games on thejaynetwork\nAddress: yjay...\nNonce: e2a...",
    "chainId": "thejaynetwork"
  }
}
```

### Step 2: Sign Message
Sign the `message` field with wallet's private key (Cosmos SDK secp256k1 signing).

### Step 3: Connect
```bash
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"address":"yjay...","nonce":"e2a...","signature":"sig..."}' \
  "https://games.thejaynetwork.com/api/wallet/connect"
```

### Step 4: Check Session
```bash
curl -s "https://games.thejaynetwork.com/api/wallet/session"
```
Response:
```json
{
  "ok": true,
  "data": {
    "connected": true,
    "address": "yjay...",
    "verified": false,
    "pending": 0
  }
}
```

## Blocking Issue

Need private key for JAY wallet `yjay19t8u26z70aeqvuj28y3jlnqznzh57vzcqc8tr9` to sign message.

- Unicity seed phrase doesn't derive to this wallet
- Need correct seed phrase or private key from user
- Manual connect via browser (Keplr extension or JAY Wallet mobile QR) works as fallback

## Wallet Connection Options

1. **Keplr Extension** (browser) - requires Keplr installed
2. **JAY Wallet** (mobile) - scan QR code
3. **API** - requires private key for signing

## Twitter Verification

- Unverified: 0.05× reward
- Verified: up to 250 JAY/day
- Verify button on main page (disabled if no wallet connected)
- OAuth flow to X/Twitter

## Old PHP API (DEPRECATED - 404)

All old endpoints return 404:
- `api.php?api=stats` → 404
- `api.php?api=claim` → 404
- `api.php?api=x_check` → 404
- `api.php?api=x_connect` → 404
- `api.php?api=qr_create` → 404
