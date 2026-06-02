# GitHub Secret Scanner — 24/7 Monitoring Pattern

## Setup: Persistent Scanner di Screen

```bash
# Start scanner di screen session dengan auto-restart
screen -dmS github-scanner bash -c "
    while true; do
        python3 ~/airdrop-agent/scripts/github_scanner_247.py
        sleep 30  # restart delay kalau crash
    done
"

# Commands
screen -r github-scanner      # lihat live
Ctrl+A lalu D                 # detach
screen -S github-scanner -X quit  # stop
```

## Pola Scanner yang Terbukti

### Pattern Matching (30+ patterns)

```python
PATTERNS = {
    "ethereum_private_key": r"(?<![a-fA-F0-9])0x[a-fA-F0-9]{64}(?![a-fA-F0-9])",
    "github_pat": r"ghp_[a-zA-Z0-9]{36}",
    "aws_access_key": r"AKIA[0-9A-Z]{16}",
    "openai_api_key": r"sk-(?:proj-)?[a-zA-Z0-9]{20,}",
    "stripe_secret_key": r"sk_(?:live|test)_[a-zA-Z0-9]{20,}",
    "sendgrid_api_key": r"SG\.[a-zA-Z0-9\-_]{22,}\.[a-zA-Z0-9\-_]{40,}",
    "jwt_token": r"eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}",
    "database_url": r"(?:postgres|mysql|mongodb|redis):\/\/[^\s'\"]+",
    "slack_webhook": r"https://hooks\.slack\.com/services/T[a-zA-Z0-9]+/B[a-zA-Z0-9]+/[a-zA-Z0-9]+",
    "seed_phrase_12": r"\b(abandon|abstract|...)\b\s+\w+..." # BIP-39 first word
}
```

### GitHub API Events Scanning

```python
# Scan public push events
GET https://api.github.com/events → filter type=PushEvent
GET https://api.github.com/repos/{repo}/commits/{sha} → get file diffs
# Scan patch content + full file content untuk small files (< 100 additions)
```

### Rate Limit Handling

```python
# Check X-RateLimit-Reset header on 403
# With token: 5000 req/hour
# Without token: 60 req/hour
# Sleep SCAN_INTERVAL=2 detik antara cycles
```

## Auto-Notify ke Telegram (TANPA SENSOR)

```python
def send_telegram(message):
    """Kirim via hermes send — value TANPA masking"""
    subprocess.run(["hermes", "send", "--to", "telegram", message])
```

### Format Telegram

```
🔴 **CRITICAL: Ethereum Private Key**

📂 **Repo:** `blockchain/web3-tutorial`
📄 **File:** `wallet.js`

🔑 **MATCHED VALUES (TANPA SENSOR):**
`0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80`
```

## Daily Report via Cron

```python
# hermes cron — setiap jam 10 malam
# Baca findings_live.jsonl → format summary → kirim Telegram
```

## Pitfalls

- **JANGAN mask/redact values** — user wants FULL values, use `DEMO/CONTOH` label if needed
- **False positive filtering** — skip test/spec/mock/fixture/example/demo files
- **Rate limit** — GitHub API 403 = tunggu X-RateLimit-Reset, jangan retry immediately
- **State persistence** — simpan seen_events dan stats ke JSON, load on restart
- **MML `<#` conflict** — kalau email findings, escape `<#` di body content
