# Cosmos SDK TX Signing (Protobuf)

## Critical Pitfalls

Two encoding issues that cause `invalid length: tx parse error`:

### 1. PubKey Must Be Nested Protobuf

WRONG (raw bytes):
```python
pub_any = field_bytes(1, "/cosmos.crypto.secp256k1.PubKey") + field_bytes(2, pub_compressed)
```

CORRECT (nested field 1 wrapping):
```python
pubkey_inner = field_bytes(1, pub_compressed)  # 0a21 + 33 bytes
pub_any = field_bytes(1, "/cosmos.crypto.secp256k1.PubKey") + field_bytes(2, pubkey_inner)
```

The PubKey Any's value field must contain a protobuf message with field 1 = raw compressed pubkey bytes.

### 2. Signature Must Be 64-Byte Compact (Not DER)

WRONG (72-byte DER):
```python
sig_der = sk.sign_digest(sign_hash, sigencode=ecdsa.util.sigencode_der)
tx_raw = field_bytes(1, tx_body) + field_bytes(2, auth_info) + field_bytes(3, sig_der)
```

CORRECT (64-byte compact with low-S):
```python
sig_compact = sk.sign_digest(sign_hash, sigencode=ecdsa.util.sigencode_string)
r_val = sig_compact[:32]
s_val = sig_compact[32:]
s_int = int.from_bytes(s_val, 'big')
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
if s_int > n // 2:
    s_int = n - s_int
    s_val = s_int.to_bytes(32, 'big')
signature = r_val + s_val  # 64 bytes exactly
```

## Working Example (JAY Network)

Chain: `thejaynetwork`, API: `https://api-jayn.winnode.xyz`

```python
import json, hashlib, base64, requests
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes, Bech32Encoder
import ecdsa

def varint(value):
    if value < 0: value = value & 0xFFFFFFFFFFFFFFFF
    out = []
    while value > 0x7F:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    out.append(value & 0x7F)
    return bytes(out)

def field_bytes(fn, data):
    if isinstance(data, str): data = data.encode()
    return varint((fn << 3) | 2) + varint(len(data)) + data

def field_varint(fn, val):
    return varint((fn << 3) | 0) + varint(val)

# MsgSend
coin = field_bytes(1, DENOM) + field_bytes(2, str(send_amount))
msg_send_value = field_bytes(1, FROM) + field_bytes(2, TO) + field_bytes(3, coin)
msg_any = field_bytes(1, "/cosmos.bank.v1beta1.MsgSend") + field_bytes(2, msg_send_value)

# TxBody (NO memo field unless non-empty)
tx_body = field_bytes(1, msg_any)

# Fee
fee_coin = field_bytes(1, DENOM) + field_bytes(2, str(FEE_AMOUNT))
fee = field_bytes(1, fee_coin) + field_varint(2, GAS_LIMIT)

# PubKey (NESTED!)
pubkey_inner = field_bytes(1, pub_compressed)
pub_any = field_bytes(1, "/cosmos.crypto.secp256k1.PubKey") + field_bytes(2, pubkey_inner)

# ModeInfo.Single + SignerInfo
mode_info = field_bytes(1, field_varint(1, 1))
signer_info = field_bytes(1, pub_any) + field_bytes(2, mode_info) + field_varint(3, sequence)

# AuthInfo
auth_info = field_bytes(1, signer_info) + field_bytes(2, fee)

# SignDoc → Sign
sign_doc = field_bytes(1, tx_body) + field_bytes(2, auth_info) + field_bytes(3, CHAIN_ID) + field_varint(4, account_number)
sign_hash = hashlib.sha256(sign_doc).digest()

# 64-byte compact signature (NOT DER!)
sk = ecdsa.SigningKey.from_string(priv_key_bytes, curve=ecdsa.SECP256k1)
sig = sk.sign_digest(sign_hash, sigencode=ecdsa.util.sigencode_string)
r_val, s_val = sig[:32], sig[32:]
s_int = int.from_bytes(s_val, 'big')
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
if s_int > n // 2: s_int = n - s_int
signature = r_val + s_int.to_bytes(32, 'big')

# TxRaw → Broadcast
tx_raw = field_bytes(1, tx_body) + field_bytes(2, auth_info) + field_bytes(3, signature)
tx_b64 = base64.b64encode(tx_raw).decode()
r = requests.post(f"{CHAIN_API}/cosmos/tx/v1beta1/txs", json={"tx_bytes": tx_b64, "mode": "BROADCAST_MODE_SYNC"})
```

## Debug: Analyze Existing TX Format

To understand a chain's exact encoding, parse an existing tx:
```python
# Get latest block txs
r = requests.get(f"{CHAIN_API}/cosmos/base/tendermint/v1beta1/blocks/latest")
height = r.json()["block"]["header"]["height"]
r2 = requests.get(f"{CHAIN_API}/cosmos/base/tendermint/v1beta1/blocks/{height}")
txs = r2.json()["block"]["data"]["txs"]
tx_bytes = base64.b64decode(txs[0])
# Parse fields manually to see exact encoding
```

## Chain-Specific Notes

- **JAY Network**: `thejaynetwork`, API `https://api-jayn.winnode.xyz`
  - Uses compact 64-byte sig, nested PubKey
  - Account info: `/cosmos/auth/v1beta1/accounts/{addr}`
  - Balance: `/cosmos/bank/v1beta1/balances/{addr}`
  - Wallet address: RIPEMD160(SHA256(pubkey)) → Bech32 with 'yjay' prefix (43 chars)

## Chain ID Discovery

**CRITICAL**: Do NOT guess chain ID. Always fetch from node:
```python
r = requests.get(f"{CHAIN_API}/cosmos/base/tendermint/v1beta1/node_info")
chain_id = r.json()["default_node_info"]["network"]
```

Wrong chain ID → `invalid length: tx parse error` or code 5.

## How to Debug TX Encoding

1. **Get existing tx from chain**:
```python
r = requests.get(f"{CHAIN_API}/cosmos/base/tendermint/v1beta1/blocks/latest")
height = r.json()["block"]["header"]["height"]
r2 = requests.get(f"{CHAIN_API}/cosmos/base/tendermint/v1beta1/blocks/{height}")
txs = r2.json()["block"]["data"]["txs"]
tx_bytes = base64.b64decode(txs[0])
```

2. **Parse protobuf fields** to see exact encoding
3. **Compare** your tx encoding with existing tx
4. **Key differences** to look for:
   - PubKey nested vs raw bytes
   - Signature DER vs compact 64-byte
   - Memo field present vs absent
   - Field ordering
