# Flashbots Protect & Compromised Wallet Recovery

## Protected RPC Endpoints
```python
PROTECTED_RPCS = {
    "ethereum": "https://rpc.mevblocker.io",
    "arbitrum": "https://rpc.flashbots.net/arbitrum",
    "optimism": "https://rpc.flashbots.net/optimism",
    "base": "https://rpc.flashbots.net/base",
    "polygon": "https://rpc.flashbots.net/polygon",
    "bsc": "https://bsc.meowrpc.com",
}
```

## How It Works
```
NORMAL:  Kamu → Mempool (public) → Attacker lihat → Front-run → Block ❌
PROTECT: Kamu → Private Relay → Block Builder → Block ✅
```

## Compromised Wallet Recovery Workflow

### 1. Scan All Chains
```python
# Check native balance on all chains
for chain_name, rpc in CHAINS:
    w3 = Web3(Web3.HTTPProvider(rpc))
    bal = w3.eth.get_balance(old_wallet)

# Check ERC-20 via Blockscout
for chain_name, blockscout_url in BLOCKSCOUT_URLS:
    tokens = discover_tokens(old_wallet, chain_name, blockscout_url)
```

### 2. Check Airdrop Eligibility
- Wallet with on-chain history is likely eligible for airdrops
- Check: earni.fi, airdrops.io, official claim pages
- Monitor for new airdrops via cron

### 3. Claim & Transfer Strategy
1. **Deposit gas** via Flashbots Protect (attacker can't see)
2. **Claim airdrop** via Flashbots Protect
3. **Transfer to new wallet** immediately
4. All in same block if possible (atomic)

### 4. Race Condition
- Both user and attacker have same private key
- Whoever claims first wins
- Flashbots Protect prevents attacker from seeing your TX
- Use high gas price to ensure quick inclusion

## BscScan API V2 (Breaking Change)
BscScan V1 API deprecated. V2 requires paid plan for BSC.

Alternatives:
- Blockscout: `https://bsc.blockscout.com/api?module=account&action=tokenlist&address=ADDR`
- Direct RPC: `w3.eth.get_balance()` + known token contracts
- Etherscan V2: `https://api.etherscan.io/v2/api?chainid=56` (paid)

## Multi-Chain Activity Check
Check if wallet has history on chains (for airdrop eligibility):
```python
BLOCKSCOUT_CHAINS = [
    ("Ethereum", "https://eth.blockscout.com/api"),
    ("Arbitrum", "https://arbitrum.blockscout.com/api"),
    ("Optimism", "https://optimism.blockscout.com/api"),
    ("Base", "https://base.blockscout.com/api"),
    ("Polygon", "https://polygon.blockscout.com/api"),
]

for chain, api in BLOCKSCOUT_CHAINS:
    url = f"{api}?module=account&action=txlist&address={WALLET}&page=1&offset=5&sort=desc"
    r = requests.get(url, timeout=10)
    data = r.json()
    txs = data.get("result", [])
    if isinstance(txs, list) and len(txs) > 0:
        print(f"{chain}: {len(txs)}+ txs — POTENTIAL AIRDROP ELIGIBLE")
```
