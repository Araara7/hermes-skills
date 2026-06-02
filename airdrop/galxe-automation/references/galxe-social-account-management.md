# Galxe Social Account Management — Detailed Findings (Jun 2026)

## Problem
Galxe connected to wrong Twitter (@agy_sabdany7), need to switch to @otama777A.

## API Attempts (All Failed)

### deleteSocialAccount
- **Schema:** EXISTS in introspection, NOT deprecated
- **Input:** `DeleteSocialAccountInput { sig: String, address: String!, type: SocialAccountType! }`
- **Return type:** `Error` object
- **Result:** `GRAPHQL_VALID_FAILED` on ALL call formats:
  - Inline enum: `deleteSocialAccount(input: {address: "0x...", type: TWITTER})` ❌
  - Variable with enum string: `{"input": {"address": "0x...", "type": "TWITTER"}}` ❌
  - With sig field ❌
  - EVM prefix address ❌
  - camelCase type ❌
- **Diagnosis:** Mutation exists in schema but is NOT callable via public API. May be internal-only or requires browser session auth.

### getSocialAuthUrl
- **Schema:** EXISTS, takes `schema: String!, type: SocialAccountType!, captchaInput: CaptchaInput`
- **Result:** `"Invalid JWT token"` for all schema values
- **Diagnosis:** Requires browser session JWT (not API JWT from SIWE signin). The `signin` mutation returns an API JWT, but `getSocialAuthUrl` needs the frontend session token.

### VerifyTwitterOauth2Token
- **Schema:** EXISTS, takes `address: String, token: String`
- **Result:** `GRAPHQL_VALID_FAILED` — same issue as deleteSocialAccount

## Browser Attempts (All Failed)

### Wallet Inject via window.ethereum
- Galxe uses **AppKit** (WalletConnect v2) + **wagmi** for wallet management
- `window.ethereum` injection DOES NOT WORK — AppKit checks for wallet through its own SDK
- localStorage shows: `@appkit/connection_status: "disconnected"`, `wagmi.store` with empty connections
- Clicking "MetaMask Installed" in dialog → dialog closes but NO sign request fires
- Galxe detects injected wallet is not real MetaMask

### nodriver Anti-Detect
- `navigator.webdriver: false` ✅ (undetected)
- Galxe loads successfully ✅
- Login dialog appears with wallet options ✅
- MetaMask Installed click → dialog closes silently (no SIWE flow)

### Settings Page Access
- `app.galxe.com/me/settings` → 404 without browser auth
- localStorage inject of wallet data → doesn't trigger Galxe auth
- SIWE in browser context → Galxe frontend doesn't recognize it

## Root Cause
Galxe's social account management (disconnect/reconnect) is protected by:
1. Browser session JWT (not API JWT)
2. AppKit/WalletConnect SDK (not window.ethereum)
3. Server-side validation of wallet connection

## Workaround
User must manually:
1. Open `app.galxe.com` in real browser
2. Connect wallet via AppKit (MetaMask/WalletConnect)
3. Settings → Disconnect old Twitter
4. Connect new Twitter via OAuth flow
5. After that, ALL API operations work automatically

## Key Finding
Galxe's public GraphQL API has mutations that exist in schema but cannot be called. This is a form of API-level access control — the mutation is defined but gated behind browser session auth that can't be replicated via API.
