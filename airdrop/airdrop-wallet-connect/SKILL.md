---
name: airdrop-wallet-connect
description: "Template: connect wallet ke platform airdrop — Cosmos, EVM, Solana signing. Tested patterns untuk JAY, EVM, dan generic web3."
tags: [airdrop, wallet, connect, cosmos, evm, signing]
---

# Airdrop Wallet Connect Templates

## When to Use
- New platform butuh wallet auth
- Script wallet connect rusak
- Mau tambah support chain baru

## Cosmos SDK (JAY Network)

### Derive Wallet from Seed
```python
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes, Bech32Encoder
import hashlib

SEED = "your seed phrase here"
PREFIX = "yjay"  # chain prefix

seed_bytes = Bip39SeedGenerator(SEED).Generate()
bip44 = Bip44.FromSeed(seed_bytes, Bip44Coins.COSMOS)
acc = bip44.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)

# CORRECT: RIPEMD160(SHA256(pubkey)) — 43 chars
pub_bytes = acc.PublicKey().RawCompressed().ToBytes()
sha_hash = hashlib.sha256(pub_bytes).digest()
ripemd_hash = hashlib.new('ripemd160', sha_hash).digest()
wallet = Bech32Encoder.Encode(PREFIX, ripemd_hash)

priv_key = bytes.fromhex(acc.PrivateKey().Raw().ToHex())
```

### Sign Message (Cosmos Amino)
```python
import json, base64
from ecdsa import SECP256k1, SigningKey

def cosmos_sign(message, priv_key, wallet, pub_key_b64):
    data_b64 = base64.b64encode(message.encode()).decode()
    sign_doc = {
        "account_number": "0", "chain_id": "", 
        "fee": {"amount": [], "gas": "0"}, "memo": "",
        "msgs": [{"type": "sign/MsgSignData", "value": {"data": data_b64, "signer": wallet}}],
        "sequence": "0"
    }
    sign_json = json.dumps(sign_doc, separators=(',', ':'))  # NO sort_keys!
    msg_hash = hashlib.sha256(sign_json.encode()).digest()
    sk = SigningKey.from_string(priv_key, curve=SECP256k1)
    sig = sk.sign_digest(msg_hash, sigencode=lambda r, s, order: r.to_bytes(32, 'big') + s.to_bytes(32, 'big'))
    return base64.b64encode(sig).decode()
```

### QR Confirm Flow (JAY Games pattern)
```python
import requests

def connect_qr(session, wallet, site):
    # 1. Create QR session
    r = session.post(f"{site}/api.php?api=qr_create")
    sid = r.json()["session_id"]
    
    # 2. Confirm with wallet
    r = session.post(f"{site}/api.php?api=qr_confirm", 
                     json={"session_id": sid, "wallet": wallet})
    
    # 3. Poll for connection
    for _ in range(10):
        r = session.get(f"{site}/api.php?api=qr_status&session_id={sid}")
        if r.json().get("status") == "connected":
            return True
        time.sleep(2)
    return False
```

## EVM (Ethereum/BNB/Arbitrum)

### Sign Message (EIP-191)
```python
from eth_account import Account
from eth_account.messages import encode_defunct

def evm_sign(message, private_key):
    msg = encode_defunct(text=message)
    signed = Account.sign_message(msg, private_key)
    return signed.signature.hex()
```

### Connect to dApp
```python
def evm_connect(session, wallet, site):
    # Get nonce/challenge
    r = session.get(f"{site}/api/auth/nonce?address={wallet}")
    nonce = r.json()["nonce"]
    
    # Sign nonce
    signature = evm_sign(f"Sign this message: {nonce}", PRIVATE_KEY)
    
    # Verify
    r = session.post(f"{site}/api/auth/verify", 
                     json={"address": wallet, "signature": signature})
    return r.json().get("success", False)
```

## 🔐 Key Management Security (CRITICAL)

**Incident (1 Jun 2026):** Wallet `0xb01E...de3E` compromised — private key stored in plain text across multiple script files. Attacker deployed auto-sweeper, drained all chains. Lesson learned the hard way.

### Rules (WAJIB IKUTI)
1. **NEVER store private key in script source code** — use environment variables or encrypted config
2. **NEVER store private key in `/tmp/` files** — world-readable on shared VPS
3. **Config files with secrets → chmod 600** — `~/airdrop-agent/config/credentials/` only
4. **Use `wallet_module.py` as single source** — derive keys from encrypted seed, don't copy keys into scripts
5. **Audit key exposure regularly** — `grep -r "private_key\|priv_key\|0x[0-9a-f]\{64\}" ~/airdrop-agent/scripts/`
6. **Separate hot wallet from cold wallet** — farming wallet (small amounts) ≠ storage wallet (bulk funds)
7. **Auto-sweep incoming funds** — if wallet is hot, sweep to cold wallet immediately on deposit

