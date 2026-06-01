#!/usr/bin/env python3
"""
Telegram Auth Commands Handler
Usage: python telegram_auth.py <command> [args...]

Commands:
  auth <url>                    - Extract all auth data
  token <url>                   - Extract tokens only
  jwt <url>                     - Extract JWT
  cookie <url>                  - Export cookies
  login <url> <user> <pass>     - Login + extract
  status                        - Check all saved auth
  check <domain>                - Check specific domain auth
  refresh <domain>              - Refresh token
  clear <domain>                - Clear auth data
"""

import sys
import json
import time
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from camoufox.sync_api import Camoufox
    HAS_CAMOUFOX = True
except ImportError:
    HAS_CAMOUFOX = False

# Config
TOKENS_DIR = Path.home() / "airdrop-agent" / "data" / "tokens"
TOKENS_DIR.mkdir(parents=True, exist_ok=True)

def extract_auth_data(url, actions=None):
    """Extract auth data via background browser"""
    
    if not HAS_CAMOUFOX:
        return {"error": "Camoufox not installed"}
    
    captured = {
        "url": url,
        "tokens": [],
        "cookies": [],
        "localStorage": {},
        "timestamp": time.time()
    }
    
    def handle_request(request):
        headers = request.headers
        if "authorization" in headers:
            captured["tokens"].append({
                "type": "authorization",
                "value": headers["authorization"][:200],
                "url": request.url[:80]
            })
        for key in ["x-csrf-token", "x-auth-token", "x-api-key", "x-jwt"]:
            if key in headers:
                captured["tokens"].append({
                    "type": key,
                    "value": headers[key][:100],
                    "url": request.url[:80]
                })
    
    def handle_response(response):
        url = response.url
        if any(x in url.lower() for x in ['token', 'auth', 'session', 'login']):
            try:
                if 'json' in response.headers.get('content-type', ''):
                    body = response.json()
                    if isinstance(body, dict):
                        for key in ['token', 'access_token', 'jwt', 'refresh_token']:
                            if key in body:
                                captured["tokens"].append({
                                    "type": key,
                                    "value": body[key][:200],
                                    "url": url[:80]
                                })
            except:
                pass
    
    try:
        with Camoufox(headless=True) as browser:
            context = browser.new_context()
            page = context.new_page()
            
            page.on("request", handle_request)
            page.on("response", handle_response)
            
            page.goto(url)
            page.wait_for_load_state("networkidle")
            time.sleep(3)
            
            if actions:
                for action in actions:
                    if action["type"] == "click":
                        page.locator(action["selector"]).first.click()
                        time.sleep(action.get("wait", 2))
                    elif action["type"] == "fill":
                        page.locator(action["selector"]).first.fill(action["value"])
                        time.sleep(action.get("wait", 1))
            
            # Extract cookies
            captured["cookies"] = context.cookies()
            
            # Extract localStorage
            try:
                captured["localStorage"] = page.evaluate("""
                    () => {
                        const data = {};
                        for (let i = 0; i < localStorage.length; i++) {
                            const key = localStorage.key(i);
                            data[key] = localStorage.getItem(key);
                        }
                        return data;
                    }
                """)
            except:
                pass
            
            # Save
            domain = url.split("//")[1].split("/")[0].replace(".", "_")
            output_file = TOKENS_DIR / f"{domain}_auth.json"
            with open(output_file, "w") as f:
                json.dump(captured, f, indent=2)
            
            return captured
            
    except Exception as e:
        return {"error": str(e)}

def login_and_extract(url, username, password):
    """Login and extract auth data"""
    
    if not HAS_CAMOUFOX:
        return {"error": "Camoufox not installed"}
    
    captured = {
        "url": url,
        "tokens": [],
        "cookies": [],
        "localStorage": {},
        "timestamp": time.time()
    }
    
    try:
        with Camoufox(headless=True) as browser:
            context = browser.new_context()
            page = context.new_page()
            
            page.goto(url)
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            # Try to find login form
            email_input = page.locator('input[type="email"], input[type="text"], input[name*="email"], input[name*="user"]')
            password_input = page.locator('input[type="password"]')
            
            if email_input.count() > 0 and password_input.count() > 0:
                email_input.first.fill(username)
                password_input.first.fill(password)
                
                # Find and click submit
                submit = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")')
                if submit.count() > 0:
                    submit.first.click()
                    page.wait_for_load_state("networkidle")
                    time.sleep(3)
            
            # Extract after login
            captured["cookies"] = context.cookies()
            captured["url"] = page.url
            
            # Save
            domain = url.split("//")[1].split("/")[0].replace(".", "_")
            output_file = TOKENS_DIR / f"{domain}_auth.json"
            with open(output_file, "w") as f:
                json.dump(captured, f, indent=2)
            
            return captured
            
    except Exception as e:
        return {"error": str(e)}

def get_auth_status():
    """Get status of all saved auth"""
    files = list(TOKENS_DIR.glob("*_auth.json"))
    status = []
    
    for f in files:
        try:
            with open(f) as fh:
                data = json.load(fh)
            
            domain = f.stem.replace("_auth", "")
            token_count = len(data.get("tokens", []))
            cookie_count = len(data.get("cookies", []))
            timestamp = data.get("timestamp", 0)
            
            status.append({
                "domain": domain,
                "tokens": token_count,
                "cookies": cookie_count,
                "timestamp": timestamp
            })
        except:
            pass
    
    return status

