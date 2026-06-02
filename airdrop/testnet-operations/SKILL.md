---
name: testnet-operations
description: Testnet blockchain operations — custom RPC, swap, bridge, send tokens, faucet, on-chain transactions for airdrop farming
tags: [airdrop, testnet, web3, swap, bridge, send, rpc, blockchain]
---

# 🔗 Testnet Operations

Skill untuk operasi on-chain di testnet: swap, bridge, send token, faucet claim.

## Setup

### Dependencies
```bash
pip install web3 eth-account requests
```

### Custom RPC Setup
```python
from web3 import Web3

# Contoh testnet RPCs
TESTNETS = {
    "ethereum_sepolia": {
        "rpc": "https://rpc.sepolia.org",
        "chain_id": 11155111,
        "explorer": "https://sepolia.etherscan.io",
        "symbol": "ETH"
    },
    "base_sepolia": {
        "rpc": "https://sepolia.base.org",
        "chain_id": 84532,
        "explorer": "https://sepolia.basescan.org",
        "symbol": "ETH"
    },
    "arbitrum_sepolia": {
        "rpc": "https://sepolia-rollup.arbitrum.io/rpc",
        "chain_id": 421614,
        "explorer": "https://sepolia.arbiscan.io",
        "symbol": "ETH"
    },
    "optimism_sepolia": {
        "rpc": "https://sepolia.optimism.io",
        "chain_id": 11155420,
        "explorer": "https://sepolia-optimistic.etherscan.io",
        "symbol": "ETH"
    },
    "polygon_amoy": {
        "rpc": "https://rpc-amoy.polygon.technology",
        "chain_id": 80002,
        "explorer": "https://amoy.polygonscan.com",
        "symbol": "POL"
    },
    "monad_testnet": {
        "rpc": "https://testnet-rpc.monad.xyz",
        "chain_id": 10143,
        "explorer": "https://testnet.monadexplorer.com",
        "symbol": "MON"
    },
    "berachain_bartio": {
        "rpc": "https://bartio.rpc.berachain.com",
        "chain_id": 80084,
        "explorer": "https://bartio.beratrail.io",
        "symbol": "BERA"
    },
    "abstract_testnet": {
        "rpc": "https://api.testnet.abs.xyz",
        "chain_id": 11124,
        "explorer": "https://sepolia.abscan.org",
        "symbol": "ETH"
    }
}

def get_web3(network_name):
    """Get Web3 instance for a testnet"""
    if network_name not in TESTNETS:
        raise ValueError(f"Unknown network: {network_name}")
    
    config = TESTNETS[network_name]
    w3 = Web3(Web3.HTTPProvider(config["rpc"]))
    
    if not w3.is_connected():
        raise ConnectionError(f"Failed to connect to {network_name}")
    
    return w3, config
```

## Wallet Operations

### Load Wallet
```python
from eth_account import Account

def load_wallet(private_key):
    """Load wallet from private key"""
    account = Account.from_key(private_key)
    return account

def create_wallet():
    """Create new wallet"""
    account = Account.create()
    return account
```

### Check Balance
```python
def get_balance(w3, address):
    """Get native token balance"""
    balance_wei = w3.eth.get_balance(address)
    balance_eth = w3.from_wei(balance_wei, 'ether')
    return balance_eth

def get_token_balance(w3, token_address, wallet_address):
    """Get ERC20 token balance"""
    abi = [{"constant":True,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"}]
    contract = w3.eth.contract(address=token_address, abi=abi)
    balance = contract.functions.balanceOf(wallet_address).call()
    return balance
```

## Send Token

### Send Native Token (ETH/MON/BERA)
```python
def send_native(w3, config, private_key, to_address, amount_eth):
    """Send native token"""
    account = Account.from_key(private_key)
    
    tx = {
        'from': account.address,
        'to': to_address,
        'value': w3.to_wei(amount_eth, 'ether'),
        'gas': 21000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(account.address),
        'chainId': config['chain_id']
    }
    
    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    
    return w3.to_hex(tx_hash)
```