### Encrypted Key Storage Pattern
```python
import os, json
from cryptography.fernet import Fernet

# Store encrypted
key = Fernet.generate_key()
f = Fernet(key)
encrypted = f.encrypt(json.dumps({"seed": "your seed"}).encode())
# Save: key → env var WALLET_ENC_KEY, encrypted → config/credentials/wallet.enc

# Load decrypted
seed = json.loads(f.decrypt(encrypted).decode())["seed"]
```

### Auto-Sweeper Pattern (Defensive)
Monitor wallet 24/7, sweep incoming funds to cold wallet:
```python
from web3 import Web3
# Poll for new blocks, check balance, if > threshold → sweep to cold wallet
# Use nonce management to avoid race conditions with attacker
```

### Key Exposure Audit Command
```bash
# Find any plaintext keys in project
grep -rn "private_key\|priv_key\|seed_phrase\|mnemonic" ~/airdrop-agent/scripts/ ~/airdrop-agent/config/ --include="*.py" --include="*.json" --include="*.sh" | grep -v "encrypted\|\.enc\|chmod"
```

## Pitfalls
- ⚠️ **Cosmos pubkey**: must be base64 string, NOT `{"type": "tendermint/PubKeySecp256k1", "value": "..."}` object
- ⚠️ **Cosmos signing**: `separators=(',', ':')` but `sort_keys=False`
- ⚠️ **Wallet address**: RIPEMD160(SHA256(pubkey)) = 43 chars, NOT raw pubkey = 64 chars
- ⚠️ **Cosmos address regex**: `/^yjay1[a-z0-9]{38}$/` — server validates this
- ⚠️ **Session**: use `requests.Session()` to persist cookies
- ⚠️ **EVM**: different chains have different message formats
- ⚠️ **Solana**: `Keypair.from_bytes(priv_key)` fails with "expected 64 bytes" — use `Keypair.from_seed(priv_key)` instead (32 bytes)
- ⚠️ **API endpoints**: `/api/` REST endpoints may be dead — try `api.php` instead (older sites still use it)
- ⚠️ **Solana**: use `Keypair.from_seed()` not `Keypair.from_bytes()` (needs 32 bytes seed, not 64 bytes keypair)

## Working Implementation
Script: `~/airdrop-agent/scripts/wallet_module.py`
Config: `~/airdrop-agent/config/wallets.json` (chmod 600)
Packages: `pip install bip_utils ecdsa eth-account solana solders base58`

### Quick Usage
```python
from wallet_module import derive_all, cosmos_sign, evm_sign, solana_sign

# Get all wallets
wallets = derive_all()
# wallets["cosmos"]["address"]  → yjay1aervd...
# wallets["evm"]["address"]     → 0xb01Eaede...
# wallets["solana"]["address"]  → D98Jh6rr2gtc...
```

### CLI Test
```bash
cd ~/airdrop-agent && .venv/bin/python3 scripts/wallet_module.py addresses
cd ~/airdrop-agent && .venv/bin/python3 scripts/wallet_module.py sign all
```

### Addresses (from single seed in wallets.json)
- Cosmos (JAY): `yjay1aervdugs5rngpq3frszvtvsc6v6afwchatvnf6`
- EVM (OLD): `0xb01Eaede24ad33b820f8c1bD35eA9324230Ede3E` ← **COMPROMISED — DO NOT USE**
- EVM (CURRENT): `0x000A5c7AC1963a890796D3E8f823AFcB28f4c55A` (user-created, primary farming wallet)
- Solana: `D98Jh6rr2gtcTmn2knzzcCfqmDwZtvMJHujw5xe1iPKP`

### EVM Key Derivation from Seed
Derive EVM private key from `wallets.json` master seed using BIP44:
```python
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
import json

with open("config/wallets.json") as f:
    cfg = json.load(f)
seed_bytes = Bip39SeedGenerator(cfg["master_seed"]).Generate()
bip44 = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
acc = bip44.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
priv_key = acc.PrivateKey().Raw().ToHex()  # 64 hex chars
address = acc.PublicKey().ToAddress()       # 0x...
```

### Config Loader
All scripts MUST load keys via `config_loader.py`, never hardcode. Template: `airdrop-manager` skill → `templates/config_loader.py`. Usage:
```python
from config_loader import get_key
PRIV_KEY = get_key("wallet_private_key")  # from .env
```

## Related Skills
- `airdrop-api-discovery` — find the endpoints first
- `testnet-operations` — on-chain transactions
- `web3-airdrop-automation` — full automation
