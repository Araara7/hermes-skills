# GitHub Secret Scanner (Educational / Defensive)

## Overview
Scanner yang monitor GitHub public events real-time untuk cari leaked secrets.
Sama seperti tools resmi: TruffleHog, GitGuardian, Gitleaks.

**LEGALITAS:**
- ✅ Scan public events = LEGAL (GitHub public API)
- ✅ Find patterns = LEGAL (security research)
- ✅ Clone public repos = LEGAL
- ⚠️ Exploit found secrets = ILLEGAL

## Architecture

```
GitHub Events API → Pattern Matcher → Report Findings
       ↓                  ↓                ↓
  Stream events    Regex patterns     Save to JSONL
  (real-time)      (private keys,     (findings.jsonl)
                    seeds, API keys)
```

## Patterns Scanned

| Pattern | Severity | Regex |
|---------|----------|-------|
| Ethereum Private Key | CRITICAL | `0x[a-fA-F0-9]{64}` |
| Seed Phrase (BIP-39) | CRITICAL | Word list matching |
| GitHub PAT | HIGH | `ghp_[a-zA-Z0-9]{36}` |
| AWS Access Key | HIGH | `AKIA[0-9A-Z]{16}` |
| Database URL | HIGH | `mysql/postgres/mongodb://...` |
| JWT Token | MEDIUM | `eyJ...eyJ...` |
| Generic API Key | MEDIUM | `api_key = "..."` |

## Deployment

### Script Location
```
~/airdrop-agent/scripts/github_secret_scanner.py
```

### Quick Test
```bash
cd ~/airdrop-agent
source venv/bin/activate
python3 scripts/github_secret_scanner.py --duration 60 --max-events 100
```

### 24/7 Service
```bash
sudo systemctl start github-scanner
sudo systemctl status github-scanner
tail -f ~/airdrop-agent/data/github_scanner/scanner.log
```

### Systemd Service File
Location: `/etc/systemd/system/github-scanner.service`

```ini
[Unit]
Description=GitHub Secret Scanner - Educational
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/airdrop-agent
ExecStart=/home/ubuntu/airdrop-agent/venv/bin/python3 /home/ubuntu/airdrop-agent/scripts/github_secret_scanner.py --duration 3600 --max-events 10000 --defensive
Restart=on-failure
RestartSec=10
StandardOutput=append:/home/ubuntu/airdrop-agent/data/github_scanner/scanner.log
StandardError=append:/home/ubuntu/airdrop-agent/data/github_scanner/scanner.log

[Install]
WantedBy=multi-user.target
```

## Output
- `~/airdrop-agent/data/github_scanner/findings.jsonl` — JSON Lines format
- `~/airdrop-agent/data/github_scanner/scanner.log` — Service logs
- `~/airdrop-agent/data/github_scanner/README.md` — Documentation

## Why Live Scan Finds 0 Secrets
1. GitHub Push Protection — blocks secrets before push
2. GitHub Secret Scanning — auto-detects and alerts
3. Developer awareness — most don't commit secrets anymore
4. Rate limits — can't scan fast enough

## Key Learning
User's wallet was drained because:
1. Seed phrase was hardcoded in script
2. Pushed to GitHub (public repo)
3. Attacker's bot detected within seconds
4. No Push Protection existed at that time

**Fix:** Always load from wallets.json, never hardcode.

## Educational Demo Data
Full demo findings with detailed explanations at:
- `~/airdrop-agent/data/github_scanner/findings_full.jsonl` — 12 findings with full code context
- `~/airdrop-agent/data/github_scanner/FINDINGS_README.md` — Human-readable breakdown
