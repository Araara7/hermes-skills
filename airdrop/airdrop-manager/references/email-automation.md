# Email Automation for Airdrop Agents

## Himalaya CLI Setup (Gmail)

### Prerequisites
- Gmail App Password (not regular password)
- Himalaya installed (`himalaya --version`)

### Config File
Location: `~/.config/himalaya/config.toml`

```toml
[accounts.gmail]
email = "your-email@gmail.com"
display-name = "Your Name"
default = true

backend.type = "imap"
backend.host = "imap.gmail.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "your-email@gmail.com"
backend.auth.type = "password"
backend.auth.raw = "your-app-password-here"

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.gmail.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "your-email@gmail.com"
message.send.backend.auth.type = "password"
message.send.backend.auth.raw = "your-app-password-here"

folder.aliases.inbox = "INBOX"
folder.aliases.sent = "[Gmail]/Sent Mail"
folder.aliases.drafts = "[Gmail]/Drafts"
folder.aliases.trash = "[Gmail]/Trash"
```

### Common Commands

```bash
# List emails
himalaya envelope list -a gmail -f INBOX --page-size 20

# Search by subject
himalaya envelope list -a gmail subject "umbra"

# Read email by ID
himalaya message read -a gmail 8

# Send email
echo "Body text" | cat << 'EOF' | himalaya template send -a gmail
From: your-email@gmail.com
To: recipient@example.com
Subject: Test

Body text here.
EOF
```

### Cron Integration Pattern

For periodic email monitoring, create cron jobs that:
1. Check for specific emails (airdrop confirmations, verification codes)
2. Extract relevant info (codes, links)
3. Report to user via Telegram

```
Cron prompt template:
"Check Gmail for [SPECIFIC_EMAIL_TYPE] using Himalaya.
1. Run: himalaya envelope list -a gmail -f INBOX --page-size 20
2. Search for [PATTERN]
3. If found: extract [DATA], report to user
4. If not found: report 'no new emails'"
```

## Pitfalls

### App Password vs OAuth
- **App Password**: Quick setup, works for IMAP/SMTP, no expiry
- **OAuth**: Full Google Workspace access, needs browser for initial auth
- For cron jobs: App Password is more reliable (no token refresh needed)

### Gmail Folder Names
- Gmail uses non-standard folder names: `[Gmail]/Sent Mail`
- Must configure `folder.aliases` in himalaya config
- Without aliases, save-to-Sent fails after SMTP delivery succeeds

### Search Syntax
- Himalaya search: `himalaya envelope list -a gmail subject "keyword"`
- NOT: `himalaya envelope list -a gmail -n 5` (invalid syntax)
- Use `--page-size N` for pagination

## Tested Setup (Otama Agent)
- Email: otamaagent7@gmail.com
- Auth: App Password (ryjb fmjb mcny rzbq)
- Config: ~/.config/himalaya/config.toml
- Status: ✅ Working (tested 2026-05-28)
