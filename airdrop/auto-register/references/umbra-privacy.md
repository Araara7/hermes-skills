# Umbra Privacy — Registration & API Reference

## Overview
- **URL:** https://app.umbraprivacy.com/?ref=5VDB4Z
- **Type:** Web3 DeFi privacy platform (NOT traditional email signup)
- **Tech:** Next.js + Wagmi + Web3Modal (AppKit)
- **Backend:** Phoenix DAO LLC
- **Chains:** Ethereum, Base, Arbitrum, Optimism, Polygon, BSC, Solana, and more

## Registration Flow

### Waitlist (Initial)
1. Load page with referral URL: `https://app.umbraprivacy.com/?ref={CODE}`
2. Click "Get Started" button
3. Modal appears: "Join the waitlist"
4. Fill email input (placeholder: `you@domain.com`)
5. Referral code auto-filled from URL (6 segmented boxes)
6. Click "Send my code" → sends access code to email
7. **Rate limit:** ~2758s cooldown after multiple attempts

### Access Code (Invite)
1. Click "Already have an access code?" (button at bottom of waitlist modal)
2. New modal: "Enter access code" — 6 alphanumeric boxes
3. Type code via **keyboard** (NOT fill — see OTP pattern in SKILL.md)
4. Button changes to "Verifying..."
5. On success: modal closes, full app access granted

## API Endpoints

### Waitlist
```
POST /proxy/backend/v3/referral/access-codes/redeem
Content-Type: application/json
Origin: https://app.umbraprivacy.com

Body: {"code":"<6-char-code>","referralCode":"<referral>"}

Responses:
  200: {"success":true} — code redeemed
  400: {"success":false,"error":"invalid_format"} — wrong body format
  429: {"success":false,"error":"Rate limit exceeded. Try again shortly."}
```

### Bridge/Pool APIs (public, no auth)
```
GET /api/bridge/chains — supported chains list
GET /api/bridge/tokens?chains=1,8453,... — token list per chain
GET /api/bridge/1click-tokens — quick bridge tokens
GET /api/pool-health — pool liquidity scores
```

### ZK Proof Endpoints
```
GET zk.api.umbraprivacy.com/v5/manifest.json — ZK circuit manifest
GET zk.api.umbraprivacy.com/v5/zkey-wasm/userregistration.zkey
GET zk.api.umbraprivacy.com/v5/zkey-wasm/userregistration.wasm
GET zk.api.umbraprivacy.com/v5/zkey-wasm/createdeposit*.zkey
GET zk.api.umbraprivacy.com/v5/zkey-wasm/claimdeposit*.zkey
```

## Wallet Connection
- Uses Web3Modal/AppKit with projectId `c6c84f74cf1b67f76233fb7a98f14724`
- localStorage keys: `@appkit/*`, `wagmi.store`, `base-acc-sdk.store`
- Connection status: `@appkit/connection_status` (values: `disconnected`, `connected`)
- Active namespace: `@appkit/active_namespace` (values: `solana`, `eip155`)

## Pitfalls

### Rate Limiting (CRITICAL)
- Waitlist "Send my code" triggers ~45 min cooldown after 2-3 attempts
- Access code redeem API also rate-limited
- **Always test API first** before browser automation to avoid wasting attempts
- If rate limited, wait or use different IP

### OTP Input
- Code boxes use `input[maxlength="1"]` with `aria-label="Character N of 6"`
- `fill()` does NOT work — must use `keyboard.press()` per digit
- 12 boxes total on page (6 for referral + 6 for access code) — target the correct set

### Button Clicks
- "Already have an access code?" button is behind modal overlay
- Playwright `locator.click()` fails with "subtree intercepts pointer events"
- Must use `page.evaluate()` with `element.click()` via JS

### No Email Registration
- Umbra does NOT have traditional email/password registration
- Waitlist = email only (no password)
- Full access requires wallet connection (Wagmi/Web3Modal)
- Access code is invite-only ("Ping us on X" if no code)

## Detection Patterns
- Success: modal closes, main app visible (Shield/Private Swap/Private Send/Withdraw/Bridge tabs)
- Still verifying: button shows "Verifying..." text
- Rate limited: "Slow down. Retry in Xs." message
- Invalid code: stays on code entry page