### Send ERC20 Token
```python
def send_token(w3, config, private_key, token_address, to_address, amount):
    """Send ERC20 token"""
    account = Account.from_key(private_key)
    
    # ERC20 transfer ABI
    abi = [{"constant":False,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"type":"function"}]
    
    contract = w3.eth.contract(address=token_address, abi=abi)
    
    tx = contract.functions.transfer(to_address, amount).build_transaction({
        'from': account.address,
        'gas': 100000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(account.address),
        'chainId': config['chain_id']
    })
    
    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    
    return w3.to_hex(tx_hash)
```

### Send to Random Address
```python
import secrets

def send_to_random(w3, config, private_key, amount_eth):
    """Send to random address (for volume)"""
    # Generate random address
    random_key = secrets.token_hex(32)
    random_account = Account.from_key(random_key)
    
    tx_hash = send_native(w3, config, private_key, random_account.address, amount_eth)
    
    return tx_hash, random_account.address
```

## Swap Operations

### Uniswap V2 Swap
```python
def swap_uniswap_v2(w3, config, private_key, router_address, token_in, token_out, amount_in, min_amount_out):
    """Swap on Uniswap V2 compatible DEX"""
    account = Account.from_key(private_key)
    
    # Uniswap V2 Router ABI (swapExactTokensForTokens)
    abi = [{
        "constant": False,
        "inputs": [
            {"name": "amountIn", "type": "uint256"},
            {"name": "amountOutMin", "type": "uint256"},
            {"name": "path", "type": "address[]"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactTokensForTokens",
        "outputs": [{"name": "amounts", "type": "uint256[]"}],
        "type": "function"
    }]
    
    router = w3.eth.contract(address=router_address, abi=abi)
    
    deadline = w3.eth.get_block('latest').timestamp + 1200
    
    tx = router.functions.swapExactTokensForTokens(
        amount_in,
        min_amount_out,
        [token_in, token_out],
        account.address,
        deadline
    ).build_transaction({
        'from': account.address,
        'gas': 300000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(account.address),
        'chainId': config['chain_id']
    })
    
    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    
    return w3.to_hex(tx_hash)
```

### Swap Native to Token (ETH -> Token)
```python
def swap_eth_for_tokens(w3, config, private_key, router_address, token_out, amount_eth, min_amount_out):
    """Swap native token for ERC20"""
    account = Account.from_key(private_key)
    
    abi = [{
        "constant": False,
        "inputs": [
            {"name": "amountOutMin", "type": "uint256"},
            {"name": "path", "type": "address[]"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactETHForTokens",
        "outputs": [{"name": "amounts", "type": "uint256[]"}],
        "type": "function"
    }]
    
    router = w3.eth.contract(address=router_address, abi=abi)
    
    deadline = w3.eth.get_block('latest').timestamp + 1200
    
    # WETH address (usually)
    weth = router.functions.WETH().call()
    
    tx = router.functions.swapExactETHForTokens(
        min_amount_out,
        [weth, token_out],
        account.address,
        deadline
    ).build_transaction({
        'from': account.address,
        'value': w3.to_wei(amount_eth, 'ether'),
        'gas': 300000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(account.address),
        'chainId': config['chain_id']
    })
    
    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    
    return w3.to_hex(tx_hash)
```

## Bridge Operations

