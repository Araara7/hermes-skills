# Anti-Bot Random Delays Pattern

## Delay Ranges (terbukti work untuk JAY Games)

| Action | Min (detik) | Max (detik) |
|--------|-------------|-------------|
| Antara moves | 1.5 | 4.0 |
| Sebelum claim | 3.0 | 8.0 |
| Antara games | 30 | 120 |
| Page load wait | 8 | 15 |
| Cooldown antara game | 3 | 10 |

## Implementation

```python
import random
import asyncio

# Simple delay
delay = random.uniform(1.5, 4.0)
await asyncio.sleep(delay)

# With label for logging
async def random_delay(min_sec, max_sec, label=""):
    delay = random.uniform(min_sec, max_sec)
    if label:
        print(f"  ⏱️ {label}: {delay:.1f}s")
    await asyncio.sleep(delay)

# Usage
await random_delay(1.5, 4.0, "Between moves")
await random_delay(30, 120, "Between games")
```

## Anti-Bot Best Practices

1. **Randomize timing** — Jangan gunakan delay statis
2. **Vary patterns** — Kadang cepat, kadang lambat
3. **Human-like pauses** — Tambahkan occasional longer pauses
4. **Session rotation** — Ganti browser context periodik
5. **Request spacing** — Min 1s antara API calls

## Background Play

```bash
# Pastikan Xvfb sudah running di :99
ps aux | grep Xvfb

# Run dengan DISPLAY=:99
cd ~/airdrop-agent && DISPLAY=:99 timeout 300 .venv/bin/python3 -u scripts/game.py

# Untuk long-running, pakai background
DISPLAY=:99 timeout 1800 .venv/bin/python3 -u scripts/game.py &
```

**Pitfall:** Output Python di-buffer. Pakai `-u` flag untuk unbuffered output.
