---
name: web3-airdrop-agent
description: Manage web3 airdrop projects - tracking, task management, wallet organization, social media integration. Use when user wants to track airdrops, manage project lists, check deadlines, or coordinate multi-chain activities.
tags: [web3, airdrop, defi, crypto, tracking, twitter, xurl]
triggers:
  - "airdrop"
  - "track project"
  - "claim token"
  - "web3 task"
  - "defi airdrop"
  - "multi-chain"
---

# Web3 Airdrop Agent

Agent untuk mengelola project airdrop web3 - tracking, task management, wallet organization.

## Project Structure

Default location: `~/airdrop-agent/`

```
airdrop-agent/
├── config/
│   └── settings.json      # Konfigurasi agent
├── scripts/
│   └── tracker.py          # Helper scripts
├── trackers/               # Active tracking
├── logs/                   # Activity logs
├── data/
│   ├── wallets/            # Wallet info (SENSITIVE - .gitignore)
│   ├── projects/           # Project details per file
│   └── claims/             # Claim history
├── templates/
│   └── project_template.md # Template untuk project baru
└── screenshots/            # Bukti task
```

## Workflow

### 1. Tambah Project Baru
```
User: "Tambah project [NAMA]"
```
- Copy template dari `templates/project_template.md`
- Simpan ke `data/projects/[nama].md`
- Isi info dasar: chain, website, twitter, discord

### 2. Update Task Progress
```
User: "Update [NAMA] task [TASK_NAME]"
```
- Buka file project di `data/projects/`
- Update checklist task
- Update status (🟡/🟢/🔴)

### 3. Cek Deadline
```
User: "Cek deadline"
```
- Scan semua file di `data/projects/`
- Filter yang deadline < 7 hari
- Return list dengan priority (🔴/🟡/🟢)

### 4. List Projects
```
User: "List project"
```
- Return semua project dengan status

## Integration Points

### Twitter/X (via xurl skill)
- Follow project Twitter
- Monitor announcement
- Post thread tentang airdrop

### Browser Tools
- Interaksi dengan website project
- Claim process automation
- Screenshot bukti task

### Research (web_search, web_extract)
- Cek info project baru
- Verify legitimacy
- Check contract addresses

## Data Format

### Project File (`data/projects/[nama].md`)
```markdown
# [NAMA_PROJECT]

## Info
- **Chain:** [CHAIN]
- **Website:** [URL]
- **Twitter:** [URL]
- **Status:** 🟡 Active

## Tasks
- [ ] Task 1
- [x] Task 2

## Deadline
- **Claim:** [TANGGAL]
```

### Settings (`config/settings.json`)
```json
{
  "wallets": [],
  "notifications": { "telegram": true },
  "tracking": { "priority_chains": ["ethereum", "base", "arbitrum"] }
}
```

## Security Rules

1. **NEVER** store private keys in plaintext
2. **NEVER** commit wallet data to git
3. **ALWAYS** use .gitignore for sensitive data
4. **VERIFY** project legitimacy before engaging

## Common Chains
- Ethereum, Base, Arbitrum, Optimism, Polygon
- Solana, Avalanche, BSC
- L2s: zkSync, Starknet, Scroll, Linea

## Pitfalls

1. **Scam projects** - Selalu verify contract address dan official links
2. **Gas fees** - Factor gas cost ke ROI calculation
3. **Sybil detection** - Jangan pakai wallet pattern yang terdeteksi
4. **Deadline miss** - Set reminder untuk claim window
5. **Multi-wallet** - Track wallet mana yang dipakai project mana
