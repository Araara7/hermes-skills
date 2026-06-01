# eth-account Library Reference

## Installation
```bash
# Create venv first (system Python is externally managed)
python3 -m venv venv
source venv/bin/activate
pip install eth-account
```

## Basic Usage

### Derive Address from Private Key
```python
from eth_account import Account

private_key = "0x..."
account = Account.from_key(private_key)

print(f"Address: {account.address}")
```

### Generate New Account
```python
from eth_account import Account

account = Account.create()
print(f"Address: {account.address}")
print(f"Key: {account.key.hex()}")
```

### Sign Message
```python
from eth_account import Account
from eth_account.messages import encode_defunct

message = encode_defunct(text="Hello World")
signed = Account.sign_message(message, private_key)

print(f"Signature: {signed.signature.hex()}")
```

## Common Issues

### ModuleNotFoundError: eth_account
**Solution**: Use venv, not system Python
```bash
python3 -m venv venv
source venv/bin/activate
pip install eth-account
```

### externally-managed-environment
**Solution**: Use `--break-system-packages` or venv
```bash
# Option 1: venv (recommended)
python3 -m venv venv

# Option 2: force install
pip install eth-account --break-system-packages
```

## Dependencies
- eth-abi
- eth-keyfile
- eth-keys
- eth-rlp
- eth-utils
- hexbytes
- rlp
- pydantic
