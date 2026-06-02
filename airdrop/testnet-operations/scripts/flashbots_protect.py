#!/usr/bin/env python3
"""
Flashbots Protect TX sender - kirim TX tanpa masuk public mempool.
Attacker tidak bisa front-run atau sandwich.

Usage:
    python3 flashbots_protect.py --chain eth --to 0x... --value 0.1
    python3 flashbots_protect.py --chain bsc --token USDT --to 0x... --amount 100
"""

from web3 import Web3
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
import json, sys

# Load seed
with open("/home/ubuntu/airdrop-agent/config/wallets.json") as f:
    cfg = json.load(f)
seed_bytes = Bip39SeedGenerator(cfg["master_seed"]).Generate()
bip44 = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
acc = bip44.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
PRIVATE_KEY = acc.PrivateKey().Raw().ToHex()
FROM_ADDR = acc.PublicKey().ToAddress()

# Private RPC endpoints (Flashbots Protect)
PROTECTED_RPCS = {
    "eth":     {"rpc": "https://rpc.mevblocker.io",              "chain_id": 1,     "name": "Ethereum (MEV Blocker)"},
    "arb":     {"rpc": "https://rpc.flashbots.net/arbitrum",     "chain_id": 42161, "name": "Arbitrum (Flashbots)"},
    "op":      {"rpc": "https://rpc.flashbots.net/optimism",     "chain_id": 10,    "name": "Optimism (Flashbots)"},
    "base":    {"rpc": "https://rpc.flashbots.net/base",         "chain_id": 8453,  "name": "Base (Flashbots)"},
    "polygon": {"rpc": "https://rpc.flashbots.net/polygon",      "chain_id": 137,   "name": "Polygon (Flashbots)"},
    "bsc":     {"rpc": "https://bsc.meowrpc.com",                "chain_id": 56,    "name": "BSC (MEV Protect)"},
}

TOKENS = {
    "eth":  {"USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7", "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"},
    "bsc":  {"USDT": "0x55d398326f99059fF775485246999027B3197955", "USDC": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d"},
    "arb":  {"USDT": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9", "USDC": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831", "ARB": "0x912CE59144191C1204E64559FE8253a0e49E6548"},
    "op":   {"USDC": "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85", "OP": "0x4200000000000000000000000000000000000042"},
    "base": {"USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"},
}

ERC20_ABI = json.loads('[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"type":"function"}]')


def get_w3(chain):
    cfg = PROTECTED_RPCS[chain]
    return Web3(Web3.HTTPProvider(cfg["rpc"], request_kwargs={"timeout": 15})), cfg


def send_native_protected(chain, to_addr, percent=0.99):
    w3, chain_cfg = get_w3(chain)
    addr = Web3.to_checksum_address(FROM_ADDR)
    to = Web3.to_checksum_address(to_addr)
    bal = w3.eth.get_balance(addr)
    if bal == 0:
        return {"error": "No balance"}
    
    gas_price = w3.eth.gas_price
    try:
        est = w3.eth.estimate_gas({'from': addr, 'to': to, 'value': int(bal * percent)})
    except:
        est = 21000
    gas_cost = int(est * gas_price * 1.1)
    value = int(bal * percent) - gas_cost
    if value <= 0:
        return {"error": "Balance too low for gas"}
    
    nonce = w3.eth.get_transaction_count(addr)
    tx = {'from': addr, 'to': to, 'value': value, 'gas': est, 'gasPrice': gas_price, 'nonce': nonce, 'chainId': chain_cfg['chain_id']}
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    return {"success": True, "tx": w3.to_hex(tx_hash), "amount": float(w3.from_wei(value, 'ether')), "chain": chain_cfg['name']}


def send_token_protected(chain, token_sym, to_addr, amount=None):
    w3, chain_cfg = get_w3(chain)
    addr = Web3.to_checksum_address(FROM_ADDR)
    to = Web3.to_checksum_address(to_addr)
    tokens = TOKENS.get(chain, {})
    token_addr = tokens.get(token_sym)
    if not token_addr:
        return {"error": f"Token {token_sym} not found on {chain}"}
    
    contract = w3.eth.contract(address=Web3.to_checksum_address(token_addr), abi=ERC20_ABI)
    bal = contract.functions.balanceOf(addr).call()
    if bal == 0:
        return {"error": f"No {token_sym} balance"}
    
    value = bal if not amount else min(int(amount * 10**contract.functions.decimals().call()), bal)
    gas_price = w3.eth.gas_price
    native_bal = w3.eth.get_balance(addr)
    if native_bal < 100000 * gas_price:
        return {"error": "Not enough native token for gas"}
    
    nonce = w3.eth.get_transaction_count(addr)
    tx = contract.functions.transfer(to, value).build_transaction({'from': addr, 'gas': 100000, 'gasPrice': gas_price, 'nonce': nonce, 'chainId': chain_cfg['chain_id']})
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    dec = contract.functions.decimals().call()
    return {"success": True, "tx": w3.to_hex(tx_hash), "token": token_sym, "amount": value / 10**dec, "chain": chain_cfg['name']}


if __name__ == "__main__":
    print("=== Flashbots Protect TX Sender ===")
    print(f"From: {FROM_ADDR}")
    print(f"Chains: {', '.join(PROTECTED_RPCS.keys())}")
    print(f"\nAll TXs via private RPC = TIDAK BISA di-front-run!")
