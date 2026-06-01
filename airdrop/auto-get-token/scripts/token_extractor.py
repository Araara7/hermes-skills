#!/usr/bin/env python3
"""
Token Extractor - Extract JWT, API keys, auth tokens from web apps
Usage: python token_extractor.py <url>
"""

import sys
import json
import base64
from pathlib import Path

def decode_jwt(token):
    """Decode JWT payload"""
    parts = token.split(".")
    if len(parts) != 3:
        return None
    
    payload = parts[1]
    payload += "=" * (4 - len(payload) % 4)
    
    try:
        decoded = base64.b64decode(payload)
        return json.loads(decoded)
    except:
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python token_extractor.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    print(f"Token Extractor - Target: {url}")
    print("Use Playwright to intercept and extract tokens")
    print("See SKILL.md for full implementation")

if __name__ == "__main__":
    main()
