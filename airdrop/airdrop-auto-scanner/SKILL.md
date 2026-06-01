---
name: airdrop-auto-scanner
description: "Auto-scan new airdrop opportunities — cek crypto news, Twitter, eligibility check. Filter yang worth dikerjakan berdasarkan potensi reward."
tags: [airdrop, scanner, discovery, automation, research]
---

# Airdrop Auto Scanner

## When to Use
- Daily scan untuk airdrop baru
- User minta cari project baru
- Evaluate apakah project worth dikejar

## Scan Sources

### 1. Crypto Airdrop Aggregators
```bash
# Check airdrop listing sites
curl -s "https://airdrops.io/latest/" | grep -oE 'href="[^"]*airdrop[^"]*"' | head -20
```

### 2. Twitter/X Search
```bash
# Search for new airdrop announcements
# Use xurl skill: xurl search "airdrop now live" --limit 20
```

### 3. Galxe Quest Platform (API)
```python
import requests

GALXE_API = "https://graphigo.prd.galaxy.eco/query"
HEADERS = {"Content-Type": "application/json", "Origin": "https://app.galxe.com"}

# Get active campaigns
resp = requests.post(GALXE_API, json={
    "query": 'query { campaigns(input: {first: 20, status: Active}) { list { id name space { name } credentialGroups { credentials { id name type } } } } }'
}, headers=HEADERS).json()

# Get trending campaigns
resp = requests.post(GALXE_API, json={
    "query": 'query { campaigns(input: {first: 10, listType: Trending}) { list { id name status space { name } } } }'
}, headers=HEADERS).json()

# Query specific space
resp = requests.post(GALXE_API, json={
    "query": 'query { project(name: "spacename") { id name campaigns(input: {first: 5, status: Active}) { list { id name } } } }'
}, headers=HEADERS).json()
```

**Auto-completable task types:** Twitter (follow, like, retweet, quote), Telegram join
**Manual-only:** Discord (requires server join), on-chain (requires wallet tx), quiz/form

**Categorize tasks by type:**
```python
for cred in campaign["credentialGroups"][0]["credentials"]:
    if "TWITTER" in cred["type"]: → auto-completable
    elif "DISCORD" in cred["type"]: → manual
    elif "BALANCE" in cred["type"] or "SWAP" in cred["type"]: → on-chain
```

Script: `~/airdrop-agent/scripts/galxe_scanner.py`

### 4. DeFiLlama / Data Sources
```bash
# Check new protocols
curl -s "https://api.llama.fi/protocols" | python3 -c "
import sys,json
data = json.load(sys.stdin)
new = [p for p in data if p.get('listedAt',0) > $(date -d '7 days ago' +%s)]
for p in new[:10]:
    print(f\"{p['name']} | {p['chain']} | {p['category']}\")
"
```

## Evaluation Criteria

### Score Each Project (1-10)
| Factor | Weight | Scoring |
|--------|--------|---------|
| Team credibility | 20% | Known team = 8-10, anon = 3-5 |
| Funding raised | 20% | >$10M = 8-10, <$1M = 3-5 |
| Token confirmed | 15% | Confirmed = 10, rumored = 5 |
| Task complexity | 15% | Simple = 10, complex = 3 |
| Time required | 15% | <1hr = 10, >10hr = 3 |
| Historical payouts | 15% | Past airdrops = 10, first time = 5 |

### Minimum Score to Pursue: 6/10

## Task Types & Time Estimates

| Task Type | Time | Automation? |
|-----------|------|-------------|
| Wallet connect | 2 min | ✅ Full |
| Social follow/retweet | 5 min | ⚠️ Partial (rate limits) |
| Testnet swap | 10 min | ✅ Full |
| Bridge tokens | 15 min | ✅ Full |
| Run node | Ongoing | ✅ Full |
| Discord join | 5 min | ⚠️ Partial |
| Quiz/form | 10 min | ❌ Manual |
| KYC | 30 min | ❌ Manual |

## Output: New Project Card
```
🆕 NEW AIRDROP: [Project Name]
🔗 URL: https://...
⛓️ Chain: [chain]
💰 Potential: [high/medium/low]
📋 Tasks: [list]
⏱️ Est. Time: [hours]
🎯 Score: [X/10]
🤖 Auto: [yes/partial/no]

Recommendation: [PURSUE / SKIP / MONITOR]
```

## Related Skills
- `airdrop-api-discovery` — discover APIs for new project
- `airdrop-wallet-connect` — connect wallet
- `airdrop-project-tracker` — add to tracker
- `web3-airdrop-automation` — full automation
