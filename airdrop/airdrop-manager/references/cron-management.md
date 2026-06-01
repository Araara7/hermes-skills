# Cron Job Management Patterns

## Periodic Monitoring Pattern

For airdrop monitoring, use cron jobs with these schedules:

| Task Type | Schedule | Example |
|-----------|----------|---------|
| Email checks | Every 24h | Umbra verification code |
| Game farming | Every 6h | JAY Games chess |
| Token claims | Every 1h | When approaching deadline |
| Site monitoring | Every 30m | During active farming |

## Create Cron Job

```bash
# Via Hermes
hermes cron create \
  --name "task-name" \
  --schedule "every 24h" \
  --prompt "Self-contained task instructions" \
  --skills '["skill-name"]'
```

## Auto-Pause Pattern

For tasks that should stop if no results found:

```
Cron prompt:
"Check [EMAIL/TASK]. If NOT found:
- Report: 'No results after X hours'
- Add note: 'Job will be paused. Resume with /cron resume JOB_ID'"
```

## Resume Pattern

```
User: "Check Umbra again"
Agent: 
1. hermes cron resume JOB_ID
2. hermes cron run JOB_ID  # immediate check
```

## Job Management Commands

```bash
# List all jobs
hermes cron list

# Pause job
hermes cron pause JOB_ID

# Resume job
hermes cron resume JOB_ID

# Run immediately
hermes cron run JOB_ID

# Update schedule
hermes cron update JOB_ID --schedule "every 12h"

# Remove job
hermes cron remove JOB_ID
```

## Current Active Jobs (Otama Agent)

| Job ID | Name | Schedule | Purpose |
|--------|------|----------|---------|
| 9ee74f581400 | umbra-email-check | 24h | Check Umbra verification email |
| ce5fee11a94b | jay-chess-monitor | 6h | Play chess, farm UJAY |

## Delivery Targets

- `telegram` — default home channel
- `telegram:CHAT_ID` — specific chat
- `telegram:CHAT_ID:THREAD_ID` — specific topic/thread
- `local` — save only, no delivery
- `all` — fan out to all connected channels
