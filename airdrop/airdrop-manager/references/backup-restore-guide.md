# Backup & Restore Guide for Airdrop Agent

## Overview

Two-repo strategy:
- `airdrop-agent` (public) — Code, scripts, configs (no secrets)
- `airdrop-agent-backup` (private) — Encrypted credentials, data, skills

Password: stored by user, shared with agent for automation.

## Full Backup Script

```bash
#!/bin/bash
# backup-agent-data.sh [backup|restore]
set -e
REPO_NAME="airdrop-agent-backup"
ENCRYPT_FILE="backup-encrypted.tar.gz.enc"
BACKUP_TARGETS=(
    "$HOME/airdrop-agent/config/credentials"
    "$HOME/airdrop-agent/data/cookies"
    "$HOME/airdrop-agent/data/umbra"
    "$HOME/airdrop-agent/data/jay_games"
    "$HOME/airdrop-agent/data/projects"
    "$HOME/airdrop-agent/data/wallets"
    "$HOME/airdrop-agent/.env"
)

backup() {
    local BACKUP_DIR="/tmp/airdrop-agent-backup"
    rm -rf "$BACKUP_DIR" && mkdir -p "$BACKUP_DIR"
    tar -czf "$BACKUP_DIR/backup.tar.gz" --ignore-failed-read "${BACKUP_TARGETS[@]}" 2>/dev/null
    openssl enc -aes-256-cbc -salt -pbkdf2 \
        -in "$BACKUP_DIR/backup.tar.gz" \
        -out "$BACKUP_DIR/$ENCRYPT_FILE" \
        -pass pass:"$1"
    # Push to private repo
    cd /tmp && rm -rf "${REPO_NAME}"
    git clone "git@github.com:Araara7/${REPO_NAME}.git"
    cd "${REPO_NAME}"
    cp "$BACKUP_DIR/$ENCRYPT_FILE" .
    git add -A && git commit -m "🔒 Backup $(date +%Y%m%d_%H%M%S)" && git push origin main
    rm -rf "$BACKUP_DIR" "/tmp/${REPO_NAME}"
}

restore() {
    cd /tmp && rm -rf "${REPO_NAME}"
    git clone "git@github.com:Araara7/${REPO_NAME}.git"
    cd "${REPO_NAME}"
    openssl enc -aes-256-cbc -d -salt -pbkdf2 \
        -in "$ENCRYPT_FILE" -out "/tmp/backup.tar.gz" \
        -pass pass:"$1"
    cd / && tar -xzf "/tmp/backup.tar.gz"
    rm -f "/tmp/backup.tar.gz" && rm -rf "/tmp/${REPO_NAME}"
}
```

## Skills Backup

Skills live in `~/.hermes/skills/` — NOT in the airdrop-agent project.

```bash
# Backup all skills
cd /tmp && cp -r ~/.hermes/skills skills_backup
tar -czf skills_all_backup.tar.gz skills_backup/
openssl enc -aes-256-cbc -salt -pbkdf2 -in skills_all_backup.tar.gz \
    -out skills-all-encrypted.tar.gz.enc -pass pass:$PASSWORD
# Push to backup repo

# Restore skills
openssl enc -aes-256-cbc -d -salt -pbkdf2 -in skills-all-encrypted.tar.gz.enc \
    -out /tmp/skills.tar.gz -pass pass:$PASSWORD
cd / && tar -xzf /tmp/skills.tar.gz
cp -r /tmp/skills_backup/* ~/.hermes/skills/
```

## VPS Migration Checklist

1. Generate SSH key → add to GitHub
2. `git clone git@github.com:user/airdrop-agent.git`
3. Restore encrypted backup (credentials + data)
4. Restore encrypted skills
5. Setup Python venv: `python3 -m venv venv && source venv/bin/activate`
6. Install deps: `pip install -r requirements.txt` (if exists)
7. Setup cron jobs (import from Hermes config)
8. Verify: `screen -ls`, check mining, test API calls

## Quick-Restore Script (1 Command VPS Setup)

Create `scripts/quick-restore.sh` in the main repo. This handles everything:
1. Install dependencies (git, python3, openssl, xvfb)
2. Generate SSH key + prompt user to add to GitHub
3. Clone main repo + backup repo
4. Decrypt & restore credentials/data
5. Decrypt & restore all skills to ~/.hermes/skills/
6. Setup Python venv
7. Cleanup temp files

User only needs to:
```bash
git clone git@github.com:USER/airdrop-agent.git && \
chmod +x ~/airdrop-agent/scripts/quick-restore.sh && \
bash ~/airdrop-agent/scripts/quick-restore.sh
```

Then: paste SSH key to GitHub, enter decryption password once, done.

## Jay-Miner Backup

Third-party mining tools (like jay-miner from `reiyuura/jay-miner`) have local config that needs backup:
```bash
# Backup miner config
cd /tmp && mkdir jay_backup
cp ~/jay-miner/.env jay_backup/
cp -r ~/jay-miner/logs jay_backup/ 2>/dev/null
tar -czf jay_backup.tar.gz jay_backup/
openssl enc -aes-256-cbc -salt -pbkdf2 -in jay_backup.tar.gz \
    -out jay-miner-encrypted.tar.gz.enc -pass pass:$PASSWORD
# Push to backup repo
```

Restore: clone original repo → copy .env back → install deps → start in screen.

## Skills Auto-Sync Cron

Set up a cron job to auto-backup skills daily:
```
name: skills-backup-sync
schedule: 0 10 * * *
deliver: telegram:<chat_id>
enabled_toolsets: ["terminal", "file"]
```

Prompt pattern:
1. `cp -r ~/.hermes/skills /tmp/skills_backup`
2. `tar -czf /tmp/skills.tar.gz /tmp/skills_backup/`
3. `openssl enc -aes-256-cbc -salt -pbkdf2 -in /tmp/skills.tar.gz -out /tmp/skills-encrypted.tar.gz.enc -pass pass:PASSWORD`
4. Clone backup repo, replace encrypted file, push
5. Cleanup temp files
6. Report: skills count, size, synced/no-changes

Result: skills always backed up within 24h of any change.

## Critical: ssh-keyscan for GitHub

Always add GitHub host key before first SSH connection:
```bash
ssh-keyscan github.com >> ~/.ssh/known_hosts 2>/dev/null
```
Without this, all git SSH operations fail with "Host key verification failed".
