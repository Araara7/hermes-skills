# Galxe Social Account Switching — Investigation Results (Jun 2026)

## Problem
Galxe connected to `@agy_sabdany7` (Twitter ID: 1340762460). Want to switch to `@otama777A` (Twitter ID: 2059872573077561345).

## Root Cause of `allow: false`
Connected Twitter `@agy_sabdany7` has **expired OAuth2 token** at Galxe's backend. Even with `mockFollow: true` (mock mode), Galxe still validates the OAuth token. Expired token → `allow: false` with no error message.

## What We Tried (ALL FAILED)

### 1. API `deleteSocialAccount`
- Mutation exists in `__schema` introspection (not deprecated, 197 total mutations)
- Input type: `{sig: String, address: String!, type: SocialAccountType!}`
- `SocialAccountType` enum: `TWITTER, DISCORD, GITHUB, TELEGRAM, WORLDCOIN, VERY`
- Return type: `Error` object
- **Result**: ALL call formats return `GRAPHQL_VALIDATION_FAILED` at mutation name level
- Tested: inline enum, variables with/without sig, EVM prefix, camelCase, with/without return fields
- **Verdict**: SCHEMA GHOST — exists in introspection but NOT callable

### 2. API `getSocialAuthUrl`
- Query: `getSocialAuthUrl(schema: String!, type: SocialAccountType!, captchaInput: CaptchaInput)`
- Returns: `String!` (OAuth redirect URL)
- **Result**: "Invalid JWT token" — requires browser session JWT, not API `signin` JWT
- Tested with schemas: `https://app.galxe.com`, `https://app.galxe.com/quest`, etc.

### 3. Browser Wallet Inject (Playwright + Camoufox)
- Injected `window.ethereum` with MetaMask-compatible API
- SIWE signing pre-computed and returned from `personal_sign`
- **Result**: Galxe uses `@appkit` SDK (WalletConnect v2), NOT direct `window.ethereum`
- localStorage keys: `@appkit/connection_status: "disconnected"`, `wagmi.store`
- AppKit won't detect injected provider

### 4. nodriver Anti-Detect Browser
- `navigator.webdriver: false` — passes bot detection
- Galxe loads successfully
- Module 95088 (`Ay`, `Qc`) accessible
- **Result**: Same AppKit issue — wallet connect dialog shows "MetaMask Installed" but clicking it doesn't trigger SIWE flow
- Dialog elements found: idx 16 = `MetaMaskInstalled` (DIV with cursor-pointer class)
- Click triggers dialog close but no `eth_requestAccounts` or `personal_sign` request

### 5. CDP Network Interception
- No WASM binary loaded on page load (lazy loading)
- No captcha-related network requests until claim/verify action

## Definitive Conclusion
**Social account switching CANNOT be done programmatically.** The user MUST:
1. Open `app.galxe.com` in real browser (not headless)
2. Connect wallet via AppKit (MetaMask/WalletConnect popup)
3. Settings → Disconnect `@agy_sabdany7`
4. Connect Twitter → authorize `@otama777A` via OAuth

After this one-time manual action, all Twitter verify via API will work automatically.

## Key Technical Details

### Galxe Frontend Stack
- Next.js (webpack chunks: `webpackChunk_N_E`)
- Apollo GraphQL client (`__APOLLO_CLIENT__`)
- AppKit/WalletConnect v2 (`@appkit` SDK)
- wagmi for wallet state (`wagmi.store` in localStorage)
- WASM captcha module 95088 (`Ay` init, `Qc` generate)

### localStorage Keys
- `@appkit/connection_status` — "connected" / "disconnected"
- `@appkit/active_caip_network_id` — "eip155:42161"
- `@appkit/active_namespace` — "eip155"
- `wagmi.store` — wallet connections map
- `connectMethod` — wallet type
- `mm-sdk-anon-id` — MetaMask anonymous ID

### GraphQL Introspection Findings
- `deleteSocialAccount` — NOT callable (schema ghost)
- `getSocialAuthUrl` — needs browser session JWT
- `VerifyTwitterOauth2Token` — needs OAuth2 bearer token
- `checkTwitterAccount` / `verifyTwitterAccount` — need tweetURL + token
- `ScoreSocialBind` — needs metricId + address + token
- `twitterOauth2Status` — works without auth, returns mock flags