### Bridge via Contract
```python
def bridge_tokens(w3, config, private_key, bridge_contract, dest_chain_id, amount):
    """Bridge tokens to another chain"""
    account = Account.from_key(private_key)
    
    # Generic bridge ABI
    abi = [{
        "constant": False,
        "inputs": [
            {"name": "destChainId", "type": "uint256"},
            {"name": "amount", "type": "uint256"}
        ],
        "name": "bridge",
        "outputs": [],
        "type": "function"
    }]
    
    bridge = w3.eth.contract(address=bridge_contract, abi=abi)
    
    tx = bridge.functions.bridge(dest_chain_id, amount).build_transaction({
        'from': account.address,
        'value': amount,  # If bridging native token
        'gas': 500000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(account.address),
        'chainId': config['chain_id']
    })
    
    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    
    return w3.to_hex(tx_hash)
```

## Faucet Claim

### Claim from Faucet
```python
import requests

def claim_faucet(faucet_url, wallet_address):
    """Claim testnet tokens from faucet"""
    try:
        resp = requests.post(faucet_url, json={"address": wallet_address})
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        else:
            return {"success": False, "error": resp.text}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

## Utility

### Wait for Transaction
```python
def wait_for_tx(w3, tx_hash, timeout=120):
    """Wait for transaction confirmation"""
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
    return receipt

### Generate Random Amount
```python
import random

def random_amount(min_eth=0.001, max_eth=0.01):
    """Generate random ETH amount"""
    return round(random.uniform(min_eth, max_eth), 6)
```

## Checklist

- [ ] RPC terhubung
- [ ] Wallet ada balance
- [ ] Gas cukup
- [ ] Contract address benar
- [ ] Transaction confirmed

## Multi-Chain Wallet Scan

Scan balance di 30+ testnet sekaligus. Berguna untuk audit wallet lama atau cek farming progress.

```python
from web3 import Web3
import requests

TESTNETS = {
    "Ethereum Sepolia": {"rpc": "https://rpc.sepolia.org", "symbol": "ETH", "chain_id": 11155111},
    "Ethereum Holesky": {"rpc": "https://ethereum-holesky-rpc.publicnode.com", "symbol": "ETH", "chain_id": 17000},
    "Base Sepolia": {"rpc": "https://sepolia.base.org", "symbol": "ETH", "chain_id": 84532},
    "Arbitrum Sepolia": {"rpc": "https://sepolia-rollup.arbitrum.io/rpc", "symbol": "ETH", "chain_id": 421614},
    "Optimism Sepolia": {"rpc": "https://sepolia.optimism.io", "symbol": "ETH", "chain_id": 11155420},
    "Polygon Amoy": {"rpc": "https://rpc-amoy.polygon.technology", "symbol": "POL", "chain_id": 80002},
    "Linea Sepolia": {"rpc": "https://rpc.sepolia.linea.build", "symbol": "ETH", "chain_id": 59141},
    "Scroll Sepolia": {"rpc": "https://sepolia-rpc.scroll.io", "symbol": "ETH", "chain_id": 534351},
    "Blast Sepolia": {"rpc": "https://sepolia.blast.io", "symbol": "ETH", "chain_id": 168587773},
    "Zora Sepolia": {"rpc": "https://sepolia.rpc.zora.energy", "symbol": "ETH", "chain_id": 999999999},
    "Abstract Testnet": {"rpc": "https://api.testnet.abs.xyz", "symbol": "ETH", "chain_id": 11124},
    "Monad Testnet": {"rpc": "https://testnet-rpc.monad.xyz", "symbol": "MON", "chain_id": 10143},
    "Berachain Bartio": {"rpc": "https://bartio.rpc.berachain.com", "symbol": "BERA", "chain_id": 80084},
    "Soneium Testnet": {"rpc": "https://rpc.minato.soneium.org", "symbol": "ETH", "chain_id": 1946},
    "Mode Sepolia": {"rpc": "https://sepolia.mode.network", "symbol": "ETH", "chain_id": 919},
    "opBNB Testnet": {"rpc": "https://opbnb-testnet-rpc.bnbchain.org", "symbol": "tBNB", "chain_id": 5611},
    "BNB Testnet": {"rpc": "https://data-seed-prebsc-1-s1.bnbchain.org:8545", "symbol": "tBNB", "chain_id": 97},
    "Mantle Sepolia": {"rpc": "https://rpc.sepolia.mantle.xyz", "symbol": "MNT", "chain_id": 5003},
    "Lisk Sepolia": {"rpc": "https://rpc.api.lisk.com", "symbol": "ETH", "chain_id": 4202},
    "Taiko Hekla": {"rpc": "https://rpc.hekla.taiko.xyz", "symbol": "ETH", "chain_id": 167009},
    "Worldchain Sepolia": {"rpc": "https://worldchain-sepolia.g.alchemy.com/public", "symbol": "ETH", "chain_id": 4801},
    "Shape Sepolia": {"rpc": "https://sepolia.shape.network", "symbol": "ETH", "chain_id": 11011},
    "Ink Sepolia": {"rpc": "https://rpc-gel-sepolia.inkonchain.com", "symbol": "ETH", "chain_id": 763373},
    "Unichain Sepolia": {"rpc": "https://sepolia.unichain.org", "symbol": "ETH", "chain_id": 1301},
}

def scan_all_native(wallet_address):
    """Scan native balance across all testnets."""
    results = {}
    for name, cfg in TESTNETS.items():
        try:
            w3 = Web3(Web3.HTTPProvider(cfg["rpc"], request_kwargs={"timeout": 10}))
            if w3.is_connected():
                bal = w3.eth.get_balance(Web3.to_checksum_address(wallet_address))
                bal_eth = float(w3.from_wei(bal, 'ether'))
                if bal_eth > 0:
                    results[name] = {"balance": bal_eth, "symbol": cfg["symbol"], "chain_id": cfg["chain_id"]}
        except:
            pass
    return results
```

