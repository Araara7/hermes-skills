# Flashbots Protect — Private TX Reference

## Endpoints

| Chain | RPC | Notes |
|-------|-----|-------|
| Ethereum | `https://rpc.mevblocker.io` | MEV Blocker, free tier |
| Ethereum | `https://protect.flashbots.net` | Flashbots direct |
| Arbitrum | `https://rpc.flashbots.net/arbitrum` | Flashbots relay |
| Optimism | `https://rpc.flashbots.net/optimism` | Flashbots relay |
| Base | `https://rpc.flashbots.net/base` | Flashbots relay |
| Polygon | `https://rpc.flashbots.net/polygon` | Flashbots relay |
| BSC | `https://bsc.meowrpc.com` | MEV Protect (no Flashbots on BSC) |

## How It Works

```
Normal TX:  Wallet → Public Mempool → Miner → Block
            (attacker can see, front-run, sandwich)

Protected:  Wallet → Flashbots Relay → Block Builder → Block
            (private, invisible until included)
```

## Usage Pattern

Same as normal Web3, just swap the RPC:

```python
from web3 import Web3

# Normal (public)
w3 = Web3(Web3.HTTPProvider("https://eth.llamarpc.com"))

# Protected (private)
w3 = Web3(Web3.HTTPProvider("https://rpc.mevblocker.io"))

# Build & sign TX exactly the same way
tx = {...}
signed = w3.eth.account.sign_transaction(tx, private_key)
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
```

## Compromised Wallet Claim Workflow

1. Check eligibility (earni.fi, airdrops.io)
2. Build claim TX calldata
3. Send via Flashbots Protect RPC
4. Wait for confirmation
5. Transfer claimed tokens to new wallet (also via Flashbots)

**Race condition:** Attacker has same key. Speed matters. Use Flashbots to stay invisible.

**CRITICAL:** Do NOT deposit gas without immediately claiming! Attacker runs auto-sweeper — any gas deposited will be swept within seconds. Deposit + claim must happen in rapid succession.

## Scripts

- `scripts/flashbots_protect.py` — reusable TX sender with private RPC
- `scripts/airdrop_protect.py` — full claim workflow orchestrator

## Verified Working

- ✅ MEV Blocker (Ethereum): block 25225194
- ✅ Flashbots Arbitrum: block 25225195
- ✅ Flashbots Optimism: block 25225195
- ✅ Flashbots Base: block 25225195
- ✅ Flashbots Polygon: block 25225195
- ✅ BSC MEV Protect: block 101761140

## BscScan API V2 Migration

BscScan V1 deprecated (2025). V2 requires paid plan for BSC.

```python
# ❌ Old (deprecated)
"https://api.bscscan.com/api?module=account&action=tokentx&address=..."

# ✅ Alternatives
"https://bsc.blockscout.com/api?module=account&action=tokenlist&address=..."
# Or direct RPC: w3.eth.get_balance() + known token contracts
```
