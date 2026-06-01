#!/usr/bin/env python3
"""
Camoufox Helper - Anti-detect browser utilities
Usage: python camoufox_helper.py [test|intercept|login]
"""

import sys
import json
from pathlib import Path

def test_stealth():
    """Test if Camoufox passes bot detection"""
    from camoufox.sync_api import Camoufox
    
    print("🦊 Testing Camoufox stealth...")
    
    with Camoufox(headless=True) as browser:
        page = browser.new_page()
        page.goto("https://bot.sannysoft.com/")
        page.wait_for_load_state("networkidle")
        
        # Check key metrics
        webdriver = page.evaluate("navigator.webdriver")
        ua = page.evaluate("navigator.userAgent")
        
        print(f"✅ Webdriver: {webdriver} (should be False)")
        print(f"✅ User Agent: {ua[:60]}...")
        
        # Check for detection
        page.screenshot(path="stealth_test.png")
        print("📸 Screenshot saved: stealth_test.png")

def intercept_network(url, output_file="captured_tokens.json"):
    """Intercept network traffic and capture tokens"""
    from camoufox.sync_api import Camoufox
    
    captured = []
    
    def on_request(request):
        headers = request.headers
        if "authorization" in headers:
            captured.append({
                "type": "authorization",
                "value": headers["authorization"][:100],
                "url": request.url[:80]
            })
    
    def on_response(response):
        url = response.url
        if any(x in url for x in ["/token", "/auth", "/login"]):
            try:
                if "json" in response.headers.get("content-type", ""):
                    body = response.json()
                    for key in ["token", "access_token", "jwt"]:
                        if key in body:
                            captured.append({
                                "type": key,
                                "value": body[key][:100],
                                "url": url[:80]
                            })
            except:
                pass
    
    print(f"🌐 Intercepting: {url}")
    
    with Camoufox(headless=True) as browser:
        context = browser.new_context()
        page = context.new_page()
        
        page.on("request", on_request)
        page.on("response", on_response)
        
        page.goto(url)
        page.wait_for_load_state("networkidle")
        
        # Save captured
        with open(output_file, "w") as f:
            json.dump(captured, f, indent=2)
        
        print(f"💾 Captured {len(captured)} tokens → {output_file}")
        return captured

def main():
    if len(sys.argv) < 2:
        print("Usage: python camoufox_helper.py [test|intercept <url>]")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "test":
        test_stealth()
    elif action == "intercept":
        if len(sys.argv) < 3:
            print("Usage: python camoufox_helper.py intercept <url>")
            sys.exit(1)
        intercept_network(sys.argv[2])
    else:
        print(f"Unknown action: {action}")

if __name__ == "__main__":
    main()
