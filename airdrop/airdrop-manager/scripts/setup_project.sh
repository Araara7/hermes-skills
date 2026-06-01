#!/bin/bash
# Airdrop Agent Initial Setup Script
# Usage: bash setup_project.sh

set -e

PROJECT_DIR="$HOME/airdrop-agent"

echo "🚀 Setting up Airdrop Agent..."

# Create directory structure
echo "📁 Creating directories..."
mkdir -p "$PROJECT_DIR"/{config/credentials,scripts,trackers,logs,data/{wallets,projects,claims,tokens},templates,screenshots}

# Create venv
echo "🐍 Creating Python virtual environment..."
cd "$PROJECT_DIR"
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install eth-account requests playwright

# Set permissions
echo "🔐 Setting permissions..."
chmod 600 "$PROJECT_DIR"/config/credentials/* 2>/dev/null || true
chmod 700 "$PROJECT_DIR"/config/credentials/

# Create .gitignore
echo "📝 Creating .gitignore..."
cat > "$PROJECT_DIR/.gitignore" << 'EOF'
# Protect sensitive data
config/credentials/
*.key
*.pem
*.env

# Wallet data
data/wallets/

# Logs
logs/*.log

# Virtual environment
venv/

# Python cache
__pycache__/
*.pyc

# OS files
.DS_Store
Thumbs.db
EOF

# Create README
echo "📄 Creating README..."
cat > "$PROJECT_DIR/README.md" << 'EOF'
# 🚀 Airdrop Agent

Agent otomatis untuk tracking dan manage airdrop web3.

## Quick Start
```bash
source venv/bin/activate
python3 scripts/tracker.py
```

## Structure
- `config/` - Configuration and credentials
- `scripts/` - Automation scripts
- `data/` - Project data and tokens
- `trackers/` - Active airdrop tracking
- `logs/` - Activity logs

## Security
- Credentials in `config/credentials/.env` (chmod 600)
- Never commit secrets to git
EOF

echo ""
echo "✅ Setup complete!"
echo ""
echo "📁 Project created at: $PROJECT_DIR"
echo ""
echo "📋 Next steps:"
echo "1. Edit config/credentials/.env with your credentials"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python3 scripts/tracker.py"
