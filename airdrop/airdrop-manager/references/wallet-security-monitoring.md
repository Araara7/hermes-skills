# Wallet Security Monitoring Guide

## Quick Check Commands

### Gnosis Chain
```bash
# Recent transactions
curl -s "https://gnosis.blockscout.com/api/v2/addresses/<WALLET>/transactions?sort=desc&limit=10"

# Token transfers
curl -s "https://gnosis.blockscout.com/api/v2/addresses/<WALLET>/token-transfers?sort=desc&limit=10"
```

### Ethereum Mainnet
```bash
curl -s "https://eth.blockscout.com/api/v2/addresses/<WALLET>/transactions?sort=desc&limit=10"
```

### Arbitrum
```bash
curl -s "https://arbitrum.blockscout.com/api/v2/addresses/<WALLET>/transactions?sort=desc&limit=10"
```

### Multi-Chain Check Script
```bash
for chain in "eth" "gnosis" "arbitrum" "optimism" "base" "polygon"; do
    result=$(curl -s "https://${chain}.blockscout.com/api/v2/addresses/<WALLET>/transactions?sort=desc&limit=3")
    count=$(echo "$result" | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d.get('items',[])))" 2>/dev/null)
    if [ "$count" != "0" ] && [ -n "$count" ]; then
        echo "$chain: $count recent txs"
    fi
done
```

## Wallet Addresses

