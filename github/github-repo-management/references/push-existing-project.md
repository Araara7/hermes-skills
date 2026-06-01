# Pushing Existing Local Project to GitHub

Workflow untuk push project yang sudah ada ke repo baru di GitHub.

## Pre-flight Checklist

1. **Auth check**: pastikan token Classic (bukan Fine-grained) — lihat pitfall di SKILL.md
2. **Gitignore**: review sebelum commit! Exclude:
   - `.env`, `config/credentials/`, `config/secrets.json`
   - `venv/`, `.venv/`, `__pycache__/`
   - `data/cookies/`, `data/screenshots/`, `screenshots/`
   - `*.key`, `*.pem`
3. **Cek staged files**: `git status` — pastikan tidak ada file sensitif

## Step-by-step

```bash
# 1. Init git
cd ~/project
git init
git config user.name "Username"
git config user.email "email@example.com"

# 2. Create repo via API (Classic token required!)
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user/repos \
  -d '{"name": "repo-name", "description": "desc", "private": false}'

# 3. Review .gitignore BEFORE adding
cat .gitignore

# 4. Stage & verify
git add -A
git status --short  # ← CRITICAL: review this output!

# 5. If sensitive files staged, unstage them
git rm -r --cached config/credentials/ data/cookies/ ...

# 6. Commit
git commit -m "🚀 Initial commit"

# 7. Push (use credential helper, not URL-embedded token)
git branch -M main
git remote add origin https://github.com/USER/REPO.git
git config --global credential.helper store
echo "https://USER:TOKEN@github.com" > ~/.git-credentials
git push -u origin main

# 8. Clean up .git-credentials after push
rm ~/.git-credentials
```

## Fallback: SSH Key (when HTTPS + PAT fails)

Even with a valid Classic token, git push can fail with:
```
remote: Invalid username or token. Password authentication is not supported for Git operations.
```

If credential helper + Classic token still fails after 2-3 attempts, switch to SSH:

```bash
# 1. Generate SSH key (if not exists)
ssh-keygen -t ed25519 -C "user@email.com" -f ~/.ssh/id_ed25519 -N ""

# 2. Add to GitHub via API
PUB_KEY=$(cat ~/.ssh/id_ed25519.pub)
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user/keys \
  -d "{\"title\": \"$(hostname)-vps\", \"key\": \"$PUB_KEY\"}"

# 3. If API add fails (404/token scope issue), tell user to add manually:
#    → https://github.com/settings/ssh/new
#    → Title: <hostname>-vps
#    → Key: paste ~/.ssh/id_ed25519.pub content

# 4. IMPORTANT: Add GitHub host key to known_hosts FIRST
ssh-keyscan github.com >> ~/.ssh/known_hosts

# 5. Switch remote to SSH
git remote set-url origin git@github.com:USER/REPO.git

# 6. Test & push
ssh -T git@github.com 2>&1 || true  # expect "Hi USER! You've..."
git push -u origin main
```

## Common Pitfalls

- **Fine-grained token on push**: "Bad credentials" → switch to Classic token
- **Classic token still fails**: Credential helper not working → try SSH key instead (see above)
- **Token in URL fails**: `https://user:***@github.com/...` sometimes fails with newer git → use credential helper or SSH
- **SSH key add via API 404**: Token may not have `admin:public_key` scope → tell user to add manually at https://github.com/settings/ssh/new
- **SSH "Host key verification failed"**: First time connecting to GitHub via SSH, host key not in known_hosts. Fix BEFORE pushing:
  ```bash
  ssh-keyscan github.com >> ~/.ssh/known_hosts
  ```
  Without this, `git push` via SSH will always fail with "Host key verification failed".
- **Gitignore not taking effect**: Files already tracked by git won't be affected by `.gitignore` changes. Must untrack first:
  ```bash
  git rm -r --cached config/credentials/ data/cookies/ screenshots/
  git add -A
  git status  # verify sensitive files are gone
  ```
  Common symptom: you add dirs to `.gitignore` but `git status` still shows them staged.
- **Sensitive files committed**: Always `git status` before committing. If accidentally pushed, use `git filter-branch` or `BFG Repo-Cleaner`
- **Branch name**: Default is `master`, rename to `main` with `git branch -M main`

## Encrypted Backup to Private GitHub Repo

Pattern for backing up sensitive project data (credentials, configs, session files) to a private GitHub repo using openssl encryption.

### When to Use
- User wants to migrate VPS but keep credentials/history
- Sensitive data excluded from main repo needs a backup strategy
- Data includes: credentials, cookies, screenshots, game logs, .env files

### Workflow

```bash
# 1. Create backup tarball (exclude large binary files if needed)
cd ~/project
tar -czf /tmp/backup.tar.gz \
  --ignore-failed-read \
  config/credentials/ \
  data/cookies/ \
  data/wallets/ \
  .env

# 2. Encrypt with openssl (AES-256-CBC, PBKDF2)
openssl enc -aes-256-cbc -salt -pbkdf2 \
  -in /tmp/backup.tar.gz \
  -out /tmp/backup_repo/backup-encrypted.tar.gz.enc \
  -pass pass:YOUR_PASSWORD

# 3. Create private repo (via API or web)
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user/repos \
  -d '{"name": "project-backup", "private": true, "auto_init": true}'

# 4. Push encrypted backup
cd /tmp/backup_repo
git init && git add -A && git commit -m "🔒 Backup $(date +%Y%m%d)"
git remote add origin git@github.com:USER/project-backup.git
git push -u origin main
```

### Restore on New VPS

```bash
# 1. Clone backup repo
git clone git@github.com:USER/project-backup.git
cd project-backup

# 2. Decrypt
openssl enc -aes-256-cbc -d -salt -pbkdf2 \
  -in backup-encrypted.tar.gz.enc \
  -out /tmp/backup.tar.gz \
  -pass pass:YOUR_PASSWORD

# 3. Extract to project directory
cd ~/project
tar -xzf /tmp/backup.tar.gz

# 4. Cleanup
rm /tmp/backup.tar.gz
```

### Important Notes
- **Always use `private` repo** for backup — it contains credentials!
- **Remember the password** — without it, backup is unrecoverable
- **Script it** — create `scripts/backup.sh` and `scripts/restore.sh` in the main repo
- **Gitignore the backup repo** — don't mix backup data into the main project repo
- Consider periodic backups via cron job (daily or weekly)
