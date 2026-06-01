---
name: web3-airdrop-automation
description: End-to-end web3 airdrop automation — account setup, task tracking, social verification, on-chain interaction, progress monitoring
tags: [airdrop, web3, defi, testnet, automation, twitter, wallet]
---

# 🚀 Web3 Airdrop Automation

Workflow lengkap untuk automate airdrop web3: dari setup akun sampai claim token.

## Setup Checklist

### 1. Akun yang Dibutuhkan
- [ ] Email (Gmail dengan App Password untuk IMAP)
- [ ] Twitter (auth_token + ct0 dari cookies)
- [ ] Discord (opsional, untuk role/verification)
- [ ] Wallet (EVM: MetaMask, Solana: Phantom)

### 2. Tools yang Dibutuhkan
- [ ] Camoufox (anti-detect browser)
- [ ] xvfb (virtual display untuk popup)
- [ ] eth-account (wallet management)
- [ ] requests (HTTP client)

### 3. File Structure
```
~/airdrop-agent/
├── config/credentials/
│   ├── .env              # Sensitive data
│   ├── accounts.json     # Status akun
│   └── wallet_*.json     # Wallet data
├── data/
│   ├── cookies/          # Browser cookies
│   ├── projects/         # Project tracking
│   └── tokens/           # Extracted tokens
├── scripts/
│   ├── browser_login.py  # Camoufox login
│   ├── twitter_tasks.py  # Twitter automation
│   └── tracker.py        # Progress tracking
└── screenshots/
```

## Workflow Per Project

### Step 1: Research
```python
# Search Twitter untuk project baru
search_queries = [
    "airdrop testnet",
    "new protocol airdrop",
    "DeFi incentivized testnet",
]
```

### Step 2: Daftar & Connect
1. Buka website project
2. Connect wallet (MetaMask/Sphere)
3. Complete Stage 0 / registration
4. Verifikasi social (Twitter, Discord)

### Step 3: Task Harian
- [ ] Daily check-in
- [ ] Social tasks (like, retweet, follow)
- [ ] On-chain tasks (swap, bridge, stake)
- [ ] Referral tasks

### Step 4: Monitor Progress
```python
# Track XP, rank, deadline
project_status = {
    "name": "Project Name",
    "xp": 1500,
    "rank": "Top 10%",
    "deadline": "2026-06-30",
    "tasks_completed": 15,
    "tasks_total": 20,
}
```

### Step 5: Claim
- Monitor TGE announcement
- Claim token saat available
- Bridge/swap jika perlu

## Twitter Automation

### Like & Retweet
```python
def like_tweet(tweet_id, cookies, headers):
    url = "https://api.x.com/1.1/favorites/create.json"
    resp = requests.post(url, cookies=cookies, headers=headers, 
                         json={"id": tweet_id})
    return resp.status_code == 200

def retweet(tweet_id, cookies, headers):
    url = f"https://api.x.com/1.1/retweets/{tweet_id}.json"
    resp = requests.post(url, cookies=cookies, headers=headers)
    return resp.status_code == 200
```

### Follow User
```python
def follow_user(user_id, cookies, headers):
    url = "https://api.x.com/1.1/friendships/create.json"
    resp = requests.post(url, cookies=cookies, headers=headers,
                         json={"user_id": user_id})
    return resp.status_code == 200
```

## Reporting

### Harian
```
📊 Laporan Harian Airdrop
========================
📅 Tanggal: 2026-05-28

🐦 Twitter:
   - Like: 5 tweets
   - Retweet: 3 tweets
   - Follow: 2 accounts

💰 Wallet:
   - Balance: 0.5 ETH
   - Transactions: 3

📋 Projects:
   - Unicity Quest: Stage 0 ✅
   - Project X: 75% complete
   - Project Y: baru daftar

⏰ Deadline:
   - Project X: 3 hari lagi
```

## Pitfalls

⚠️ **JANGAN:**
- Pakai satu IP untuk banyak wallet (sybil detection)
- Automate terlalu cepat (rate limit, ban)
- Share seed phrase / private key
- Skip Stage 0 (biasanya prerequisite)

✅ **LAKUKAN:**
- Delay random antar action (30-60 detik)
- Rotasi IP per wallet
- Track semua project di satu tempat
- Backup credentials
- Monitor deadline harian

## Referensi

- `references/twitter_cookies.md` — Twitter cookie extraction
- `skills/anti-ip-detection` — Proxy & fingerprinting
- `skills/auto-resolve-captcha` — CAPTCHA solving
- `skills/airdrop-manager` — Galxe API automation (`references/galxe-api.md`)
