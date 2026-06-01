# JAY Games Setup & Status

## Account Info

| Item | Value |
|------|-------|
| JAY Wallet | `yjay19t8u26z70aeqvuj28y3jlnqznzh57vzcqc8tr9` |
| EVM Address | `0x000C0e48DC08987954631249Cffba71B5EfaD263` |
| Twitter | @otama777A (not verified) |
| Site URL | https://games.thejaynetwork.com/ |

## API Commands (Tested Working)

```bash
UA="User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
WALLET="yjay19t8u26z70aeqvuj28y3jlnqznzh57vzcqc8tr9"
BASE="https://games.thejaynetwork.com"

# Stats
curl -s -H "$UA" "$BASE/api.php?api=stats&wallet=$WALLET"

# Twitter check
curl -s -H "$UA" "$BASE/api.php?api=x_check&wallet=$WALLET"

# Admin check
curl -s -H "$UA" "$BASE/api.php?api=check_admin&wallet=$WALLET"

# Create QR session
curl -s -H "$UA" "$BASE/api.php?api=qr_create"

# Poll QR
curl -s -H "$UA" "$BASE/api.php?api=qr_poll&sid=SESSION_ID"
```

## Current Stats (2026-05-28)

```json
{"claims":0,"total_ujay":"0","max_claims":15,"max_ujay":"50000000","x_verified":false}
```

- Claims: 0/15
- UJAY: 0/50,000,000
- Twitter: NOT verified (rate limited)

## Game URLs

| Game | URL |
|------|-----|
| Chess | `preview.php?f=chess.html` |
| Tower Defense | `preview.php?f=tower-defense.html` |
| Crypto Racer | `preview.php?f=crypto-racer.html` |
| Neon Runner | `preview.php?f=neon-runner.html` |

## Cron Jobs

| Job | Schedule | Purpose |
|-----|----------|---------|
| jay-chess-monitor (ce5fee11a94b) | 6h | Play chess, farm UJAY |

## Pitfalls

1. **Browser timeout**: Site blocks datacenter IPs at WAF level. API still works via curl.
2. **Twitter rate limit**: OAuth flow rate limited. Wait 15-30 min between attempts.
3. **Canvas games**: Use Playwright `page.mouse.click()` on canvas coords, NOT `browser_console` JS injection (state resets between calls).
4. **Wallet format**: JAY wallet is `yjay...` format, NOT EVM `0x...`.
5. **Claim API**: Exists at `api.php?api=claim` but requires HMAC-signed params from server. Cannot claim via curl directly.
6. **Game over**: Chess ends when king captured. Avoid moving king early in game.

## Working Scripts

| Script | Path | Status |
|--------|------|--------|
| chess_playwright_v2.py | `~/airdrop-agent/scripts/chess_playwright_v2.py` | ✅ Works, plays 16+ moves |
| chess_playwright.py | `~/airdrop-agent/scripts/chess_playwright.py` | ⚠️ Crashes on context error |

## Reward Structure

- Each game: **5 JAY** reward
- Unverified: **1/20** reward (0.25 JAY per game)
- Verified: up to **250 JAY/day**
- Daily claims limit: **15 plays**
- Total games available: **14 games**

## Connectivity Test

```bash
# Test if site accessible
curl -I --max-time 10 https://games.thejaynetwork.com

# If timeout, API may still work
curl -s -H "$UA" "$BASE/api.php?api=stats&wallet=$WALLET"
```
