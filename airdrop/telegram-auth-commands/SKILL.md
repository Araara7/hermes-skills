---
name: telegram-auth-commands
description: Telegram commands for extracting auth data — tokens, JWT, cookies, API keys via background browser
tags: [telegram, commands, auth, token, jwt, cookie, automation]
---

# 📱 Telegram Auth Commands

Command Telegram untuk extract dan manage authentication data.

## Command List

### 🔐 Auth Extraction

| Command | Deskripsi | Contoh |
|---------|-----------|--------|
| `/auth [url]` | Extract semua auth data | `/auth https://airdrop.example.com` |
| `/token [url]` | Extract token saja | `/token https://api.example.com` |
| `/jwt [url]` | Extract JWT | `/jwt https://app.example.com` |
| `/cookie [url]` | Export cookies | `/cookie https://twitter.com` |
| `/login [url] [user] [pass]` | Login + extract | `/login https://example.com user pass` |

### 🔍 Query Auth

| Command | Deskripsi | Contoh |
|---------|-----------|--------|
| `/auth-status` | Cek semua auth tersimpan | `/auth-status` |
| `/auth-check [domain]` | Cek auth specific domain | `/auth-check twitter` |
| `/auth-refresh [domain]` | Refresh token | `/auth-refresh twitter` |
| `/auth-clear [domain]` | Hapus auth | `/auth-clear example` |

### 📊 Data Extraction

| Command | Deskripsi | Contoh |
|---------|-----------|--------|
| `/extract [url] [type]` | Extract data tertentu | `/extract https://example.com api_keys` |
| `/scrape [url] [selector]` | Scrape data | `/scrape https://example.com .price` |
| `/api-discover [url]` | Discover API endpoints | `/api-discover https://example.com` |

## Implementation

### Command Handler

```python
def handle_auth_command(command, args):
    """Handle Telegram auth commands"""
    
    if command == "/auth":
        # Extract all auth data
        url = args[0]
        result = extract_auth_data(url)
        return format_auth_result(result)
    
    elif command == "/token":
        # Extract tokens only
        url = args[0]
        result = extract_auth_data(url)
        tokens = [t for t in result.get("tokens", [])]
        return format_tokens(tokens)
    
    elif command == "/jwt":
        # Extract JWT
        url = args[0]
        result = extract_auth_data(url)
        jwt_tokens = [t for t in result.get("tokens", []) if "jwt" in t["type"].lower() or t["value"].startswith("eyJ")]
        return format_jwt(jwt_tokens)
    
    elif command == "/cookie":
        # Export cookies
        url = args[0]
        result = extract_auth_data(url)
        cookies = result.get("cookies", [])
        return format_cookies(cookies)
    
    elif command == "/login":
        # Login and extract
        url, username, password = args[0], args[1], args[2]
        result = login_and_extract(url, username, password)
        return format_auth_result(result)
    
    elif command == "/auth-status":
        # Check all saved auth
        auth_dir = Path.home() / "airdrop-agent" / "data" / "tokens"
        files = list(auth_dir.glob("*_auth.json"))
        return format_auth_status(files)
    
    elif command == "/auth-check":
        # Check specific domain
        domain = args[0]
        auth_file = Path.home() / "airdrop-agent" / "data" / "tokens" / f"{domain}_auth.json"
        if auth_file.exists():
            with open(auth_file) as f:
                data = json.load(f)
            return format_auth_detail(data)
        return f"❌ No auth data for {domain}"
    
    elif command == "/auth-refresh":
        # Refresh token
        domain = args[0]
        # Re-extract auth
        url = get_url_for_domain(domain)
        result = extract_auth_data(url)
        return f"✅ Auth refreshed for {domain}"
    
    elif command == "/auth-clear":
        # Clear auth
        domain = args[0]
        auth_file = Path.home() / "airdrop-agent" / "data" / "tokens" / f"{domain}_auth.json"
        if auth_file.exists():
            auth_file.unlink()
            return f"✅ Auth cleared for {domain}"
        return f"❌ No auth data for {domain}"
```

### Format Output

```python
def format_auth_result(result):
    """Format auth result for Telegram"""
    output = "🔐 **Auth Data Extracted**\n\n"
    
    if result.get("tokens"):
        output += "**Tokens:**\n"
        for t in result["tokens"]:
            output += f"• `{t['type']}`: `{t['value'][:30]}...`\n"
    
    if result.get("cookies"):
        output += f"\n**Cookies:** {len(result['cookies'])} found\n"
    
    if result.get("localStorage"):
        output += f"**LocalStorage:** {len(result['localStorage'])} items\n"
    
    return output

def format_tokens(tokens):
    """Format tokens for Telegram"""
    output = "🔑 **Tokens**\n\n"
    for t in tokens:
        output += f"**{t['type']}:**\n`{t['value']}`\n\n"
    return output

def format_jwt(jwt_tokens):
    """Format JWT for Telegram"""
    output = "🎫 **JWT Tokens**\n\n"
    for t in jwt_tokens:
        output += f"`{t['value']}`\n\n"
    return output

def format_cookies(cookies):
    """Format cookies for Telegram"""
    output = "🍪 **Cookies**\n\n"
    for c in cookies:
        output += f"• `{c['name']}`: `{c['value'][:30]}...`\n"
    return output
```

## Workflow

### 1. Extract Auth (Background)

```python
# Command: /auth https://airdrop.example.com
# → Background browser
# → Extract tokens, cookies, JWT
# → Simpan ke file
# → Kirim summary ke Telegram
```

### 2. Use Auth (API)

```python
# Setelah extract, pakai API:
# /task https://airdrop.example.com complete_task
# → Load auth dari file
# → Pakai API dengan token
# → Kirim hasil ke Telegram
```

## File Storage

```
~/airdrop-agent/data/tokens/
├── twitter_auth.json
├── example_auth.json
├── umbra_auth.json
└── ...
```

## Checklist

- [ ] Command berfungsi
- [ ] Background execution
- [ ] Token tersimpan
- [ ] Output terformat
- [ ] Error handling

## Pitfalls

⚠️ **JANGAN:**
- Tampilkan full token di Telegram (security)
- Buka browser untuk setiap command
- Skip error handling

✅ **LAKUKAN:**
- Mask token (tampilkan 30 char pertama)
- Cache auth data
- Handle timeout/error
- Kirim summary saja