## ERC-20 Token Discovery via Blockscout

Use Blockscout API to discover ALL ERC-20 tokens held by a wallet. Much better than hardcoding token addresses.

```python
import requests

BLOCKSCOUT_ENDPOINTS = {
    "Optimism Sepolia": "https://optimism-sepolia.blockscout.com/api",
    "Arbitrum Sepolia": "https://arbitrum-sepolia.blockscout.com/api",
    "Base Sepolia": "https://base-sepolia.blockscout.com/api",
    "Abstract Testnet": "https://explorer.testnet.abs.xyz/api",
    "Soneium Testnet": "https://explorer-testnet.soneium.org/api",
    "Mode Sepolia": "https://sepolia.explorer.mode.network/api",
}

def discover_tokens(wallet_address, chain_name, blockscout_url):
    """Get all ERC-20 tokens held by wallet via Blockscout."""
    url = f"{blockscout_url}?module=account&action=tokenlist&address={wallet_address}"
    r = requests.get(url, timeout=15)
    data = r.json()
    tokens = data.get("result", [])
    if not isinstance(tokens, list):
        return []
    return [
        {
            "symbol": t.get("symbol", "?"),
            "name": t.get("name", "?"),
            "address": t.get("contractAddress") or t.get("address", ""),
            "balance_raw": t.get("balance", "0"),
            "decimals": int(t.get("decimals", 18)),
        }
        for t in tokens if t.get("contractAddress") or t.get("address")
    ]
```

## Seed Phrase → EVM Private Key Derivation

Derive EVM private key from BIP39 seed phrase using BIP44 path `m/44'/60'/0'/0/0`.

```python
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes

def derive_evm_key(seed_phrase, index=0):
    """Derive EVM private key and address from seed phrase."""
    seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
    bip44 = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
    account = bip44.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(index)
    priv_key = account.PrivateKey().Raw().ToHex()
    address = account.PublicKey().ToAddress()
    return priv_key, address

# Usage with wallets.json config:
import json
with open("config/wallets.json") as f:
    cfg = json.load(f)
priv_key, addr = derive_evm_key(cfg["master_seed"])
```

## Bulk Transfer (Native + ERC-20)

