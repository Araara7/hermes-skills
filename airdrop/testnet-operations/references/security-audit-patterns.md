# Security Audit: Scan for Leaked Secrets

## Quick Scan Commands

### Local Codebase
```bash
# Private keys
grep -r -E "0x[a-fA-F0-9]{64}" --include="*.py" --include="*.sh" --include="*.env" . | grep -v node_modules

# Seed phrases
grep -r -E "museum|length|cake|oven|wasp" --include="*.py" --include="*.md" . | grep -v node_modules

# API keys/tokens
grep -r -E "ghp_[a-zA-Z0-9]{36}|sk-[a-zA-Z0-9]{20,}" --include="*.py" --include="*.sh" .

# Generic secrets
grep -r -i -E "(private.?key|seed.?phrase|api.?key|secret.?key).?=.*['\"][a-zA-Z0-9]{20,}" .
```

### Git History
```bash
# All commits with .env files
git log --all --oneline -- "*.env" ".env" "*/.env"

# Deleted sensitive files
git log --all --diff-filter=D --name-only | grep -i -E "\.env|secret|credential|key|wallet|seed"

# Search patches for secrets
git log --all -p | grep -i -E "private.?key.*=.*['\"]0x|seed.*=.*['\"][a-z]+ [a-z]+"
```

### GitHub API
```bash
PAT="ghp_xxx"

# List repos
curl -s -H "Authorization: token $PAT" "https://api.github.com/user/repos?per_page=100"

# Search code for patterns
curl -s -H "Authorization: token $PAT" "https://api.github.com/search/code?q=PRIVATE_KEY+repo:user/repo"

# Get file content from specific commit
curl -s -H "Authorization: token $PAT" "https://api.github.com/repos/user/repo/commits/$SHA"
```

## Common Leak Vectors

1. **Hardcoded in scripts** - `PRIVATE_KEY = "0x..."` in .py files
2. **Committed .env files** - `.env` not in `.gitignore`
3. **Skill/reference files** - seed phrase in documentation
4. **Cron output logs** - seed phrase logged during execution
5. **Git history** - deleted files still in history
6. **PAT in config** - GitHub token in `.git/config`

## Real Incident: Seed Phrase Leak (2 June 2026)

**What happened:**
- Seed phrase was hardcoded in `jay_sudoku_solver.py` line 34
- Also found in skill reference file `sudoku-automation.md`
- Also found in cron output log `~/.hermes/cron/output/da3c85af0fef/2026-05-31_08-26-15.md`

**How it was found:**
```bash
grep -r "museum length cake oven wasp" ~/airdrop-agent/ ~/.hermes/ --include="*.py" --include="*.md"
```

**Fix applied:**
1. Changed `jay_sudoku_solver.py` to load from wallets.json:
```python
# BEFORE (INSECURE):
SEED_PHRASE = "museum length cake oven wasp..."

# AFTER (SECURE):
_wallets_path = Path.home() / "airdrop-agent" / "config" / "wallets.json"
with open(_wallets_path) as _f:
    SEED_PHRASE = json.load(_f)["master_seed"]
```

2. Removed seed from skill reference file
3. Deleted cron output containing seed
4. Deleted temp scripts in `/tmp/send_jay*.py`

**Lesson:** ALWAYS load secrets from wallets.json or .env. NEVER hardcode.

## Fix Checklist

- [ ] Remove hardcoded secrets from all files
- [ ] Load secrets from `wallets.json` or `.env` via `config_loader.py`
- [ ] `chmod 600` all credential files
- [ ] `.gitignore` includes `.env`, `wallets.json`, `credentials/`
- [ ] Rotate PAT if exposed
- [ ] Clean git history (force push or BFG Repo-Cleaner)
- [ ] Enable GitHub Secret Scanning on repos
- [ ] Check cron output logs for leaked secrets
- [ ] Check skill/reference files for hardcoded values
- [ ] Check temp files in `/tmp/` for secrets