def check_auth(domain):
    """Check auth for specific domain"""
    auth_file = TOKENS_DIR / f"{domain}_auth.json"
    
    if not auth_file.exists():
        return None
    
    with open(auth_file) as f:
        return json.load(f)

def clear_auth(domain):
    """Clear auth for specific domain"""
    auth_file = TOKENS_DIR / f"{domain}_auth.json"
    
    if auth_file.exists():
        auth_file.unlink()
        return True
    return False

def format_output(result, command):
    """Format output for Telegram"""
    
    if "error" in result:
        return f"❌ Error: {result['error']}"
    
    if command == "auth":
        output = "🔐 **Auth Data Extracted**\n\n"
        output += f"🌐 URL: `{result.get('url', 'N/A')}`\n\n"
        
        if result.get("tokens"):
            output += f"**Tokens:** {len(result['tokens'])} found\n"
            for t in result["tokens"][:5]:
                output += f"• `{t['type']}`: `{t['value'][:30]}...`\n"
        
        if result.get("cookies"):
            output += f"\n**Cookies:** {len(result['cookies'])} found\n"
        
        if result.get("localStorage"):
            output += f"**LocalStorage:** {len(result['localStorage'])} items\n"
        
        return output
    
    elif command == "token":
        if not result.get("tokens"):
            return "❌ No tokens found"
        
        output = "🔑 **Tokens**\n\n"
        for t in result["tokens"]:
            output += f"**{t['type']}:**\n`{t['value']}`\n\n"
        return output
    
    elif command == "jwt":
        jwt_tokens = [t for t in result.get("tokens", []) if "jwt" in t.get("type", "").lower() or t.get("value", "").startswith("eyJ")]
        if not jwt_tokens:
            return "❌ No JWT found"
        
        output = "🎫 **JWT Tokens**\n\n"
        for t in jwt_tokens:
            output += f"`{t['value']}`\n\n"
        return output
    
    elif command == "cookie":
        if not result.get("cookies"):
            return "❌ No cookies found"
        
        output = "🍪 **Cookies**\n\n"
        for c in result["cookies"]:
            output += f"• `{c['name']}`: `{c['value'][:30]}...`\n"
        return output
    
    elif command == "status":
        if not result:
            return "📭 No saved auth data"
        
        output = "📊 **Auth Status**\n\n"
        for s in result:
            output += f"• **{s['domain']}**: {s['tokens']} tokens, {s['cookies']} cookies\n"
        return output
    
    elif command == "check":
        if not result:
            return "❌ No auth data found"
        
        output = "🔍 **Auth Detail**\n\n"
        output += f"🌐 URL: `{result.get('url', 'N/A')}`\n"
        output += f"🔑 Tokens: {len(result.get('tokens', []))}\n"
        output += f"🍪 Cookies: {len(result.get('cookies', []))}\n"
        return output
    
    return json.dumps(result, indent=2)

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1]
    
    if command == "auth":
        if len(sys.argv) < 3:
            print("Usage: auth <url>")
            return
        url = sys.argv[2]
        print(f"🌐 Extracting auth from {url}...")
        result = extract_auth_data(url)
        print(format_output(result, "auth"))
    
    elif command == "token":
        if len(sys.argv) < 3:
            print("Usage: token <url>")
            return
        url = sys.argv[2]
        print(f"🔑 Extracting tokens from {url}...")
        result = extract_auth_data(url)
        print(format_output(result, "token"))
    
    elif command == "jwt":
        if len(sys.argv) < 3:
            print("Usage: jwt <url>")
            return
        url = sys.argv[2]
        print(f"🎫 Extracting JWT from {url}...")
        result = extract_auth_data(url)
        print(format_output(result, "jwt"))
    
    elif command == "cookie":
        if len(sys.argv) < 3:
            print("Usage: cookie <url>")
            return
        url = sys.argv[2]
        print(f"🍪 Exporting cookies from {url}...")
        result = extract_auth_data(url)
        print(format_output(result, "cookie"))
    
    elif command == "login":
        if len(sys.argv) < 5:
            print("Usage: login <url> <username> <password>")
            return
        url, username, password = sys.argv[2], sys.argv[3], sys.argv[4]
        print(f"🔐 Logging in to {url}...")
        result = login_and_extract(url, username, password)
        print(format_output(result, "auth"))
    
    elif command == "status":
        status = get_auth_status()
        print(format_output(status, "status"))
    
    elif command == "check":
        if len(sys.argv) < 3:
            print("Usage: check <domain>")
            return
        domain = sys.argv[2]
        result = check_auth(domain)
        print(format_output(result, "check"))
    
    elif command == "clear":
        if len(sys.argv) < 3:
            print("Usage: clear <domain>")
            return
        domain = sys.argv[2]
        if clear_auth(domain):
            print(f"✅ Auth cleared for {domain}")
        else:
            print(f"❌ No auth data for {domain}")
    
    else:
        print(f"❌ Unknown command: {command}")
        print(__doc__)

if __name__ == "__main__":
    main()
