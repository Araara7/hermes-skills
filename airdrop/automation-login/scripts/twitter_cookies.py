#!/usr/bin/env python3
"""
Twitter Cookies Loader - Load and use exported cookies
Usage: python twitter_cookies.py [load|test|save]
"""

import sys
import json
from pathlib import Path

COOKIES_DIR = Path.home() / "airdrop-agent" / "data" / "cookies"

def load_cookies(cookies_file):
    """Load cookies from JSON file"""
    with open(cookies_file) as f:
        return json.load(f)

def save_cookies(cookies, output_file):
    """Save cookies to file"""
    with open(output_file, "w") as f:
        json.dump(cookies, f, indent=2)
    print(f"💾 Saved {len(cookies)} cookies to {output_file}")

def test_cookies(cookies_file):
    """Test if cookies are valid"""
    from camoufox.sync_api import Camoufox
    
    cookies = load_cookies(cookies_file)
    
    with Camoufox(headless=True) as browser:
        context = browser.new_context()
        context.add_cookies(cookies)
        
        page = context.new_page()
        page.goto("https://twitter.com/home")
        page.wait_for_load_state("networkidle")
        
        if "home" in page.url:
            print("✅ Cookies masih valid!")
            return True
        else:
            print("❌ Cookies expired")
            return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python twitter_cookies.py [load|test|save]")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "load":
        cookies_file = COOKIES_DIR / "twitter_cookies.json"
        if cookies_file.exists():
            cookies = load_cookies(cookies_file)
            print(f"🍪 Loaded {len(cookies)} cookies")
        else:
            print("❌ No cookies file found")
    
    elif action == "test":
        cookies_file = COOKIES_DIR / "twitter_cookies.json"
        if cookies_file.exists():
            test_cookies(cookies_file)
        else:
            print("❌ No cookies file found")
    
    elif action == "save":
        if len(sys.argv) < 3:
            print("Usage: python twitter_cookies.py save <cookies_json>")
            sys.exit(1)
        cookies_json = sys.argv[2]
        cookies = json.loads(cookies_json)
        save_cookies(cookies, COOKIES_DIR / "twitter_cookies.json")
