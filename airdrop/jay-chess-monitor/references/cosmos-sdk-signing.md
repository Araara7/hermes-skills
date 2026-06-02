# JAY Network Cosmos SDK Transaction Signing

## Chain Info
- **Chain ID**: `thejaynetwork` (NOT `jaynetwork-1`)
- **Chain API**: `https://api-jayn.winnode.xyz`
- **Pool API**: `https://api-pool.winnode.xyz`
- **Mining**: `https://mining.thejaynetwork.com`
- **Denom**: `ujay` (1 JAY = 1,000,000 uJAY)
- **Cosmos SDK**: v0.38.19
- **App**: `jaynd` v1.1.0

## Wallet Derivation
```python
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes, Bech32Encoder
import hashlib

seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
bip44 = Bip44.FromSeed(seed_bytes, Bip44Coins.COSMOS)
acc = bip44.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)

# CRITICAL: Use RIPEMD160(SHA256(pubkey)) for address, NOT raw pubkey
pub_compressed = acc.PublicKey().RawCompressed().ToBytes()
ripemd_hash = hashlib.new('ripemd160', hashlib.sha256(pub_compressed).digest()).digest()
wallet_addr = Bech32Encoder.Encode('yjay', ripemd_hash)  # 43 chars, NOT 64
```

## Protobuf Encoding Helpers
```python
def varint(value):
    if value < 0:
        value = value & 0xFFFFFFFFFFFFFFFF
    out = []
    while value > 0x7F:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    out.append(value & 0x7F)
    return bytes(out)

def field_bytes(fn, data):
    if isinstance(data, str):
        data = data.encode()
    return varint((fn << 3) | 2) + varint(len(data)) + data

def field_varint(fn, val):
    return varint((fn << 3) | 0) + varint(val)
```

## Full Transaction Build + Sign + Broadcast
```python
import json, hashlib, base64, time, requests
import ecdsa

CHAIN_API = "https://api-jayn.winnode.xyz"
CHAIN_ID = "thejaynetwork"
DENOM = "ujay"
GAS_LIMIT = 200000
FEE_AMOUNT = 5000

# Get account info
r = requests.get(f"{CHAIN_API}/cosmos/auth/v1beta1/accounts/{FROM_WALLET}")
acc_info = r.json()["account"]
account_number = int(acc_info["account_number"])
sequence = int(acc_info["sequence"])

# MsgSend
coin = field_bytes(1, DENOM) + field_bytes(2, str(send_amount))
msg_send_value = field_bytes(1, FROM_WALLET) + field_bytes(2, TO_WALLET) + field_bytes(3, coin)
msg_any = field_bytes(1, "/cosmos.bank.v1beta1.MsgSend") + field_bytes(2, msg_send_value)

# TxBody
tx_body = field_bytes(1, msg_any)

# Fee
fee_coin = field_bytes(1, DENOM) + field_bytes(2, str(FEE_AMOUNT))
fee = field_bytes(1, fee_coin) + field_varint(2, GAS_LIMIT)

# PubKey — MUST be nested protobuf (field 1 wraps compressed pubkey)
# Existing tx shows: PubKey.value = 0a21 + 33 bytes
# This is: field 1 (0a), length 33 (21), then pubkey bytes
pubkey_inner = field_bytes(1, pub_compressed)
pub_any = field_bytes(1, "/cosmos.crypto.secp256k1.PubKey") + field_bytes(2, pubkey_inner)

# ModeInfo.Single(mode=SIGN_MODE_DIRECT=1)
mode_single_value = field_varint(1, 1)
mode_info = field_bytes(1, mode_single_value)

# SignerInfo
signer_info = field_bytes(1, pub_any) + field_bytes(2, mode_info) + field_varint(3, sequence)

# AuthInfo
auth_info = field_bytes(1, signer_info) + field_bytes(2, fee)

# SignDoc
sign_doc = field_bytes(1, tx_body) + field_bytes(2, auth_info) + field_bytes(3, CHAIN_ID) + field_varint(4, account_number)

# Sign — MUST be 64-byte compact (r+s), NOT 72-byte DER
sign_hash = hashlib.sha256(sign_doc).digest()
sk = ecdsa.SigningKey.from_string(priv_key_bytes, curve=ecdsa.SECP256k1)
sig_compact = sk.sign_digest(sign_hash, sigencode=ecdsa.util.sigencode_string)
r_val = sig_compact[:32]
s_val = sig_compact[32:]
# Ensure low-S (BIP-62)
s_int = int.from_bytes(s_val, 'big')
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
if s_int > n // 2:
    s_int = n - s_int
    s_val = s_int.to_bytes(32, 'big')
signature = r_val + s_val  # 64 bytes

# TxRaw
tx_raw = field_bytes(1, tx_body) + field_bytes(2, auth_info) + field_bytes(3, signature)
tx_b64 = base64.b64encode(tx_raw).decode()

# Broadcast
payload = {"tx_bytes": tx_b64, "mode": "BROADCAST_MODE_SYNC"}
r3 = requests.post(f"{CHAIN_API}/cosmos/tx/v1beta1/txs", json=payload, timeout=30)
result = r3.json()
tx_resp = result.get("tx_response", result)
# code 0 = success
```

## Critical Pitfalls

### 1. PubKey Encoding
❌ WRONG: `field_bytes(2, pub_compressed)` — raw bytes as Any.value
✅ CORRECT: `field_bytes(2, field_bytes(1, pub_compressed))` — nested protobuf field 1 wrapping pubkey

The existing tx on chain shows PubKey.value = `0a21022a4c6e...`
- `0a` = field 1, length-delimited
- `21` = 33 bytes (length of compressed pubkey)
- `022a4c6e...` = the actual pubkey bytes

### 2. Signature Format
❌ WRONG: 72-byte DER signature (ecdsa.util.sigencode_der)
✅ CORRECT: 64-byte compact signature (ecdsa.util.sigencode_string) with low-S normalization

### 3. Chain ID
❌ WRONG: `jaynetwork-1`
✅ CORRECT: `thejaynetwork`

### 4. Address Derivation
❌ WRONG: `Bech32Encoder.Encode('yjay', pub_compressed)` → 64 chars
✅ CORRECT: `Bech32Encoder.Encode('yjay', RIPEMD160(SHA256(pub_compressed)))` → 43 chars

### 5. TxBody Memo Field
Do NOT include empty memo field. Only include `field_bytes(1, msg_any)` in TxBody.
Existing tx body is 141 bytes (without memo), not 142 (with empty memo).

## API Endpoints
```bash
# Balance
curl "$CHAIN_API/cosmos/bank/v1beta1/balances/$WALLET"

# Account info (account_number, sequence)
curl "$CHAIN_API/cosmos/auth/v1beta1/accounts/$WALLET"

# Node info (chain_id, version)
curl "$CHAIN_API/cosmos/base/tendermint/v1beta1/node_info"

# Latest block
curl "$CHAIN_API/cosmos/base/tendermint/v1beta1/blocks/latest"

# TX status
curl "$CHAIN_API/cosmos/tx/v1beta1/txs/$TXHASH"
```
