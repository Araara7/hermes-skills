# Proxy Providers Reference

## Residential Proxies (Recommended for Airdrops)

| Provider | Price | Pool Size | Format |
|----------|-------|-----------|--------|
| Bright Data | $15/GB | 72M+ | HTTP/SOCKS5 |
| Smartproxy | $14/GB | 40M+ | HTTP/SOCKS5 |
| IPRoyal | $7/GB | 32M+ | HTTP/SOCKS5 |
| Oxylabs | $15/GB | 100M+ | HTTP/SOCKS5 |
| SOAX | $6.60/GB | 155M+ | HTTP/SOCKS5 |

## Datacenter Proxies (Cheaper, Less Reliable)

| Provider | Price | Format |
|----------|-------|--------|
| PacketStream | $1/GB | HTTP |
| Storm Proxies | $10/mo | HTTP |
| MyPrivateProxy | $2.39/proxy | HTTP/SOCKS5 |

## Free Proxies (NOT Recommended)

- Unreliable, slow, often blacklisted
- May log your traffic
- Use only for testing, never for real accounts

## Setup Example

```python
# Load proxies from file
import json

with open("config/proxies.json") as f:
    config = json.load(f)

proxies = config["proxies"]
```

## Proxy Format
```
http://user:pass@host:port
socks5://user:pass@host:port
http://host:port (no auth)
```

## Testing
```bash
# Test proxy
curl -x http://user:pass@proxy:8080 https://api.ipify.org

# Check IP
curl https://ipinfo.io
```

## Best Practices

1. **1 proxy per wallet** - Never reuse IP across accounts
2. **Residential > Datacenter** - Better for account safety
3. **Test before use** - Verify proxy works
4. **Rotate regularly** - Don't use same IP too long
5. **Match geo** - Use same country as account registration
