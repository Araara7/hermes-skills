# MetaMask Provider Injection for Privy Sites

## Technique (tested 31 Mei 2026 on pixiechess.xyz)

Inject a fake MetaMask provider via Playwright's `add_init_script` BEFORE page load.

### Minimal Working Provider

```javascript
// Injected via context.add_init_script() before page.goto()
window.ethereum = {
  isMetaMask: true,
  on(e, f) { (this._e = this._e || {})[e] = (this._e[e] || []).push(f) - 1; return this; },
  emit(e, ...a) { (this._e?.[e] || []).forEach(f => f?.(...a)); },
  removeListener() {},
  addListener(a, b) { return this.on(a, b); },
  async request({ method, params }) {
    if (method === 'eth_requestAccounts' || method === 'eth_accounts') {
      this.emit('accountsChanged', ['WALLET_ADDR']);
      return ['WALLET_ADDR'];
    }
    if (method === 'eth_chainId') return '0x1';
    if (method === 'net_version') return '1';
    if (method === 'wallet_switchEthereumChain' || method === 'wallet_addEthereumChain') return null;
    // personal_sign and eth_signTypedData_v4 need async handling via custom events
    if (method === 'personal_sign' || method === 'eth_sign') {
      return new Promise(r => { window._r = r; window._m = params[0]; });
    }
    if (method === 'eth_signTypedData_v4' || method === 'eth_signTypedData') {
      const d = typeof params[1] === 'string' ? JSON.parse(params[1]) : params[1];
      return new Promise(r => { window._tr = r; window._td = d; });
    }
    if (method === 'wallet_getPermissions' || method === 'wallet_requestPermissions')
      return [{ parentCapability: 'eth_accounts' }];
    if (method === 'eth_getBlockByNumber')
      return { number: '0x1', timestamp: '0x' + Math.floor(Date.now() / 1000).toString(16) };
    if (method === 'eth_getBalance') return '0x0';
    if (method === 'eth_estimateGas') return '0x5208';
    if (method === 'eth_gasPrice') return '0x3B9ACA00';
    if (method === 'eth_blockNumber') return '0x1';
    if (method === 'eth_getTransactionCount') return '0x0';
    if (method === 'eth_call') return '0x';
    throw new Error('Unsupported: ' + method);
  },
  isConnected() { return true; },
  get selectedAddress() { return 'WALLET_ADDR'; }
};
window.providers = [window.ethereum];
```

### Server-side Signing Handler

```python
# Polls browser for sign requests, signs with eth_account, returns signature
async def signer(page, private_key):
    from eth_account import Account
    from eth_account.messages import encode_defunct, encode_typed_data
    import json
    
    def sign_personal(msg):
        if msg.startswith('0x'):
            eth_msg = encode_defunct(primitive=bytes.fromhex(msg[2:]))
        else:
            eth_msg = encode_defunct(text=msg)
        return '0x' + Account.sign_message(eth_msg, private_key).signature.hex()
    
    def sign_typed(data):
        d = data.get('domain', {})
        t = {k: v for k, v in data.get('types', {}).items() if k != 'EIP712Domain'}
        pt = data.get('primaryType', '')
        m = data.get('message', {})
        return '0x' + Account.sign_message(
            encode_typed_data(domain_data=d, message_types=t, message_data=m, primary_type=pt),
            private_key
        ).signature.hex()
    
    while True:
        try:
            if await page.evaluate('!!window._r'):
                msg = await page.evaluate('window._m')
                sig = sign_personal(msg)
                await page.evaluate(f'window._r("{sig}")')
                await page.evaluate('window._r=null;')
            if await page.evaluate('!!window._tr'):
                data = await page.evaluate('window._td')
                sig = sign_typed(data)
                await page.evaluate(f'window._tr("{sig}")')
                await page.evaluate('window._tr=null;')
        except:
            pass
        await asyncio.sleep(0.3)
```

## Results

- ✅ `window.ethereum.isMetaMask` detected by Privy SDK
- ✅ Wallet connects: `privy:connections` shows wallet address
- ✅ wagmi store populated
- ❌ SIWE signing does NOT auto-trigger (no `privy:token` created)
- ❌ Turnstile CAPTCHA blocks game actions without auth token

## Key Insight

The injection works for **wallet detection** but not for **authentication**. Privy requires the SIWE flow to complete to generate a JWT token. The SIWE flow needs to be triggered by user action (like trying to play), but Turnstile CAPTCHA intercepts before SIWE can complete.

**Workaround:** User must export `privy:token` from a real browser session.
