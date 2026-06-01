# Mining Watchdog Pattern

Cron job template untuk monitor screen-based mining processes dengan auto-repair.

## Template Prompt (untuk cron job)

```
Mining Watchdog + Auto-Repair.

LANGKAH CEK:
1. Cek screen: `screen -ls | grep <SCREEN_NAME>`
2. Jika screen TIDAK ada → kirim alert langsung
3. Jika screen ada, capture output: `screen -S <SCREEN_NAME> -X hardcopy /tmp/watchdog.txt && tail -30 /tmp/watchdog.txt`
4. Analisa output:
   - Ada error keywords? (error, failed, killed, terminated, connection lost, Traceback, Exception)
   - Tidak ada activity baru (>20 menit)?

LANGKAH PERBAIKAN (jika error, JANGAN kill screen):
1. `cd <PROJECT_DIR> && git pull`
2. Kirim Ctrl+C: `screen -S <SCREEN_NAME> -X stuff $'\003'`
3. Tunggu 3 detik
4. Restart di screen yang sama: `screen -S <SCREEN_NAME> -X stuff "<START_COMMAND>\n"`
5. Tunggu 10 detik, verifikasi

REPORTING:
- 🟢 REPAIRED → kirim jika berhasil fix
- 🔴 GAGAL → kirim jika fix gagal
- ✅ OK → SILENT (jangan kirim apa-apa)
```

## Cron Config

```
schedule: every 15m
deliver: telegram:<chat_id>
enabled_toolsets: ["terminal", "file"]
```

## Key Principles

1. **Never kill the screen** — always work inside the existing session
2. **Ctrl+C to stop** — not `screen -X quit`
3. **git pull before restart** — get latest fixes
4. **Silent when OK** — no spam, only alert on problems
5. **Verify after fix** — check output after restart confirms activity
