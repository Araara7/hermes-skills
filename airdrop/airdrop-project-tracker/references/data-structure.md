# Project Tracker Data Structure

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
      "wallet": "yjay1aervdugs5rngpq3frszvtvsc6v6afwchatvnf6",
      "daily_earning": "~33 JAY",
      "monthly_estimate": "~990 JAY",
      "tasks_total": 4,
      "tasks_done": 2,
      "last_updated": "2026-05-31",
      "priority": "high",
      "automation": true,
      "notes": "Mining 61 H/s + Sudoku 15 claims/day"
    }
  ],
  "summary": {
    "total_projects": 3,
    "active": 1,
    "pending": 1,
    "completed": 1,
    "total_daily_earning": "~33 JAY",
    "last_scan": "2026-05-31T09:30:00"
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
  "token": "JAY",
  "scripts": ["jay_sudoku_solver.py"],
  "cron_jobs": ["jay-sudoku-auto", "jay-sudoku-auto-sore", "jay-mining-watchdog"],
  "api_base": "https://games.thejaynetwork.com",
  "api_type": "api.php",
  "auth_method": "cosmos-qr-confirm",
  "mining": {
    "hashrate": "~61 H/s",
    "screen": "Jay",
    "wallet": "yjay1s4m4ujrhuda6tmlh9u0jxafgutfjzup55srq0t",
    "daily_earning": "~29 JAY"
  },
  "games": {
    "active": "sudoku",
    "mode": "expert",
    "score": 3472,
    "claims_per_day": 15,
    "reward_per_claim": "0.25 JAY",
    "daily_earning": "~3.75 JAY",
    "cooldown": "330s"
  },
  "daily_earning_total": "~33 JAY"
}
```

## Tasks (`tasks.json`)
```json
{
  "tasks": [
    {"id": 1, "task": "Mining 24/7 (screen Jay)", "status": "running", "auto": true, "cron": "jay-mining-watchdog"},
    {"id": 2, "task": "Sudoku 15 claims/day", "status": "running", "auto": true, "cron": "jay-sudoku-auto"},
    {"id": 3, "task": "Twitter verify", "status": "blocked", "reason": "OAuth broken server-side", "auto": false},
    {"id": 4, "task": "Himalaya Umbra setup", "status": "pending", "reason": "Not configured in himalaya", "auto": false}
  ]
}
```
