---
name: airdrop-api-discovery
description: "Auto-discover API endpoints from any airdrop/gaming site — network interception, JS analysis, curl probing. API-first approach, minimize browser."
tags: [airdrop, api, discovery, automation, reverse-engineering]
---

# Airdrop API Discovery

## When to Use
- New airdrop project found — need to find API endpoints
- Script broken — API changed, need to re-discover
- Want to automate a new site — first step is API discovery

## Golden Rule
**ALWAYS try API first before opening browser.** Browser = last resort.

## Discovery Methods (Priority Order)

### 1. Network Interception (Browser — Quick)
```bash
# Open site in browser, capture network requests
# Look for: api.php, /api/, graphql, fetch/XHR calls
# Extract: endpoints, headers, auth tokens
```

### 2. JS Source Analysis
```bash
# Find API endpoints in JavaScript
curl -s "https://site.com/" | grep -oE '(https?://[^"]+api[^"]*|/api/[^"]*|api\.php\?[^"]*)' | sort -u

# Check bundled JS files
curl -s "https://site.com/_next/static/chunks/main.js" | grep -oE '/api/[a-z/]+' | sort -u
```

### 3. Curl Probing (No Browser)
```bash
# Common API patterns to test
for pattern in "/api/stats" "/api/wallet" "/api/claim" "/api.php?api=stats" "/api/user" "/graphql"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -H "User-Agent: Mozilla/5.0" "https://site.com$pattern")
  echo "$pattern → HTTP $code"
done
```

### 4. Parameter Discovery
```bash
# Find query parameters
curl -s "https://site.com/" | grep -oE 'api\.php\?[a-z_]+=[^"&]+' | sort -u

# Test each parameter
curl -s -H "User-Agent: Mozilla/5.0" "https://site.com/api.php?api=PARAM&wallet=WALLET"
```

## Common API Patterns

### Gaming Sites
```
/api/wallet/nonce?address=WALLET   → wallet auth nonce
/api/wallet/connect                 → POST, wallet signature
/api/play/start                     → POST, get play token
/api/score/submit                   → POST, submit score
/api/claim                          → POST, claim reward
/api/rewards/pending                → GET, check pending
/api/stats?wallet=WALLET            → GET, user stats
```

### PHP-based Sites
```
api.php?api=stats&wallet=WALLET
api.php?api=claim&wallet=WALLET
api.php?api=nonce&wallet=WALLET
api.php?api=session_token&game_id=ID
```

### Next.js Sites
```
/api/auth/session          → current session
/api/user/profile          → user data
/api/rewards/claim         → claim endpoint
/_next/data/               → SSR data endpoints
```

## Headers Required (Almost Always)
```bash
-H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
-H "Origin: https://site.com"
-H "Referer: https://site.com/"
-H "Content-Type: application/json"
```

## Pitfalls
- ⚠️ Some sites return 403 without proper User-Agent
- ⚠️ `api.php` endpoints often still work even when site migrated to `/api/`
- ⚠️ CDN rate limits ("cooldown active layer 4") — need delays between requests
- ⚠️ Session cookies required for authenticated endpoints

## Output Template
After discovery, save to `~/airdrop-agent/data/projects/<project>/api_endpoints.md`:
```markdown
# <Project> API Endpoints
- Base URL: https://site.com
- Auth: wallet connect via QR/nonce
- Endpoints:
  - GET /api/stats → user stats
  - POST /api/claim → claim rewards
  - etc.
```

## Related Skills
- `auto-get-token` — extract auth tokens from browser
- `background-browser-workflow` — minimize browser usage
- `web3-gaming-automation` — full gaming automation
