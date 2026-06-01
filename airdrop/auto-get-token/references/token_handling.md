# JWT & Token Handling Reference

## JWT Structure
```
header.payload.signature
```

### Header
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Payload
```json
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022,
  "exp": 1516242622
}
```

## Decode JWT (Python)
```python
import base64
import json

def decode_jwt(token):
    """Decode JWT without verification"""
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

# Check expiry
import time

def is_expired(token):
    """Check if JWT is expired"""
    decoded = decode_jwt(token)
    if not decoded or "exp" not in decoded:
        return True
    return decoded["exp"] < time.time()
```

## Token Storage
```python
import json
from pathlib import Path

def save_tokens(project, tokens):
    """Save tokens to encrypted file"""
    token_dir = Path.home() / "airdrop-agent" / "data" / "tokens"
    token_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = token_dir / f"{project}.json"
    with open(filepath, "w") as f:
        json.dump(tokens, f, indent=2)
    
    # Set permissions
    filepath.chmod(0o600)

def load_tokens(project):
    """Load tokens from file"""
    filepath = Path.home() / "airdrop-agent" / "data" / "tokens" / f"{project}.json"
    
    if not filepath.exists():
        return None
    
    with open(filepath) as f:
        return json.load(f)
```

## Common Token Locations

### Browser
- **localStorage**: `localStorage.getItem("token")`
- **Cookies**: `document.cookie`
- ** sessionStorage**: `sessionStorage.getItem("token")`

### Network Requests
- **Authorization header**: `Bearer <token>`
- **Custom headers**: `x-auth-token`, `x-api-key`
- **Query params**: `?token=<token>`

### API Responses
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

## Token Refresh Pattern
```python
def refresh_token(refresh_token, client_id, client_secret):
    """Refresh expired access token"""
    resp = requests.post("https://api.example.com/oauth/token", data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret
    })
    
    return resp.json()
```

## Best Practices

1. **Never store in plain text** - Use encryption
2. **Check expiry** - Refresh before use
3. **Rotate tokens** - Don't reuse old tokens
4. **Secure transmission** - HTTPS only
5. **Minimal scope** - Request only needed permissions