| Wallet | Address | Chain | Status |
|--------|---------|-------|--------|
| Main EVM | `0x000C0e...D263` | Multi | ✅ Active |
| Galxe (OLD) | `0xb01E...de3E` | Multi | ❌ COMPROMISED — DO NOT USE |
| Galxe (NEW) | `0x044C7f...46bf` | Multi | ✅ Active (needs encrypted key storage) |
| Cosmos | `yjay1aervd...vnf6` | Cosmos | ✅ Active (JAY mining) |
| Solana | `D98Jh6rr...iPKP` | Solana | ✅ Active |
| Recovery | `0xA82E5b...7a6C0` | Multi | ✅ Active (user's recovery wallet) |

## Incident Log

| Date | Wallet | Chain | Amount | Recipient | Status |
|------|--------|-------|--------|-----------|--------|
| 2026-06-01 | 0xb01E...de3E | Gnosis | 1.894687 xDAI | 0x6850Bd3F...3a8a | ⚠️ Unauthorized drain |
| 2026-06-01 | 0xb01E...de3E | Base | ~0.0009 ETH | 0xf111...8008 | ⚠️ Auto-swept after Hanafuda withdraw |

**Root cause:** Private key stored in plain text in multiple script files on VPS (pixie_login*.py, wallet_unicity.json, config/credentials/.env). Attacker gained access to key, deployed auto-sweeper on Base, drained Gnosis directly. Hanafuda bot withdraw was triggered BY the attacker (not by us) — they called `withdraw` to move ETH out of Hanafuda, then swept it within 18 seconds.

**Attacker profile:** Professional drainer operation. Primary aggregator `0xf111...8008` holds ~$7,400 from 16+ victims. Uses EIP-7702 proxy infrastructure. Not yet flagged on any scam database.

**New wallet:** `0x044C7f09D871d9289f57db395Ae4963453E746bf` — generated on VPS, seed in `/tmp/new_wallet.txt` (needs proper encrypted storage).

## Response Protocol

1. **Detect** — Monitor blockscout API for new transactions
2. **Verify** — Check if TX came from our scripts
3. **Investigate** — If not from us: check processes, cron, SSH logs
4. **Act** — Move funds to new wallet if compromised
5. **Report** — Notify user immediately

## 🔍 Blockchain Investigation Workflow

When unauthorized TX detected, follow this investigation pattern:

### Step 1: Identify All Outflows
```bash
# Check recent transactions on each chain
curl -s "https://base.blockscout.com/api/v2/addresses/<WALLET>/transactions" | \
  python3 -c "
import sys, json
d = json.load(sys.stdin)
my = '<wallet>'.lower()
for tx in d.get('items', [])[:20]:
    fr = tx.get('from',{}).get('hash','').lower()
    to_addr = tx.get('to',{}).get('hash','?') if tx.get('to') else 'contract'
    val = int(tx.get('value','0'))/1e18
    ts = tx.get('timestamp','?')[:19]
    direction = 'IN' if fr != my else 'OUT'
    method = tx.get('method','transfer')
    print(f'{direction} | {val:.8f} ETH | {ts} | {method} | → {to_addr[:25]}...')
"
```

### Step 2: Build Timeline
- Sort all TXs by timestamp across chains
- Look for pattern: simultaneous drain on multiple chains = attacker has private key
- Flag `withdraw` method calls that you didn't initiate = attacker triggering your bot withdrawals

### Step 3: Profile Attacker Addresses
```bash
# Check attacker balance and activity
curl -s "https://base.blockscout.com/api/v2/addresses/<ATTACKER>" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Balance: {int(d.get(\"coin_balance\",\"0\"))/1e18:.4f} ETH'); print(f'Type: {\"EOA\" if not d.get(\"is_contract\") else \"Contract\"}'); print(f'Scam: {d.get(\"is_scam\")}'); print(f'Tags: {d.get(\"metadata\",{}).get(\"tags\",[])}')"

# Check attacker's incoming funds (how many victims?)
curl -s "https://base.blockscout.com/api/v2/addresses/<ATTACKER>/transactions" | \
  python3 -c "
import sys, json
d = json.load(sys.stdin)
senders = set()
for tx in d.get('items', []):
    fr = tx.get('from',{}).get('hash','')
    if fr.lower() != '<attacker>'.lower():
        senders.add(fr[:15])
print(f'Unique senders: {len(senders)} — likely {len(senders)} victims')
"
```

### Step 4: Check EIP-7702 Proxy Pattern
Attacker may use EIP-7702 smart wallet proxies sharing same implementation:
```bash
# Look for proxy implementation address in TX details
curl -s "https://base.blockscout.com/api/v2/transactions/<TX_HASH>" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d.get('tx_types',[]), indent=2))"
```
If multiple attacker addresses share the same EIP-7702 implementation → coordinated operation, single entity.

### Step 5: Determine Compromise Source
| Indicator | Meaning |
|-----------|---------|
| TX `method: withdraw` from your wallet you didn't call | Attacker has private key, triggered your bot's withdraw |
| Multiple chains drained simultaneously | Private key compromised (not just one chain approval) |
| Auto-sweeper pattern (< 2s after deposit) | Attacker running bot to maximize theft |
| Attacker received from 10+ addresses | Professional drainer operation, not targeted attack |
| Funds still at attacker address (not moved) | Attacker waiting to consolidate before moving to mixer |

### Step 6: Check VPS for Leak Source
```bash
# Find plaintext keys
grep -rn "private_key\|priv_key\|seed\|mnemonic\|0x[0-9a-f]\{64\}" ~/airdrop-agent/ --include="*.py" --include="*.json" --include="*.sh" --include="*.env" 2>/dev/null

# Check SSH access logs
last -20
journalctl -u sshd --since "7 days ago" | grep "Accepted"

# Check for unknown processes
ps aux | grep -E "python|node|curl" | grep -v grep

# Check cron for unknown entries
crontab -l
```

## Auto-Sweeper Detection Pattern

When investigating compromised wallets, look for this pattern:
1. **Rapid OUT transactions** (within seconds of each other) = bot sweeping
2. **`withdraw` method calls you didn't initiate** = attacker triggering bot withdrawals
3. **ETH "numpang lewat"** — deposit arrives and is swept within 1-2 seconds
4. **Multiple destination addresses** — attacker splits to avoid single-point detection

**Timeline example (1 Jun 2026, actual attack):**
```
12:49:01 → 0.00001095 ETH → 0x6850... (attacker dust)
12:49:49 → 0.00002967 ETH → 0xe91a... (attacker)
12:51:59 → token transfer  → 0x825A...
12:52:41 → withdraw        → Hanafuda (attacker triggered!)
12:52:59 → 0.00050024 ETH → 0xf111... (sweep! 18 sec after withdraw)
12:53:19 → 0.00039829 ETH → 0xf111... (sweep again)
```

## Post-Compromise Recovery Checklist

1. ✅ Generate new wallet (not on compromised VPS if possible)
2. ✅ Stop all bots using compromised wallet
3. ✅ Check for remaining ERC-20 tokens (spam vs real — most are phishing)
4. ✅ Check for NFTs with value (Sablier vesting, POAPs, etc.)
5. ✅ Check vesting contracts (Sablier, Hedgey, etc.)
6. ✅ Update all configs to new wallet
7. ✅ Set up .env + config_loader.py (never hardcode again)
8. ✅ Auto-sweep protection for new wallet
9. ✅ Report all findings to user

## Multi-Chain Token Scan

Scan all chains for remaining tokens in compromised wallet:
```bash
for chain in base gnosis optimism arbitrum; do
  echo "=== $chain ==="
  curl -s "https://${chain}.blockscout.com/api/v2/addresses/<WALLET>/tokens?type=ERC-20" | \
    python3 -c "
import sys, json
d = json.load(sys.stdin)
for t in d.get('items', [])[:20]:
    name = t.get('token',{}).get('name','?')
    symbol = t.get('token',{}).get('symbol','?')
    value = t.get('value','0')
    print(f'  {symbol} ({name}): {value}')
" 2>/dev/null
done
```

**Common findings in compromised wallets:**
- 99% of remaining tokens are spam/phishing (names contain scam URLs)
- Real tokens: check DexScreener for liquidity
- NFTs: Sablier lockups may contain vesting tokens worth claiming
- Basenames/ENS: transferable but low monetary value

## Attacker Investigation Results (1 Jun 2026)

### Primary Sweeper: `0xf111122404b8C2FC01dfF89C65D3104fbb608008`
- Balance: ~3.765 ETH (~$7,434)
- Type: EOA, no labels, not flagged
- First seen: 31 May 2026
- Received from 16+ addresses → professional drainer aggregator
- Uses EIP-7702 proxy infrastructure
- Holds scam/phishing airdrop tokens (Unicode "ETH" lookalikes)

### Dust Address: `0x6850Bd3F5AB9A8c720e1024Ba7459e2848dC3a8a`
- Gnosis: 1.8947 xDAI (still sitting, not moved)
- Role: secondary dust address, same entity as primary sweeper

### Attack Pattern
```
Multiple victims → 0xf111...8008 (aggregator, $7400+)
Our wallet → 0x6850...3a8a (Gnosis dust)
           → 0xf111...8008 (Base sweep, auto-sweeper <2s)
```
