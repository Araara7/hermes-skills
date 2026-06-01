#!/usr/bin/env python3
"""
Twitter Login Helper - Validate and use Twitter cookies
Usage: python twitter_login_helper.py [validate|api <endpoint>]
"""

import sys
import json
import requests
from pathlib import Path

# Twitter's public Bearer token (captured from network traffic)
TWITTER_BEARER = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA3"

COOKIES_DIR = Path.home() / "airdrop-agent" / "data" / "cookies"

def load_cookies():
    """Load Twitter cookies from file"""
    cookie_file = COOKIES_DIR / "twitter_cookies.json"
    if not cookie_file.exists():
        return None
    with open(cookie_file) as f:
        return json.load(f)

def validate_cookies(auth_token, ct0):
    """Validate Twitter cookies"""
    
    cookies = {"auth_token": auth_token, "ct0": ct0}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
        "Authorization": TWITTER_BEARER,
        "x-csrf-token": ct0,
    }
    
    resp = requests.get(
        "https://api.x.com/1.1/account/verify_credentials.json",
        cookies=cookies,
        headers=headers
    )
    
    if resp.status_code == 200:
        data = resp.json()
        return {
            "valid": True,
            "username": data.get("screen_name"),
            "name": data.get("name"),
            "id": data.get("id_str"),
            "followers": data.get("followers_count"),
            "following": data.get("friends_count"),
        }
    else:
        return {
            "valid": False,
            "status": resp.status_code,
            "error": resp.json().get("errors", [{}])[0].get("message", "Unknown error")
        }

def call_api(endpoint, auth_token, ct0, method="GET"):
    """Call Twitter API with cookies"""
    
    cookies = {"auth_token": auth_token, "ct0": ct0}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
        "Authorization": TWITTER_BEARER,
        "x-csrf-token": ct0,
    }
    
    url = f"https://api.x.com/1.1/{endpoint}"
    
    if method == "GET":
        resp = requests.get(url, cookies=cookies, headers=headers)
    else:
        resp = requests.post(url, cookies=cookies, headers=headers)
    
    return resp.json()

def main():
    if len(sys.argv) < 2:
        print("Usage: python twitter_login_helper.py [validate|api <endpoint>]")
        print("\nExamples:")
        print("  python twitter_login_helper.py validate")
        print("  python twitter_login_helper.py api statuses/home_timeline.json")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "validate":
        # Get cookies from user
        auth_token = input("auth_token: ").strip()
        ct0 = input("ct0: ").strip()
        
        result = validate_cookies(auth_token, ct0)
        print(json.dumps(result, indent=2))
        
        if result.get("valid"):
            # Save cookies
            COOKIES_DIR.mkdir(parents=True, exist_ok=True)
            with open(COOKIES_DIR / "twitter_cookies.json", "w") as f:
                json.dump({"auth_token": auth_token, "ct0": ct0}, f, indent=2)
            print(f"\n💾 Cookies saved to {COOKIES_DIR / 'twitter_cookies.json'}")
    
    elif action == "api":
        if len(sys.argv) < 3:
            print("Usage: python twitter_login_helper.py api <endpoint>")
            sys.exit(1)
        
        endpoint = sys.argv[2]
        
        # Load saved cookies
        cookies = load_cookies()
        if not cookies:
            print("❌ No saved cookies. Run 'validate' first.")
            sys.exit(1)
        
        result = call_api(endpoint, cookies["auth_token"], cookies["ct0"])
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown action: {action}")

if __name__ == "__main__":
    main()
