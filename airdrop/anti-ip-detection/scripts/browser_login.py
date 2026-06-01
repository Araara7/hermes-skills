#!/usr/bin/env python3
"""
Browser Login Helper with Camoufox
Supports Google, Twitter, and generic OAuth flows
"""

import json
import time
from pathlib import Path
from camoufox.sync_api import Camoufox

COOKIES_DIR = Path.home() / "airdrop-agent" / "data" / "cookies"

def login_google(email, app_password):
    """Login to Google and save cookies"""
    
    print("🦊 Starting Camoufox for Google login...")
    
    with Camoufox(headless=True) as browser:
        context = browser.new_context()
        page = context.new_page()
        
        # Navigate to Google
        print("🌐 Navigating to Google login...")
        page.goto("https://accounts.google.com/signin")
        page.wait_for_load_state("networkidle")
        
        # Enter email
        print("📧 Entering email...")
        email_field = page.locator('input[type="email"]')
        email_field.fill(email)
        page.click('button:has-text("Next")')
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        # Enter password
        print("🔑 Entering password...")
        password_field = page.locator('input[type="password"]')
        password_field.fill(app_password)
        page.click('button:has-text("Next")')
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        
        # Check if login successful
        current_url = page.url
        if "myaccount.google.com" in current_url:
            print("✅ Google login berhasil!")
            
            # Save cookies
            cookies = context.cookies()
            cookies_file = COOKIES_DIR / "google_cookies.json"
            COOKIES_DIR.mkdir(parents=True, exist_ok=True)
            
            with open(cookies_file, "w") as f:
                json.dump(cookies, f, indent=2)
            print(f"💾 Cookies saved: {cookies_file}")
            
            return True, cookies
        else:
            print(f"❌ Login gagal. URL: {current_url}")
            return False, None

def use_cookies_for_site(cookies_file, target_url):
    """Use saved cookies to access a site"""
    
    print(f"🍪 Loading cookies from: {cookies_file}")
    
    with open(cookies_file) as f:
        cookies = json.load(f)
    
    with Camoufox(headless=True) as browser:
        context = browser.new_context()
        context.add_cookies(cookies)
        
        page = context.new_page()
        page.goto(target_url)
        page.wait_for_load_state("networkidle")
        
        return page.url, context.cookies()

if __name__ == "__main__":
    # Example usage
    COOKIES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Test with saved cookies
    cookies_file = COOKIES_DIR / "google_cookies.json"
    if cookies_file.exists():
        url, cookies = use_cookies_for_site(cookies_file, "https://mail.google.com")
        print(f"📍 URL: {url}")
        print(f"🍪 Cookies: {len(cookies)}")
    else:
        print("❌ No saved cookies found")
