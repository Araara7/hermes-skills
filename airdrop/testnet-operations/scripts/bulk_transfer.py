#!/usr/bin/env python3
"""
Bulk transfer ALL assets (native + ERC-20) from one wallet to another.
Supports 20+ testnet chains with L2 gas handling.

Usage:
    python3 bulk_transfer.py --seed "your seed phrase" --to 0xNEW_ADDR [--chains all|chain1,chain2]

Requires: web3, bip_utils, requests
"""

import argparse, json, time, sys, os
from web3 import Web3
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes

# ─── Chain Registry ──────────────────────────────────────────────
CHAINS = {
    "optimism_sepolia": {"name": "Optimism Sepolia", "rpc": "https://sepolia.optimism.io", "chain_id": 11155420, "blockscout": "https://optimism-sepolia.blockscout.com/api"},
    "arbitrum_sepolia": {"name": "Arbitrum Sepolia", "rpc": "https://sepolia-rollup.arbitrum.io/rpc", "chain_id": 421614, "blockscout": "https://arbitrum-sepolia.blockscout.com/api"},
    "base_sepolia": {"name": "Base Sepolia", "rpc": "https://sepolia.base.org", "chain_id": 84532, "blockscout": "https://base-sepolia.blockscout.com/api"},
    "blast_sepolia": {"name": "Blast Sepolia", "rpc": "https://sepolia.blast.io", "chain_id": 168587773},
    "opbnb_testnet": {"name": "opBNB Testnet", "rpc": "https://opbnb-testnet-rpc.bnbchain.org", "chain_id": 5611},
    "bnb_testnet": {"name": "BNB Testnet", "rpc": "https://data-seed-prebsc-1-s1.bnbchain.org:8545", "chain_id": 97},
    "abstract_testnet": {"name": "Abstract Testnet", "rpc": "https://api.testnet.abs.xyz", "chain_id": 11124, "blockscout": "https://explorer.testnet.abs.xyz/api"},
    "soneium_testnet": {"name": "Soneium Testnet", "rpc": "https://rpc.minato.soneium.org", "chain_id": 1946, "blockscout": "https://explorer-testnet.soneium.org/api"},
    "mode_sepolia": {"name": "Mode Sepolia", "rpc": "https://sepolia.mode.network", "chain_id": 919, "blockscout": "https://sepolia.explorer.mode.network/api"},
    "polygon_amoy": {"name": "Polygon Amoy", "rpc": "https://rpc-amoy.polygon.technology", "chain_id": 80002},
    "linea_sepolia": {"name": "Linea Sepolia", "rpc": "https://rpc.sepolia.linea.build", "chain_id": 59141},
    "scroll_sepolia": {"name": "Scroll Sepolia", "rpc": "https://sepolia-rpc.scroll.io", "chain_id": 534351},
    "lisk_sepolia": {"name": "Lisk Sepolia", "rpc": "https://rpc.api.lisk.com", "chain_id": 4202},
}

ERC20_ABI = json.loads('[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"type":"function"}]')

import requests

def discover_tokens(blockscout_url, wallet):
    """Get ERC-20 token list from Blockscout."""
    try:
        r = requests.get(f"{blockscout_url}?module=account&action=tokenlist&address={wallet}", timeout=15)
        tokens = r.json().get("result", [])
        return tokens if isinstance(tokens, list) else []
    except:
        return []

def send_native_l2(w3, chain_id, priv_key, from_addr, to_addr):
    """Send max native balance. Handles L2 L1-data-fee chains."""
    addr = Web3.to_checksum_address(from_addr)
    to = Web3.to_checksum_address(to_addr)
    bal = w3.eth.get_balance(addr)
    if bal == 0:
        return None, "zero"
    
    gas_price = w3.eth.gas_price
    
    # Try estimate + 50% buffer first
    try:
        est = w3.eth.estimate_gas({'from': addr, 'to': to, 'value': int(bal * 0.99)})
        sendable = bal - int(est * gas_price * 1.5)
        if sendable > 0:
            nonce = w3.eth.get_transaction_count(addr)
            tx = {'from': addr, 'to': to, 'value': sendable, 'gas': est,
                  'gasPrice': gas_price, 'nonce': nonce, 'chainId': chain_id}
            signed = w3.eth.account.sign_transaction(tx, priv_key)
            return w3.to_hex(w3.eth.send_raw_transaction(signed.raw_transaction)), None
    except:
        pass
    
    # Fallback: 99.5%
    sendable = int(bal * 0.995)
    nonce = w3.eth.get_transaction_count(addr)
    tx = {'from': addr, 'to': to, 'value': sendable, 'gas': 21000,
          'gasPrice': gas_price, 'nonce': nonce, 'chainId': chain_id}
    signed = w3.eth.account.sign_transaction(tx, priv_key)
    return w3.to_hex(w3.eth.send_raw_transaction(signed.raw_transaction)), None

