# Privy Authentication Reference

Privy (https://privy.io) is a popular auth provider for Web3 apps. Handles email, wallet, and social login.

## Detection

Check JS bundle for:
```bash
curl -s "https://site.com/assets/index-XXXXX.js" | grep -oE 'appId:"[a-z0-9]+"' | head -5
curl -s "https://site.com/assets/index-XXXXX.js" | grep -oE '"https://auth\.privy\.io"' | head -5
```

## Auth Methods

| Method | API Endpoint | Bypass? |
|--------|-------------|---------|
| Email | `/api/v1/email/send` + `/api/v1/email/authenticate` | ❌ Turnstile CAPTCHA |
| SIWE (Wallet) | `/api/v1/siwe/init` + `/api/v1/siwe/authenticate` | ❌ Requires browser context |
| Guest | `/api/v1/guest/authenticate` | ❌ Usually disabled |
| OAuth | `/api/v1/oauth/init` + `/api/v1/oauth/authenticate` | ❌ Requires browser |
| Passkey | `/api/v1/passkeys/authenticate` | ❌ Requires biometric |

## SIWE Flow (Sign-In With Ethereum)

1. POST `/api/v1/siwe/init` with `{address: "0x..."}` → returns `{nonce}`
2. Create SIWE message: `"domain wants you to sign in with your Ethereum account:\n0x...\n\n..."`
3. Sign message with wallet private key
4. POST `/api/v1/siwe/authenticate` with `{message, signature, chainId, walletClientType, connectorType}`

**Why API-only fails:** Requires `privy-authorization-signature` header generated client-side.

## Token Storage

```js
localStorage.getItem('privy:token')  // JWT auth token
localStorage.getItem('privy:caid')   // Client analytics ID
localStorage.getItem('privy:connections')  // Connected wallets
```

## MetaMask Injection Failure

Privy detects fake `window.ethereum` providers:
- Checks for MetaMask-specific internal properties
- `isMetaMask: true` alone is NOT sufficient
- Falls back to WalletConnect QR if detection fails
- `add_init_script` timing may not override Privy's initialization

## Workaround: Manual Token Extraction

1. User logs in on their device
2. Open DevTools → Console
3. Run: `localStorage.getItem('privy:token')`
4. Copy token to VPS
5. Inject: `localStorage.setItem('privy:token', 'TOKEN_HERE')`

## Terms of Service Modal Pattern

Many Privy-enabled apps show Terms modal before login:
1. Checkbox is disabled until terms scrolled to bottom
2. Detect: `label[class*="cursor-not-allowed"]` → not ready
3. Scroll: Find `[class*="overflow-scroll"]` container, set `scrollTop = scrollHeight`
4. Checkbox enables: `label[class*="cursor-pointer"]` → ready to click
5. Click label (NOT checkbox input directly)
6. Click CONTINUE button

**PITFALL:** Setting `checkbox.checked = true` via JS does NOT work. React controlled components require clicking the label element.
