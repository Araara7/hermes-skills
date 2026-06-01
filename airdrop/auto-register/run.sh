#!/bin/bash
# Wrapper script untuk menjalankan auto-register

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$HOME/airdrop-agent/venv/bin/python"

# Cek apakah venv ada
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Virtual environment tidak ditemukan di ~/airdrop-agent/venv"
    echo "   Jalankan: python3 -m venv ~/airdrop-agent/venv && ~/airdrop-agent/venv/bin/pip install camoufox"
    exit 1
fi

# Jalankan script
if [ "$1" = "quick" ]; then
    shift
    $VENV_PYTHON "$SCRIPT_DIR/quick_register.py" "$@"
else
    $VENV_PYTHON "$SCRIPT_DIR/register.py" "$@"
fi
