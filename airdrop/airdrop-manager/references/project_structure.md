# Airdrop Agent Project Structure

## Directory Layout
```
~/airdrop-agent/
├── README.md
├── .gitignore
├── venv/                    # Python virtual environment
├── config/
│   ├── settings.json        # Agent configuration
│   └── credentials/
│       ├── accounts.json    # Metadata (no secrets)
│       └── .env             # Secrets (chmod 600)
├── scripts/
│   ├── tracker.py           # Main tracking script
│   ├── wallet_deriver.py    # Wallet utilities
│   └── captcha_solver.py    # CAPTCHA automation
├── trackers/
│   └── README.md
├── logs/
├── data/
│   ├── wallets/             # Wallet data (encrypted)
│   ├── projects/            # Airdrop project files
│   ├── claims/              # Claim history
│   └── tokens/              # Extracted tokens
├── templates/
│   ├── project_template.md  # Template for new projects
│   └── dotenv_template      # .env template
└── screenshots/             # Task proof
```

## Setup Commands
```bash
# Create project
mkdir -p ~/airdrop-agent/{config/credentials,scripts,trackers,logs,data/{wallets,projects,claims,tokens},templates,screenshots}

# Create venv
cd ~/airdrop-agent
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install eth-account requests playwright

# Set permissions
chmod 600 config/credentials/*
chmod 700 config/credentials/
```

## Git Setup
```bash
cd ~/airdrop-agent
git init
echo "config/credentials/" >> .gitignore
echo "*.env" >> .gitignore
echo "data/wallets/" >> .gitignore
git add .
git commit -m "Initial airdrop agent setup"
```

## Security Notes
- `.env` file: chmod 600 (owner read/write only)
- `credentials/` dir: chmod 700 (owner access only)
- Never commit secrets to git
- Use `.gitignore` for sensitive dirs
