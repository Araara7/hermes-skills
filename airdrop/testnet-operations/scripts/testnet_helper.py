#!/usr/bin/env python3
"""
Testnet Operations Helper
Usage: python testnet_helper.py [network] [action] [args...]

Actions:
  balance <address>           - Check balance
  send <to> <amount>          - Send native token
  random-send <amount>        - Send to random address
  faucet <address>            - Claim from faucet

Examples:
  python testnet_helper.py monad_testnet balance 0x1234...
  python testnet_helper.py monad_testnet send 0x1234... 0.01
  python testnet_helper.py monad_testnet random-send 0.001
"""

import sys
import json
import secrets
from pathlib import Path

# Add parent directory
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from web3 import Web3
from eth_account import Account

# Testnet configurations
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
    }
}

def load_wallet():
    """Load wallet from credentials"""
    creds_file = Path.home() / "airdrop-agent" / "config" / "credentials" / ".env"
    if not creds_file.exists():
        print("❌ Credentials not found")
        return None
    
    # Read private key from .env
    with open(creds_file) as f:
        for line in f:
            if line.startswith("WALLET_PRIVATE_KEY="):
                pk = line.split("=", 1)[1].strip()
                return Account.from_key(pk)
    
    print("❌ Wallet private key not found in .env")
    return None

def get_web3(network):
    """Get Web3 instance"""
    if network not in TESTNETS:
        print(f"❌ Unknown network: {network}")
        print(f"   Available: {', '.join(TESTNETS.keys())}")
        return None, None
    
    config = TESTNETS[network]
    w3 = Web3(Web3.HTTPProvider(config["rpc"]))
    
    if not w3.is_connected():
        print(f"❌ Failed to connect to {network}")
        return None, None
    
    return w3, config

def check_balance(w3, address, symbol):
    """Check native balance"""
    balance_wei = w3.eth.get_balance(address)
    balance = w3.from_wei(balance_wei, 'ether')
    print(f"💰 Balance: {balance} {symbol}")
    return balance

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
    
    print(f"📤 TX Hash: {w3.to_hex(tx_hash)}")
    print(f"🔗 Explorer: {config['explorer']}/tx/{w3.to_hex(tx_hash)}")
    
    return w3.to_hex(tx_hash)

def send_to_random(w3, config, private_key, amount_eth):
    """Send to random address"""
    random_key = secrets.token_hex(32)
    random_account = Account.from_key(random_key)
    
    print(f"🎲 Random address: {random_account.address}")
    
    tx_hash = send_native(w3, config, private_key, random_account.address, amount_eth)
    return tx_hash

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    
    network = sys.argv[1]
    action = sys.argv[2]
    
    # Load wallet
    wallet = load_wallet()
    if not wallet:
        return
    
    # Connect to network
    w3, config = get_web3(network)
    if not w3:
        return
    
    print(f"🌐 Network: {network}")
    print(f"🦊 Wallet: {wallet.address}")
    print()
    
    if action == "balance":
        check_balance(w3, wallet.address, config['symbol'])
    
    elif action == "send":
        if len(sys.argv) < 5:
            print("Usage: send <to_address> <amount>")
            return
        to_address = sys.argv[3]
        amount = float(sys.argv[4])
        send_native(w3, config, wallet.key.hex(), to_address, amount)
    
    elif action == "random-send":
        if len(sys.argv) < 4:
            print("Usage: random-send <amount>")
            return
        amount = float(sys.argv[3])
        send_to_random(w3, config, wallet.key.hex(), amount)
    
    else:
        print(f"❌ Unknown action: {action}")

if __name__ == "__main__":
    main()
