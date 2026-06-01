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

## Pitfalls

⚠️ **JANGAN:**
- Pakai private key di production
- Skip gas estimation
- Lupa cek balance sebelum tx
- Pakai mainnet RPC

✅ **LAKUKAN:**
- Test dengan amount kecil dulu
- Cek gas price
- Simpan tx hash
- Verify di explorer
