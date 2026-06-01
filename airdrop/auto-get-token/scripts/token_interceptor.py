#!/usr/bin/env python3
"""
Network Token Interceptor
Usage: python token_interceptor.py <url> [--cookies cookies.json]
"""

import sys
import json
import time
from pathlib import Path

# Storage for captured tokens
captured_tokens = []
captured_requests = []

def handle_request(request):
    """Capture network requests"""
    url = request.url
    headers = request.headers
    
    # Log important requests
    if any(x in url.lower() for x in ['oauth', 'token', 'auth', 'login', 'session']):
        captured_requests.append({
            "url": url[:100],
            "method": request.method,
            "has_auth": "authorization" in headers
        })
    
    # Capture auth headers
    if "authorization" in headers:
        captured_tokens.append({
            "type": "authorization",
            "value": headers["authorization"][:100],
            "url": url[:80]
        })

def handle_response(response):
    """Capture response tokens"""
    url = response.url
    
    # Check for token endpoints
    if any(x in url.lower() for x in ['oauth', 'token', 'auth', 'session', 'callback']):
        try:
            if 'json' in response.headers.get('content-type', ''):
                body = response.json()
                if isinstance(body, dict):
                    for key in ['token', 'access_token', 'jwt', 'session_token', 'auth_token']:
                        if key in body:
                            captured_tokens.append({
                                "type": key,
                                "value": body[key][:100],
                                "url": url[:80]
                            })
        except:
            pass

def intercept(url, cookies_file=None):
    """Main interception function"""
    from camoufox.sync_api import Camoufox
    
    cookies = None
    if cookies_file:
        with open(cookies_file) as f:
            cookies = json.load(f)
    
    with Camoufox(headless=True) as browser:
        context = browser.new_context()
        
        if cookies:
            context.add_cookies(cookies)
        
        page = context.new_page()
        
        # Setup interception
        page.on("request", handle_request)
        page.on("response", handle_response)
        
        # Navigate
        page.goto(url)
        page.wait_for_load_state("networkidle")
        
        # Wait for dynamic content
        time.sleep(3)
    
    return {
        "tokens": captured_tokens,
        "requests": captured_requests
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python token_interceptor.py <url> [--cookies cookies.json]")
        sys.exit(1)
    
    url = sys.argv[1]
    cookies_file = None
    
    if "--cookies" in sys.argv:
        idx = sys.argv.index("--cookies")
        if idx + 1 < len(sys.argv):
            cookies_file = sys.argv[idx + 1]
    
    print(f"🔍 Intercepting tokens from: {url}")
    result = intercept(url, cookies_file)
    
    print(f"\n📊 Results:")
    print(f"   Tokens captured: {len(result['tokens'])}")
    print(f"   Requests logged: {len(result['requests'])}")
    
    for token in result['tokens']:
        print(f"\n🔑 {token['type']}:")
        print(f"   Value: {token['value'][:50]}...")
        print(f"   URL: {token['url'][:50]}")
