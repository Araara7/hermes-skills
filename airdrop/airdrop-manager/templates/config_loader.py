#!/usr/bin/env python3
"""
Secure config loader — reads ALL secrets from .env files, NEVER hardcodes keys.

Usage:
    from config_loader import get_config, get_key
    cfg = get_config()
    priv_key = get_key("wallet_private_key")

.env file search order:
    1. ./config/credentials/.env  (primary — credential files)
    2. ./.env                     (secondary — project root)

Security rules:
    - NEVER hardcode private keys, seed phrases, or API keys in scripts
    - ALWAYS use this module to load secrets
    - ALWAYS chmod 600 on .env files
    - ALWAYS .gitignore .env files
"""
import os
from pathlib import Path

def _find_env_files():
    """Find all .env files in priority order."""
    project_root = Path(__file__).parent
    candidates = [
        project_root / "config" / "credentials" / ".env",
        project_root / ".env",
    ]
    return [p for p in candidates if p.exists()]

def _parse_env_file(path: Path) -> dict:
    """Parse a .env file into a dict, skipping comments and empty lines."""
    config = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            # Skip placeholder values
            if value and not value.startswith("<") and value != "***" and "***" not in value:
                config[key] = value
    return config

def get_config() -> dict:
    """
    Load all config values from .env files.
    Returns a dict with friendly names mapped to env vars.
    Later files override earlier ones.
    """
    # Merge all .env files (later overrides earlier)
    raw = {}
    for env_path in _find_env_files():
        raw.update(_parse_env_file(env_path))

    # Also check environment variables (highest priority)
    for key in raw:
        env_val = os.environ.get(key)
        if env_val:
            raw[key] = env_val

    # Map to friendly names (lowercase keys)
    lower = {k.lower(): v for k, v in raw.items()}

    return {
        # Wallet
        "wallet_address": lower.get("new_wallet_address") or lower.get("wallet_address", ""),
        "wallet_private_key": lower.get("new_wallet_private_key") or lower.get("wallet_private_key", ""),
        # Galxe
        "galxe_wallet_key": lower.get("galxe_wallet_key", ""),
        # Pixie Chess
        "pixie_private_key": lower.get("pixie_private_key", ""),
        # Unicity
        "unicity_private_key": lower.get("unicity_private_key", ""),
        "unicity_seed_phrase": lower.get("unicity_seed_phrase", ""),
        # Email
        "gmail_user": lower.get("gmail_user", ""),
        "gmail_pass": lower.get("gmail_app_password", ""),
        # API Keys
        "twocaptcha_key": lower.get("twocaptcha_api_key", ""),
        "capsolver_key": lower.get("capsolver_api_key", ""),
        # Twitter
        "twitter_username": lower.get("twitter_username", ""),
    }

def get_key(name: str) -> str:
    """Get a single config value by friendly name."""
    return get_config().get(name, "")

def mask(value: str, show: int = 6) -> str:
    """Mask a sensitive value for safe logging."""
    if len(value) <= show + 4:
        return "(short)"
    return value[:show] + "..." + value[-4:]

if __name__ == "__main__":
    cfg = get_config()
    print("=== Config Loader — Loaded Values ===")
    for k, v in cfg.items():
        status = mask(v) if v else "(empty)"
        print(f"  {k}: {status}")
