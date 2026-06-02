## Airdrop Recovery from Compromised Wallet

Even after compromise, wallet may still be eligible for airdrops based on historical on-chain activity. Both user AND attacker have the private key = **race condition**.

### Verified Activity (Old Wallet 0xb01E...de3E)
- Ethereum: 20+ txs (USDC, zkPass, Omni Network, Arkham interactions)
- Arbitrum: 10+ txs
- Optimism: 10+ txs
- Base: Active
- Polygon: Active
- 2 NFTs (ERC-721)
- Potential eligibility: zkPass, Omni, Arkham, LayerZero, Arbitrum, Optimism

### Recovery Strategy — Flashbots Protect
1. Monitor eligibility (`earni.fi`, `airdrops.io`, official claim pages)
2. Deposit gas via **private RPC** (Flashbots Protect) — attacker can't see TX
3. Claim airdrop via private RPC
4. Transfer to new wallet via private RPC

**Protected RPC Endpoints:**
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

**CRITICAL:** Do NOT deposit gas without immediately claiming! Attacker runs auto-sweeper — any gas deposited will be swept within seconds. Deposit + claim must happen in rapid succession, ideally same block.

**Scripts:** `~/airdrop-agent/scripts/flashbots_protect.py` and `~/airdrop-agent/scripts/airdrop_protect.py`

### BscScan API V2 Migration
BscScan V1 API deprecated (2025). V2 requires paid plan for BSC chain.
```python
# ❌ Old (deprecated)
"https://api.bscscan.com/api?module=account&action=tokentx&address=..."

# ✅ Alternatives
"https://bsc.blockscout.com/api?module=account&action=tokenlist&address=..."
# Or direct RPC: w3.eth.get_balance() + known token contracts
```
