#!/usr/bin/env python3
"""
Proxy Manager - Manage and rotate proxies for airdrop tasks
Usage: python proxy_manager.py [check|rotate|test]
"""

import sys
import json
import random
import requests
from pathlib import Path

CONFIG_DIR = Path.home() / "airdrop-agent" / "config"
PROXY_FILE = CONFIG_DIR / "proxies.json"

def load_proxies():
    """Load proxy list"""
    if not PROXY_FILE.exists():
        return []
    with open(PROXY_FILE) as f:
        return json.load(f)

def save_proxies(proxies):
    """Save proxy list"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROXY_FILE, "w") as f:
        json.dump(proxies, f, indent=2)

def test_proxy(proxy):
    """Test if proxy works"""
    try:
        proxies = {"http": proxy, "https": proxy}
        resp = requests.get("https://api.ipify.org", proxies=proxies, timeout=10)
        return {"status": "ok", "ip": resp.text}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def rotate_proxy():
    """Get random proxy from pool"""
    proxies = load_proxies()
    if not proxies:
        print("No proxies configured!")
        return None
    return random.choice(proxies)

def main():
    if len(sys.argv) < 2:
        print("Usage: python proxy_manager.py [check|rotate|test]")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "check":
        proxies = load_proxies()
        print(f"Total proxies: {len(proxies)}")
        for p in proxies:
            print(f"  - {p}")
    
    elif action == "rotate":
        proxy = rotate_proxy()
        if proxy:
            print(f"Selected proxy: {proxy}")
    
    elif action == "test":
        if len(sys.argv) < 3:
            print("Usage: python proxy_manager.py test <proxy_url>")
            sys.exit(1)
        proxy = sys.argv[2]
        result = test_proxy(proxy)
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown action: {action}")

if __name__ == "__main__":
    main()