Transfer ALL assets from one wallet to another across multiple chains.

```python
from web3 import Web3
import json, time

ERC20_ABI = json.loads('[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"type":"function"}]')

def send_all_native(w3, chain_id, from_key, from_addr, to_addr):
    """Send entire native balance minus gas. Handles L2 L1-data-fee chains."""
    addr = Web3.to_checksum_address(from_addr)
    to = Web3.to_checksum_address(to_addr)
    bal = w3.eth.get_balance(addr)
    if bal == 0:
        return None, "zero balance"
    
    gas_price = w3.eth.gas_price
    
    # L2 chains have L1 data fees — use 99.5% approach
    # First try estimate_gas for accuracy
    try:
        est_gas = w3.eth.estimate_gas({'from': addr, 'to': to, 'value': int(bal * 0.99)})
    except:
        est_gas = 21000
    
    # Calculate gas with 10% buffer
    total_gas = int(est_gas * gas_price * 1.1)
    sendable = bal - total_gas
    
    if sendable <= 0:
        # Fallback: send 99.5% of balance (handles L1 data fee chains)
        sendable = int(bal * 0.995)
    
    nonce = w3.eth.get_transaction_count(addr)
    tx = {
        'from': addr, 'to': to, 'value': sendable,
        'gas': est_gas, 'gasPrice': gas_price,
        'nonce': nonce, 'chainId': chain_id
    }
    
    signed = w3.eth.account.sign_transaction(tx, from_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    return w3.to_hex(tx_hash), None

def send_all_erc20(w3, chain_id, from_key, from_addr, to_addr, token_addr):
    """Send entire ERC-20 token balance."""
    addr = Web3.to_checksum_address(from_addr)
    to = Web3.to_checksum_address(to_addr)
    contract = w3.eth.contract(address=Web3.to_checksum_address(token_addr), abi=ERC20_ABI)
    
    bal = contract.functions.balanceOf(addr).call()
    if bal == 0:
        return None, "zero balance"
    
    # Check gas availability
    gas_price = w3.eth.gas_price
    native_bal = w3.eth.get_balance(addr)
    if native_bal < 150000 * gas_price:
        return None, "not enough gas for ERC-20 transfer"
    
    nonce = w3.eth.get_transaction_count(addr)
    tx = contract.functions.transfer(to, bal).build_transaction({
        'from': addr, 'gas': 150000, 'gasPrice': gas_price,
        'nonce': nonce, 'chainId': chain_id
    })
    
    signed = w3.eth.account.sign_transaction(tx, from_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    return w3.to_hex(tx_hash), None
```

## Private RPC / Flashbots Protect

Kirim TX tanpa masuk public mempool. Attacker **tidak bisa front-run** atau sandwich.

### Protected RPC Endpoints
```python
PROTECTED_RPCS = {
    "ethereum": "https://rpc.mevblocker.io",        # Flashbots MEV Blocker
    "arbitrum": "https://rpc.flashbots.net/arbitrum",
    "optimism": "https://rpc.flashbots.net/optimism",
    "base": "https://rpc.flashbots.net/base",
    "polygon": "https://rpc.flashbots.net/polygon",
    "bsc": "https://bsc.meowrpc.com",                # BSC MEV Protect
}
```

### Usage — Same as normal Web3, just different RPC
```python
w3 = Web3(Web3.HTTPProvider("https://rpc.mevblocker.io"))
# TX goes to block builder directly, NOT public mempool
# Attacker cannot see or front-run
```

### When to Use
- Claiming airdrop from compromised wallet (race condition with attacker)
- Any high-value TX where front-running is a risk
- Moving funds from hot wallet to cold wallet

### How It Works
```
NORMAL:  Kamu → Mempool (public) → Attacker lihat → Front-run → Block ❌
PROTECT: Kamu → Private Relay → Block Builder → Block ✅
```

## Compromised Wallet Recovery

