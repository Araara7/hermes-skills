# Gmail App Password Config for Himalaya

## Quick Setup

When Gmail App Password is already available (from `accounts.json` or `.env`), create config directly:

```toml
# ~/.config/himalaya/config.toml

[accounts.gmail]
email = "user@gmail.com"
display-name = "User Name"
default = true

backend.type = "imap"
backend.host = "imap.gmail.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "user@gmail.com"
backend.auth.type = "password"
backend.auth.raw = "xxxx xxxx xxxx xxxx"  # 16-char App Password

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.gmail.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "user@gmail.com"
message.send.backend.auth.type = "password"
message.send.backend.auth.raw = "xxxx xxxx xxxx xxxx"

# Gmail folder aliases (REQUIRED — Gmail uses non-standard names)
folder.aliases.inbox = "INBOX"
folder.aliases.sent = "[Gmail]/Sent Mail"
folder.aliases.drafts = "[Gmail]/Drafts"
folder.aliases.trash = "[Gmail]/Trash"
```

## Reading Credentials from accounts.json

When credentials are stored in `~/airdrop-agent/config/credentials/accounts.json`:

```json
{
  "email": {
    "address": "user@gmail.com",
    "app_password": "xxxx xxxx xxxx xxxx",
    "type": "gmail"
  }
}
```

Extract and create config:

```bash
EMAIL=$(jq -r '.email.address' ~/airdrop-agent/config/credentials/accounts.json)
PASS=$(jq -r '.email.app_password' ~/airdrop-agent/config/credentials/accounts.json)

cat > ~/.config/himalaya/config.toml << EOF
[accounts.gmail]
email = "$EMAIL"
display-name = "Otama Agent"
default = true

backend.type = "imap"
backend.host = "imap.gmail.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "$EMAIL"
backend.auth.type = "password"
backend.auth.raw = "$PASS"

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.gmail.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "$EMAIL"
message.send.backend.auth.type = "password"
message.send.backend.auth.raw = "$PASS"

folder.aliases.inbox = "INBOX"
folder.aliases.sent = "[Gmail]/Sent Mail"
folder.aliases.drafts = "[Gmail]/Drafts"
folder.aliases.trash = "[Gmail]/Trash"
EOF

chmod 600 ~/.config/himalaya/config.toml
```

## Verify

```bash
himalaya envelope list -a gmail -f INBOX --page-size 5
```

## Pitfalls

- `backend.auth.raw` — use `raw` not `cmd` when password is known directly
- `backend.auth.cmd` — use when password is in a secrets manager (`pass show email/imap`)
- Folder aliases are REQUIRED for Gmail — without them, Sent/Drafts/Trash operations fail silently
- `--page-size N` — correct flag (NOT `-n N` which is a search query)
