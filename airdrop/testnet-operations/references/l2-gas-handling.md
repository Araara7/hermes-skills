# L2 Gas Handling — Testnet Transfer Pitfalls

## The Problem

L2 chains (rollups) have a two-layer fee structure:
- **L2 execution gas**: like normal Ethereum gas
- **L1 data fee**: cost to post tx data to L1 (not exposed via `eth_gasPrice`)

When you try `balance - (21000 * gas_price)`, the result is too high because it doesn't account for L1 data fee.

## Error Messages

### "insufficient funds for gas * price + value"
- Most common on Optimism, Base, Blast, Soneium, Mode
- Means total cost (value + gas) exceeds balance
- **Fix**: Send 99.5% of balance

### "max fee per gas less than block base fee"
- Arbitrum Sepolia rejects EIP-1559 (`maxFeePerGas`)
- **Fix**: Use legacy `gasPrice`

### "intrinsic gas too low"
- Arbitrum: gas limit too low
- **Fix**: Use `estimate_gas()` not hardcoded 21000

### "invalid transaction: insufficient funds for l1fee + gas * price + value"
- Scroll Sepolia explicitly mentions L1 fee
- **Fix**: Send 99.5% of balance

### "nonce too low: next nonce N, tx nonce M"
- Pending/dropped transaction at that nonce
- **Fix**: Use `get_transaction_count(addr, 'pending')` or set nonce = N

## Working Transfer Pattern

```python
def send_max_l2(w3, chain_id, priv_key, from_addr, to_addr):
    addr = Web3.to_checksum_address(from_addr)
    to = Web3.to_checksum_address(to_addr)
    bal = w3.eth.get_balance(addr)
    if bal == 0:
        return None
    gas_price = w3.eth.gas_price
    # Try estimate + 50% buffer
    try:
        est = w3.eth.estimate_gas({'from': addr, 'to': to, 'value': int(bal * 0.99)})
        sendable = bal - int(est * gas_price * 1.5)
        if sendable > 0:
            nonce = w3.eth.get_transaction_count(addr)
            tx = {'from': addr, 'to': to, 'value': sendable, 'gas': est,
                  'gasPrice': gas_price, 'nonce': nonce, 'chainId': chain_id}
            signed = w3.eth.account.sign_transaction(tx, priv_key)
            return w3.to_hex(w3.eth.send_raw_transaction(signed.raw_transaction))
    except:
        pass
    # Fallback: 99.5%
    sendable = int(bal * 0.995)
    nonce = w3.eth.get_transaction_count(addr)
    tx = {'from': addr, 'to': to, 'value': sendable, 'gas': 21000,
          'gasPrice': gas_price, 'nonce': nonce, 'chainId': chain_id}
    signed = w3.eth.account.sign_transaction(tx, priv_key)
    return w3.to_hex(w3.eth.send_raw_transaction(signed.raw_transaction))
```

## Verified Chain Behavior (2026-06)

| Chain | RPC | ID | Behavior |
|---|---|---|---|
| Optimism Sepolia | sepolia.optimism.io | 11155420 | 99.5% works |
| Arbitrum Sepolia | sepolia-rollup.arbitrum.io/rpc | 421614 | Legacy gasPrice only, NO EIP-1559 |
| Base Sepolia | sepolia.base.org | 84532 | 99.5% works |
| Blast Sepolia | sepolia.blast.io | 168587773 | 99.5% works |
| opBNB Testnet | opbnb-testnet-rpc.bnbchain.org | 5611 | 99.5% works |
| Soneium Testnet | rpc.minato.soneium.org | 1946 | 99.5% works |
| Mode Sepolia | sepolia.mode.network | 919 | estimate+1.5x works |
| Scroll Sepolia | sepolia-rpc.scroll.io | 534351 | 99.5% works |
| Abstract Testnet | api.testnet.abs.xyz | 11124 | 99.5% works |
| Polygon Amoy | rpc-amoy.polygon.technology | 80002 | Standard, no L1 fee |
| Linea Sepolia | rpc.sepolia.linea.build | 59141 | Standard |
| BNB Testnet | data-seed-prebsc-1-s1.bnbchain.org:8545 | 97 | Standard |