Ketika wallet compromised tapi masih punya seed phrase:

### Strategy
1. **Scan remaining assets** — native + ERC-20 di semua chain (pakai Blockscout)
2. **Check airdrop eligibility** — wallet mungkin masih eligible klaim
3. **Flashbots Protect** — semua TX via private RPC
4. **Race condition** — attacker juga punya key, harus lebih cepat
5. **Claim → transfer** — langsung pindah ke wallet baru setelah klaim

### Bulk Recovery Script Pattern
```python
# 1. Scan semua chain
for chain_name, rpc, chain_id in ALL_CHAINS:
    w3 = Web3(Web3.HTTPProvider(rpc))
    native = w3.eth.get_balance(old_wallet)
    # + check ERC-20 via Blockscout

# 2. Transfer via Flashbots Protect
w3 = Web3(Web3.HTTPProvider(PROTECTED_RPCS[chain_name]))
# send_all_native() or send_all_erc20() as above
```

### BscScan API V2 (Breaking Change 2025)
BscScan V1 API deprecated. V2 requires paid plan for BSC chain.
Alternatives:
- Blockscout: `https://bsc.blockscout.com/api?module=account&action=tokenlist&address=ADDR`
- Direct RPC: `w3.eth.get_balance()` + known token contracts
- Etherscan V2: `https://api.etherscan.io/v2/api?chainid=56` (paid)

## Security Audit Results (2 June 2026)

Seed phrase leaks found and fixed in:
1. `jay_sudoku_solver.py` line 34 — hardcoded seed → now loads from wallets.json
2. `~/.hermes/skills/airdrop/jay-chess-monitor/references/sudoku-automation.md` — removed
3. Cron output `~/.hermes/cron/output/da3c85af0fef/2026-05-31_08-26-15.md` — deleted
4. 9 temp scripts in `/tmp/send_jay*.py` — deleted

**Root cause:** Seed phrase was hardcoded before `config_loader.py` pattern was established.

## Educational Materials

Full drainer/attack educational content stored at:
- `~/airdrop-agent/data/edukasi/DrainSimulator.sol` — Smart contract (Solidity)
- `~/airdrop-agent/data/edukasi/drainer_bot.py` — Bot simulation (Python)
- `~/airdrop-agent/data/edukasi/deploy_testnet.py` — Testnet deploy script
- `~/airdrop-agent/data/edukasi/README.md` — Comprehensive guide
- `~/airdrop-agent/data/edukasi_drainer.md` — Attack mechanics explained

## GitHub Secret Scanner

Deployed at `~/airdrop-agent/scripts/github_secret_scanner.py`.
Systemd service: `sudo systemctl start github-scanner`.
Output: `~/airdrop-agent/data/github_scanner/findings.jsonl`.

## Pitfalls

⚠️ **JANGAN:**
- Pakai private key di production — gunakan `.env` + `config_loader.py`
- Skip gas estimation — selalu estimate dulu
- Lupa cek balance sebelum tx
- Pakai mainnet RPC di script testnet
- Kirim `value = balance - (gas * 21000)` di L2 chains — PASTI gagal!
- Hardcode token addresses — gunakan Blockscout discovery

✅ **LAKUKAN:**
- Test dengan amount kecil dulu
- Simpan tx hash, verify di explorer
- Untuk L2 (Base/Arb/OP/Blast/Scroll): kirim 99.5% balance, jangan hitung gas manual
- Gunakan `estimate_gas()` + 10-20% buffer untuk akurasi
- Scan Blockscout untuk discover ERC-20, jangan hardcode
- `bip_utils` untuk derive key dari seed — jangan simpan private key langsung
- Wait for receipt di bulk transfer untuk confirm success

### L2 Gas Pitfalls (Critical!)

