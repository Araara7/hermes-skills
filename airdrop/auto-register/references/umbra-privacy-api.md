# Umbra Privacy — API & Registration

## Overview
Umbra Privacy (app.umbraprivacy.com) is a **waitlist-based** registration, NOT wallet-based.

## Key Discovery
- Website uses Next.js + AppKit/Web3Modal (wallet features exist but NOT for registration)
- Registration is **email waitlist** with optional referral code
- Referral code auto-filled from URL parameter `?ref=XXXXX`

## Registration Flow
1. Load URL: `https://app.umbraprivacy.com/?ref={REFERRAL_CODE}`
2. Click "Get Started" button → Modal appears
3. Modal contains:
   - Email input (placeholder: `you@domain.com`)
   - Referral code input (6 segmented character boxes)
   - "Send my code" submit button
   - "Continue with Google" alternative
4. Fill email → Submit → Waitlist confirmation

## API Endpoints Discovered
```
GET  /api/bridge/chains
GET  /api/bridge/tokens?chains=1,8453,42161,10,137,56,...
GET  /api/bridge/1click-tokens
GET  /api/pool-health
GET  zk.api.umbraprivacy.com/v5/manifest.json
GET  zk.api.umbraprivacy.com/v5/zkey-wasm/userregistration.zkey
GET  zk.api.umbraprivacy.com/v5/zkey-wasm/userregistration.wasm
```

## Registration API (Not Found via Discovery)
Tested endpoints (all returned 404/405):
- POST /api/waitlist
- POST /api/register
- POST /api/signup
- POST /api/join

**Conclusion**: Registration must go through browser form submission.

## Browser Automation Script
Location: `~/airdrop-agent/scripts/umbra_register.py`

Usage:
```bash
cd ~/airdrop-agent && .venv/bin/python3 scripts/umbra_register.py email1@gmail.com email2@gmail.com
```

## localStorage Keys
```
@appkit/active_caip_network_id
@appkit/disconnected_connector_ids
@appkit/connection_status
@appkit/active_namespace
wagmi.store
base-acc-sdk.store
```

## Pitfalls
- Submit button may be disabled until email field is filled
- Referral code input is segmented (6 individual character boxes)
- No API endpoint found for direct registration - must use browser
- Rate limiting unknown - use 3s delay between registrations
