---
name: airdrop-project-tracker
description: "Track semua airdrop project aktif — status, tasks, deadlines, earnings. Auto-manage dari satu tempat. Report ke user."
tags: [airdrop, tracker, project-management, automation]
---

# Airdrop Project Tracker

## When to Use
- User tanya "project apa aja yang aktif?"
- Daily briefing — compile status semua project
- New project ditemukan — tambah ke tracker
- Task selesai — update progress

## Data Structure
```
~/airdrop-agent/data/projects/
├── _index.json          ← master list semua project
├── jay-network/
│   ├── info.json        ← project metadata
│   ├── tasks.json       ← task list & status
│   └── api_endpoints.md ← discovered APIs
├── layerzero/
│   └── info.json
└── <project-name>/
    └── info.json
```

## Master Index (`_index.json`)
```json
{
  "projects": [
    {
      "name": "JAY Network",
      "slug": "jay-network",
      "status": "active",
      "type": "gaming+mining",
      "chain": "cosmos",
      "wallet": "yjay1...",
      "daily_earning": "33 JAY",
      "monthly_estimate": "990 JAY",
      "tasks_total": 3,
      "tasks_done": 2,
      "last_updated": "2026-05-31",
      "priority": "high",
      "notes": "Mining + Sudoku automation running"
    }
  ],
  "summary": {
    "total_projects": 1,
    "active": 1,
    "total_daily_earning": "~$X",
    "last_scan": "2026-05-31T08:00:00"
  }
}
```

## Project Info (`info.json`)
```json
{
  "name": "JAY Network",
  "slug": "jay-network",
  "url": "https://games.thejaynetwork.com",
  "type": "gaming+mining",
  "chain": "cosmos",
  "status": "active",
  "wallet": "yjay1aervdugs5rngpq3frszvtvsc6v6afwchatvnf6",
  "discovered": "2026-05-28",
  "airdrop_announced": false,
  "token": "JAY",
  "estimated_value": null,
  "scripts": ["jay_sudoku_solver.py"],
  "cron_jobs": ["jay-sudoku-auto", "jay-sudoku-auto-sore"],
  "api_base": "https://games.thejaynetwork.com",
  "auth_method": "cosmos-sign",
  "daily_earning": "33 JAY",
  "notes": "Mining 61 H/s + Sudoku 15 claims/day"
}
```

## Tasks (`tasks.json`)
```json
{
  "tasks": [
    {"id": 1, "task": "Mining 24/7", "status": "running", "auto": true},
    {"id": 2, "task": "Sudoku 15 claims/day", "status": "running", "auto": true},
    {"id": 3, "task": "Twitter verify", "status": "blocked", "reason": "OAuth broken server-side"},
    {"id": 4, "task": "Umbra email setup", "status": "pending"}
  ]
}
```

## Working Implementation
- Master index: `~/airdrop-agent/data/projects/_index.json`
- Project folders: `~/airdrop-agent/data/projects/<slug>/`
- Each project: `info.json` + `tasks.json`

### Current Projects (Jun 2026)
| Project | Status | Daily |
|---------|--------|-------|
| JAY Network | 🟢 Active | ~33 JAY |
| Galxe | 🟡 Auto-verify | 1 task/day (claim blocked by anti-bot) |
| Umbra | ⚠️ Pending setup | 0 |
| LayerZero | ✅ Completed | 0 |

### Commands

### Add New Project
```bash
mkdir -p ~/airdrop-agent/data/projects/<slug>
# Create info.json and tasks.json
```

### Update Status
```bash
# Edit _index.json to update project status
```

### Daily Report
```bash
# Read _index.json → compile summary → send to user
```

## Report Format
```
📊 AIRDROP PORTFOLIO — [DATE]

🟢 Active Projects:
1. JAY Network — Mining + Games
   💰 ~33 JAY/day | Tasks: 2/3 done
   ⚠️ Twitter verify blocked

2. [Project] — [Type]
   💰 $X/day | Tasks: X/X done

📈 Total Daily: ~$X
📅 Total Monthly: ~$X

⏳ Pending Tasks:
- [task 1]
- [task 2]
```

## Auto-Discovery Flow
1. Scan crypto news/Twitter for new airdrops
2. Check eligibility (chain, wallet, requirements)
3. Add to `_index.json` with status: "discovered"
4. Run API discovery → save endpoints
5. Create automation script
6. Set up cron if repeatable
7. Report to user

## Related Skills
- `airdrop-api-discovery` — find API endpoints
- `airdrop-wallet-connect` — connect wallet to platform
- `airdrop-manager` — master orchestrator
- `web3-airdrop-automation` — full automation