def send_erc20(w3, chain_id, priv_key, from_addr, to_addr, token_addr):
    """Send entire ERC-20 balance."""
    addr = Web3.to_checksum_address(from_addr)
    to = Web3.to_checksum_address(to_addr)
    contract = w3.eth.contract(address=Web3.to_checksum_address(token_addr), abi=ERC20_ABI)
    
    bal = contract.functions.balanceOf(addr).call()
    if bal == 0:
        return None, "zero"
    
    gas_price = w3.eth.gas_price
    native_bal = w3.eth.get_balance(addr)
    if native_bal < 150000 * gas_price:
        return None, "no gas"
    
    nonce = w3.eth.get_transaction_count(addr)
    tx = contract.functions.transfer(to, bal).build_transaction({
        'from': addr, 'gas': 150000, 'gasPrice': gas_price,
        'nonce': nonce, 'chainId': chain_id
    })
    signed = w3.eth.account.sign_transaction(tx, priv_key)
    return w3.to_hex(w3.eth.send_raw_transaction(signed.raw_transaction)), None

def main():
    parser = argparse.ArgumentParser(description="Bulk transfer all testnet assets")
    parser.add_argument("--seed", required=True, help="BIP39 seed phrase")
    parser.add_argument("--to", required=True, help="Destination wallet address")
    parser.add_argument("--chains", default="all", help="Comma-separated chain keys or 'all'")
    parser.add_argument("--native-only", action="store_true", help="Skip ERC-20 transfers")
    args = parser.parse_args()
    
    # Derive key
    seed_bytes = Bip39SeedGenerator(args.seed).Generate()
    bip44 = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
    acc = bip44.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
    priv_key = acc.PrivateKey().Raw().ToHex()
    from_addr = acc.PublicKey().ToAddress()
    
    print(f"From: {from_addr}")
    print(f"To:   {args.to}")
    
    chain_keys = list(CHAINS.keys()) if args.chains == "all" else args.chains.split(",")
    
    results = []
    for key in chain_keys:
        cfg = CHAINS.get(key.strip())
        if not cfg:
            print(f"SKIP {key}: unknown chain")
            continue
        
        try:
            w3 = Web3(Web3.HTTPProvider(cfg["rpc"], request_kwargs={"timeout": 15}))
            if not w3.is_connected():
                results.append(f"SKIP {cfg['name']}: disconnected")
                continue
            
            # Native transfer
            tx_hash, err = send_native_l2(w3, cfg["chain_id"], priv_key, from_addr, args.to)
            if tx_hash:
                bal = w3.eth.get_balance(Web3.to_checksum_address(from_addr))
                results.append(f"SENT {cfg['name']} NATIVE -> {tx_hash}")
                time.sleep(2)
            elif err:
                results.append(f"SKIP {cfg['name']} NATIVE: {err}")
            
            # ERC-20 transfers
            if not args.native_only and cfg.get("blockscout"):
                tokens = discover_tokens(cfg["blockscout"], from_addr)
                for t in tokens:
                    t_addr = t.get("contractAddress") or t.get("address", "")
                    t_sym = t.get("symbol", "?")
                    if not t_addr:
                        continue
                    try:
                        tx_hash, err = send_erc20(w3, cfg["chain_id"], priv_key, from_addr, args.to, t_addr)
                        if tx_hash:
                            results.append(f"SENT {cfg['name']} {t_sym} -> {tx_hash}")
                            time.sleep(1)
                    except:
                        pass  # Skip broken contracts (BTO, ESUP, etc)
            
        except Exception as e:
            results.append(f"ERR {cfg['name']}: {str(e)[:80]}")
    
    print("\n=== RESULTS ===")
    for r in results:
        print(r)

if __name__ == "__main__":
    main()
