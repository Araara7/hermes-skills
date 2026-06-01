# JAY Games API Quick Reference

Base URL: `https://games.thejaynetwork.com/`

## Quick Commands

### Check Points
```bash
curl -s -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  "https://games.thejaynetwork.com/api.php?api=stats&wallet=yjay19t8u26z70aeqvuj28y3jlnqznzh57vzcqc8tr9"
```
Response: `{"claims":N,"total_ujay":"X","max_claims":15,"max_ujay":"50000000","x_verified":bool}`

### Check Twitter Verification
```bash
curl -s -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  "https://games.thejaynetwork.com/api.php?api=x_check&wallet=yjay19t8u26z70aeqvuj28y3jlnqznzh57vzcqc8tr9"
```
Response: `{"verified":false,"x_handle":""}` atau `{"error":"bot blocked"}` (dari headless)

**⚠️ Twitter/X Verification Status (2026-05-30):**
- `x_connect` endpoint returns `{"error":"X not configured"}` — OAuth broken server-side
- `x_check` blocks headless browser (`bot blocked`) — use curl only
- Manual verify: user buka site → profile → Verify button
- Tanpa verify: 0.25 JAY/claim (÷20 dari full 5 JAY)

### Get Session Token (for claim)
```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"game_id":77}' \
  "https://games.thejaynetwork.com/api.php?api=session_token"
```
Response: `{"token":"Nzd8..."}`

### Get Claim Nonce + PoW Challenge
```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"wallet":"yjay19t8u26z70aeqvuj28y3jlnqznzh57vzcqc8tr9","game_id":77}' \
  "https://games.thejaynetwork.com/api.php?api=claim_nonce"
```
Response: `{"nonce":"...","pow_challenge":"...","difficulty":N}`

### Claim Reward
⚠️ **JANGAN gunakan raw curl!** Butuh PoW solve + nonce + session_token.
Lihat `references/claim-flow.md` untuk detail.

## Wallet Info
- JAY Wallet: `yjay19t8u26z70aeqvuj28y3jlnqznzh57vzcqc8tr9`
- EVM Address: `0x000C0e48DC08987954631249Cffba71B5EfaD263`

## Game URLs (UPDATED)
- Chess: `https://games.thejaynetwork.com/game.php?id=77`
- All games: `https://games.thejaynetwork.com/chess` (game listing page)
- Game iframe: `https://games.thejaynetwork.com/g/chess.html`

## Points System
- Unverified: 0.25 JAY per claim (reward / 20)
- Verified: 5 JAY per claim (⚠️ Twitter OAuth broken — server returns "X not configured")
- Max claims: 15/day
- Max UJAY: 50,000,000
- MIN_SCORE to claim: 200
- "Play longer before claiming" = server requires more gameplay before allowing claim
- Claim pattern: sering gagal attempt 1-3, sukses di attempt 4-5 (retriable errors)