L2 chains (Base, Arbitrum, Optimism, Blast, Scroll, opBNB, Abstract, Soneium, Mode) have **L1 data fees** on top of L2 gas. This means:
- `w3.eth.gas_price` only returns L2 gas price
- Actual cost = L2 gas + L1 data fee (not exposed via standard RPC)
- Sending `balance - (21000 * gas_price)` will FAIL with "insufficient funds"
- **Solution**: Send 99.5% of balance instead of calculating exact gas

**Tested working chains** (verified with real transfers):
- ✅ Optimism Sepolia: legacy gasPrice works
- ✅ Arbitrum Sepolia: legacy gasPrice works (NOT EIP-1559 `maxFeePerGas`)
- ✅ Base Sepolia: legacy gasPrice works
- ✅ Blast Sepolia: 99.5% approach needed
- ✅ opBNB Testnet: 99.5% approach needed
- ✅ Soneium Testnet: 99.5% approach needed
- ✅ Mode Sepolia: estimate_gas + 1.5x buffer works
- ✅ Scroll Sepolia: 99.5% approach needed (has explicit L1 fee error)
- ✅ Abstract Testnet: 99.5% approach needed

See also: `references/l2-gas-handling.md` for detailed error messages and fixes.
See also: `references/flashbots-protect.md` for private TX endpoints and compromised wallet recovery.
See also: `references/cosmos-sdk-tx-signing.md` for Cosmos SDK protobuf tx signing (nested PubKey, 64-byte compact sig).
See also: `references/security-audit-patterns.md` for scanning codebases and git history for leaked secrets (private keys, seed phrases, API tokens).
See also: `references/github-secret-scanner.md` for GitHub real-time secret scanning (educational/defensive).
See also: `references/drainer-defense-guide.md` for crypto drainer types and defense strategies.
Scripts: `scripts/flashbots_protect.py` — TX sender via private RPC (Flashbots Protect).
Scripts: `~/airdrop-agent/scripts/github_secret_scanner.py` — GitHub secret scanner (systemd service).
Educational: `~/airdrop-agent/data/edukasi/` — Full drainer/attack educational materials (Solidity, Python, docs).

## Airdrop Eligibility Scanning (Compromised Wallet)

When wallet is compromised but seed phrase is known, check for unclaimed airdrops:

```python
import requests
from web3 import Web3

OLD = "0x..."
BLOCKSCOUT_CHAINS = [
    ("Ethereum", "https://eth.blockscout.com/api"),
    ("Arbitrum", "https://arbitrum.blockscout.com/api"),
    ("Optimism", "https://optimism.blockscout.com/api"),
    ("Base", "https://base.blockscout.com/api"),
    ("Polygon", "https://polygon.blockscout.com/api"),
    ("Gnosis", "https://gnosis.blockscout.com/api"),
]

for chain, api in BLOCKSCOUT_CHAINS:
    # Check tx history (confirms on-chain activity)
    r = requests.get(f"{api}?module=account&action=txlist&address={OLD}&page=1&offset=5&sort=desc", timeout=10)
    txs = r.json().get("result", [])
    if isinstance(txs, list) and txs:
        print(f"{chain}: {len(txs)}+ txs — potential airdrop eligibility")
    
    # Check token interactions
    r2 = requests.get(f"{api}?module=account&action=tokentx&address={OLD}&page=1&offset=50&sort=desc", timeout=10)
    token_txs = r2.json().get("result", [])
    if isinstance(token_txs, list) and token_txs:
        seen = set()
        for tx in token_txs:
            sym = tx.get("tokenSymbol", "?")
            if sym not in seen:
                seen.add(sym)
                print(f"  Interacted: {sym}")
```

### Claim Strategy
1. Monitor airdrop checkers (earni.fi, airdrops.io, official claim pages)
2. When eligible: deposit gas via Flashbots Protect → claim via Flashbots Protect → transfer to new wallet
3. Race condition: attacker has same key, must be faster
4. Use private RPC to prevent front-running
