#!/usr/bin/env python3
"""
Wallet Deriver - Derive Ethereum address from private key
Usage: python wallet_deriver.py <private_key>
"""

import sys
from eth_account import Account

def derive_address(private_key):
    """Derive Ethereum address from private key"""
    try:
        account = Account.from_key(private_key)
        return {
            "address": account.address,
            "private_key": private_key
        }
    except Exception as e:
        return {"error": str(e)}

def main():
    if len(sys.argv) < 2:
        print("Usage: python wallet_deriver.py <private_key>")
        print("Example: python wallet_deriver.py 0xabc123...")
        sys.exit(1)
    
    private_key = sys.argv[1]
    
    # Ensure 0x prefix
    if not private_key.startswith("0x"):
        private_key = "0x" + private_key
    
    result = derive_address(private_key)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        sys.exit(1)
    
    print(f"✅ Address: {result['address']}")
    print(f"🔑 Key: {result['private_key']}")

if __name__ == "__main__":
    main()
