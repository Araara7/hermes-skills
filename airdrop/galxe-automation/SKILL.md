---
name: galxe-automation
description: "Galxe quest/airdrop automation — API auth (SIWE), campaign scanning, task verification, reward claiming via GraphQL API"
tags: [airdrop, galxe, web3, graphql, automation, quest]
triggers:
  - galxe
  - galxe quest
  - galxe campaign
  - galxe claim
  - galxe auto
---

# Galxe Automation

Automate Galxe quests via GraphQL API — scan campaigns, verify tasks, claim rewards.

## Site Info
- URL: https://app.galxe.com
- GraphQL API: `https://graphigo.prd.galaxy.eco/query`
- Auth: SIWE (Sign-In with Ethereum) → JWT token
- Campaign URL format: `https://app.galxe.com/quest/<SpaceAlias>/<CampaignID>`
- User: Aphrodite7 (Twitter ✅, Discord ✅)

## Auth Flow (SIWE)

Galxe uses Sign-In with Ethereum. **No email login available.**

```python
import json, time, requests
from eth_account import Account
from eth_account.messages import encode_defunct

def galxe_signin(address, priv_key):
    ts = int(time.time())
    exp = ts + 3600  # 1 hour (can extend to 7 days)
    message = f"""app.galxe.com wants you to sign in with your Ethereum account:
{address}

Sign in with Ethereum to Galxe.

URI: https://app.galxe.com
Version: 1
Chain ID: 1
Nonce: {ts}
Issued At: {time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(ts))}
Expiration Time: {time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(exp))}"""
    
    signed = Account.sign_message(encode_defunct(text=message), priv_key)
    
    resp = requests.post('https://graphigo.prd.galaxy.eco/query',
        json={
            'query': 'mutation SignIn($input: Auth!) { signin(input: $input) }',
            'variables': {"input": {"address": address, "message": message, "signature": signed.signature.hex()}}
        },
        headers={'Content-Type': 'application/json'},
        timeout=15)
    
    return resp.json().get('data', {}).get('signin')  # JWT token string
```

**Key details:**
- Mutation: `signin(input: $input)` — returns `String!` directly (NOT `login`, NOT `{ authToken }`)
- `expirationTime` field is REQUIRED in SIWE message (without → "`expirationTime` must not be empty")
- Token sent as `token: <jwt>` header (NOT `Authorization: Bearer`)
- `Auth` input type needs: `address`, `message`, `signature` (no `addressType`/`publicKey` needed)

## API Headers

```python
headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Origin': 'https://app.galxe.com',
    'Authorization': token  # JWT from signin — NOT "token" header!
}
```

**CRITICAL:** Use `Authorization` header, NOT `token` header! The `token` header causes "empty addr" errors on mutations like `followSpace`.

## Key Queries

### Get User Info
```graphql
query { addressInfo(address: "0x...") { 
    id username
    hasTwitter hasDiscord hasTelegram hasEmail
    twitterUserName discordUserName telegramUserName
    email
    isVerifiedTwitterOauth2 isVerifiedDiscordOauth2
}}
```
Input: address WITHOUT `EVM:` prefix for this query. Returns `Address` type with all connected social accounts.

### Get Campaigns (Trending/Popular/Newest)
```graphql
query { campaigns(input: {first: 100, listType: Trending}) { list { id name status space { id name alias } } } }
```
`listType`: `Trending`, `Popular`, `Newest`. Fetch all three, deduplicate by ID for max coverage (~158 unique from 300 fetched).

### Get Campaign Details with Eligibility
```graphql
query ($id: ID!, $addr: String!) {
  campaign(id: $id) {
    id name status
    credentialGroups(address: $addr) {
      id
      credentials { id name type credType credSource eligible(address: $addr) referenceLink description }
      conditions { eligible }
    }
  }
}
```

### Follow Space
```graphql
mutation { followSpace(spaceId: 84504) }
```
Returns `Int` (1 = success). `spaceId` is numeric, get from campaign's `space.id`. Follow ALL spaces from active campaigns before verifying tasks — unlocks "Follow on Galxe" tasks.

### Check Connected Accounts
```graphql
query { addressInfo(address: "0x...") { 
    id username
    hasTwitter hasDiscord hasTelegram hasEmail
    twitterUserName discordUserName telegramUserName
    email
    isVerifiedTwitterOauth2 isVerifiedDiscordOauth2
}}
```
Returns `Address` type. Key fields: `twitterUserName`, `discordUserName`, `telegramUserName`, `isVerifiedTwitterOauth2`, `isVerifiedDiscordOauth2`. Use to check which social accounts are connected before attempting social task verification.

### Verify/Submit Task
```graphql
mutation SyncCredentialValue($input: SyncCredentialValueInput!) {
  syncCredentialValue(input: $input) { message value { allow } }
}
```
Input: `{"input": {"syncOptions": {"credId": "<cred_id>", "address": "EVM:0x..."}}}`

⚠️ `credId` goes inside `syncOptions`, NOT at top level!

**`CredentialSyncOptionsInput` fields:**
- `credId` (ID!, required)
- `address` (String!, required)
- `twitter` (TwitterCredentialValueSyncOptionsInput) — for Twitter tasks
- `gitcoin` (GitcoinCredentialValueSyncOptionsInput)
- `survey` (SurveyCredentialValueSyncOptionsInput)
- `quiz` (QuizCredentialValueSyncOptionsInput)
- `worldCoin` (WorldCoinCredentialValueSyncOptionsInput)
- `prediction` (PredictionCredentialValueSyncOptionsInput)

### Twitter Task Verify (with Captcha)
Twitter tasks require WASM captcha + campaignID:
```graphql
mutation SyncCredentialValue($input: SyncCredentialValueInput!) {
  syncCredentialValue(input: $input) { message value { allow } }
}
```
Input:
```json
{
  "input": {
    "syncOptions": {
      "credId": "<twitter_cred_id>",
      "address": "EVM:0x...",
      "twitter": {
        "captcha": {
          "lotNumber": "...",
          "captchaOutput": "...",
          "passToken": "...",
          "genTime": "...",
          "encryptedData": "..."
        },
        "campaignID": "<campaign_id>"
      }
    }
  }
}
```
**IMPORTANT:** Twitter verify returns "not eligible" if the connected Twitter account hasn't performed the action (follow, like, retweet). Check `addressInfo.twitterUserName` to verify which Twitter is connected.

### Claim Reward
```graphql
mutation PrepareParticipate($input: PrepareParticipateInput!) {
  prepareParticipate(input: $input) { allow disallowReason signature nonce }
}
```
Input: `{"input": {"campaignID": "<id>", "address": "0x...", "signature": "0x..."}}`

**⚠️ CRITICAL: `campaignID` (capital D), NOT `campaignId`!**

Required fields (from GraphQL introspection `__type(name: "PrepareParticipateInput")`):
- `campaignID` (ID!, required)
- `address` (String!, required)
- `signature` (String!, required) — any valid ETH signature
- `captcha` (CaptchaInput) — **GeeTest captcha required** for actual claim
  - Fields: `lotNumber`, `captchaOutput`, `passToken`, `genTime` (all String, required)
  - `encryptedData` (String, optional)

Without valid captcha → `disallowReason: "1001:Invalid recaptcha token"`.

### Captcha System (Updated Jun 2026)

Galxe **no longer uses GeeTest v4**. They now use a **Rust→WASM captcha** built client-side by `wasm_lib_bg.*.wasm`. The captcha payload is generated by Galxe's webpack module exporting `geetest_encrypted`.

**How it works:**
1. Galxe's webpack chunk (module `95088` in chunk `64590`) loads a WASM binary
2. WASM calls browser fingerprinting APIs (canvas, WebGL, etc.) to generate a proof
3. Returns: `lotNumber = sha256(apiName)`, `passToken = sha256(genTime)`, `genTime = unix_timestamp`, `captchaOutput = wasm.generate_data(...).geetest_encrypted`

**⚠️ WASM fingerprinting FAILS in Camoufox headless!** Camoufox's anti-fingerprinting protection intercepts browser APIs and returns Promises where synchronous values are expected → "Fingerprint detection failed: JsValue(Promise)". **Chromium headless WORKS perfectly.** Solutions:
- **Chromium headless** (Playwright chromium.launch) — WORKS, recommended ✅
- 2captcha/CapSolver GeeTest API (~$3/1000) as fallback
- Real browser on user's machine

**Why Camoufox fails but Chromium works:** Camoufox intentionally modifies browser APIs for anti-detection (canvas, WebGL, audio fingerprinting). The WASM captcha's Rust code calls these APIs synchronously via wasm-bindgen, but Camoufox's interceptors return `JsValue(Promise)` instead of resolved values. Chromium doesn't modify these APIs, so WASM gets correct synchronous responses.

**Working Chromium approach** (from `scripts/galxe_captcha_solver.py`):
1. Load Galxe page in Chromium headless (`wait_until="commit"`, wait 15-20s)
2. Fetch+eval all `_next` scripts (they don't auto-execute in headless)
3. Replace `import.meta.url` with script URL before eval
4. Build manual webpack require shim (runtime script blocked)
5. Load WASM module: `await wasm.Ay()` → `await wasm.Qc(apiName, genTime)`
6. Parse JSON → `{lotNumber, captchaOutput, passToken, genTime, encryptedData}`

**GeeTest captcha_id for Galxe:** `244bcb8b9846215df5af4c624a750db4` (legacy, from `C0mbustibll/galxe_claimer`)
const H = mod.H || Object.values(mod).find(v => typeof v === "function");
const captcha = await H({ apiName: "PrepareParticipate", shouldEncrypt: true });
// Returns: { lotNumber, captchaOutput, passToken, genTime, encryptedData }
```

**CDN paths (Galxe static):**
- Chunk: `https://b.galxestatic.com/new-web-prd/_next/static/chunks/64590-*.js`
- WASM: `https://b.galxestatic.com/new-web-prd/_next/static/media/wasm_lib_bg.*.wasm`

## Task Types

| Type | Auto-verify? | Notes |
|------|-------------|-------|
| `GALXE_ID` (Follow Space) | ✅ | Instant verify via `syncCredentialValue` (after `followSpace`) |
| `GALXE_ID` (Visit Link) | ❌ | "Please click Go button" — needs browser auth which doesn't work |
| `GALXE_ID` (Loyalty Points) | ✅ | Instant verify |
| `GALXE_ID` (Survey/Quiz) | ❌ | "missing survey/quiz answers" |
| `VISIT_LINK` | ❌ | Same as Visit — browser auth needed |
| `BALANCE` | ✅ | On-chain check, curator-dependent |
| `EVM_ADDRESS` | ⚠️ | "please wait for credential curator to update" — data refreshes periodically |
| `SOLANA_ADDRESS` | ⚠️ | Same as EVM_ADDRESS |
| `TWITTER` | ⚠️ | Needs captcha + correct Twitter account connected. Check `addressInfo.twitterUserName` first. Returns "not eligible" if account hasn't performed action. |
| `DISCORD` | ⚠️ | Same as Twitter — needs correct Discord account + captcha |
| `TELEGRAM` | ❌ | Needs OAuth binding |
| `EMAIL` | ❌ | Needs email verification |

**Note:** `GALXE_ID` is ambiguous — can be follow (auto) or visit (manual). Always check the `syncCredentialValue` response message.

## Social Account Management

### Check Connected Accounts
```graphql
query ($a: String!) { addressInfo(address: $a) {
    id username
    hasTwitter hasDiscord hasTelegram hasEmail
    twitterUserID twitterUserName
    discordUserID discordUserName
    email
    isVerifiedTwitterOauth2 isVerifiedDiscordOauth2
}}
```
Input: address with `EVM:0x...` prefix. Returns which social accounts are connected.

### Twitter OAuth2 Status
```graphql
query { twitterOauth2Status {
    oauthRateLimited activeTokenDepleted serviceDown
    mockFollow mockLike mockRetweet mockQuote
}}
```
**Key insight:** `mockFollow: true` means Galxe's Twitter verification is in MOCK mode — it should accept verification without actually checking Twitter actions. However, a valid connected Twitter OAuth token is still required. If `allow: false` despite mock mode, the connected Twitter's OAuth token is likely **expired**.

### Disconnect Social Account
```graphql
mutation DeleteSocialAccount($input: DeleteSocialAccountInput!) {
    deleteSocialAccount(input: $input)
}
```
Input: `{address, type: TWITTER|DISCORD|GITHUB|TELEGRAM|WORLDCOIN|VERY, sig}`

⚠️ **Known issue:** This mutation may fail with `GRAPHQL_VALIDATION_ERROR` via API. May require browser session auth. Try inline enum: `deleteSocialAccount(input: {address: "0x...", type: TWITTER})`

### Get OAuth URL for Connecting
```graphql
query { getSocialAuthUrl(schema: "https://app.galxe.com", type: TWITTER) }
```
Returns OAuth redirect URL. Requires valid JWT in Authorization header. If "Invalid JWT token" error, re-authenticate (token expired).

### Verify with OAuth2 Token
```graphql
mutation VerifyTwitterOauth2Token($input: VerifyTwitterOauth2TokenInput!) {
    VerifyTwitterOauth2Token(input: $input)
}
```
Input: `{address, token}` — where `token` is a Twitter OAuth2 bearer token.

### Social Account Type Enum
`SocialAccountType`: `TWITTER`, `DISCORD`, `GITHUB`, `TELEGRAM`, `WORLDCOIN`, `VERY`

### Switching Connected Twitter Account
**Problem:** Galxe connected to wrong Twitter (e.g. `@agy_sabdany7`) but want to use `@otama777A`.

**Flow:**
1. Check current: `addressInfo` → `twitterUserName`
2. Disconnect old: `deleteSocialAccount` (may need browser)
3. Get OAuth URL: `getSocialAuthUrl(schema, type: TWITTER)`
4. Visit OAuth URL with new Twitter's session cookies (auth_token + ct0)
5. Authorize → redirects back to Galxe with OAuth code
6. Galxe stores new OAuth token

**Browser approach (if API disconnect fails):**
1. Open Galxe in Chromium with wallet injected
2. Navigate to `https://app.galxe.com/me/settings`
3. Click Disconnect on current Twitter
4. Click Connect Twitter → redirects to Twitter OAuth
5. Inject new Twitter's cookies (auth_token + ct0) before OAuth redirect
6. Authorize → done

**⚠️ Browser wallet auth is hard:** Galxe uses server-side JWT, not MetaMask inject. Settings page returns 404 without proper auth. May need to use SIWE in browser context first.

**💡 Alternative: Use `nodriver` for stronger anti-detection:** nodriver bypasses Cloudflare and has better anti-detection than Camoufox/Playwright. See `unified-auth-manager` skill for nodriver integration.

### Social Task Verification Flow
1. Check `addressInfo` for connected accounts (`twitterUserName`, `discordUserName`)
2. Check `twitterOauth2Status` for mock mode — if `mockFollow: true`, Twitter actions may not be needed
3. Verify the connected account's OAuth token is NOT expired (if `allow: false` despite mock → expired)
4. Generate WASM captcha via Chromium (`galxe_captcha_solver.py`)
5. Call `syncCredentialValue` with `twitter` parameter containing captcha + campaignID
6. If "not eligible" → connected account hasn't performed the action OR OAuth token expired
7. If `allow: false` with no error → likely expired OAuth token, need to reconnect Twitter

**Root cause of `allow: false` with no error:**
- Connected Twitter's OAuth2 token expired at Galxe's backend
- Even mock mode requires valid OAuth token
- Solution: reconnect Twitter via browser OAuth flow

## Expanded Campaign Scanning

Fetch from all list types for max coverage:
```python
all_campaigns = {}
for list_type in ['Trending', 'Popular', 'Newest']:
    camps = get_campaigns(token, list_type, 100)
    for c in camps:
        if c['id'] not in all_campaigns:
            all_campaigns[c['id']] = c
    time.sleep(1)
# ~158 unique campaigns from 300 fetched
```

Filter for wallet-only campaigns:
```python
AUTO_TYPES = {'EVM_ADDRESS', 'GALXE_ID', 'BALANCE', 'SOLANA_ADDRESS'}
SOCIAL_TYPES = {'TWITTER', 'DISCORD', 'TELEGRAM', 'EMAIL', 'VISIT_LINK', 'QUIZ', 'SURVEY'}

for camp in all_campaigns:
    creds = get_campaign_creds(token, camp['id'], address)
    auto = [c for c in creds if c['credType'] in AUTO_TYPES and not c['eligible']]
    social = [c for c in creds if c['credType'] in SOCIAL_TYPES and not c['eligible']]
    if not social and auto:
        wallet_only.append(camp)  # Only auto-verifiable tasks remaining
```

## Scripts
- `~/airdrop-agent/scripts/galxe_captcha_solver.py` — **WORKING** Chromium-based WASM captcha solver
- `~/airdrop-agent/scripts/galxe_auto_verify.py` — **WORKING** Auto-verify: scan + follow + verify
- `~/airdrop-agent/scripts/galxe_bg.py` — Full flow: auth → captcha → claim
- `~/airdrop-agent/scripts/galxe_full_auto.py` — v9: Pure API auth → scan → verify
- `~/airdrop-agent/scripts/galxe_expanded_scan.py` — Expanded scanner: 158+ campaigns
- `~/airdrop-agent/scripts/galxe_claimer_v2.py` — Claim with Chromium captcha
- `~/airdrop-agent/scripts/galxe_claimer.py` — Claim with GeeTest (legacy)
- `~/airdrop-agent/scripts/galxe_scanner.py` — API scanner
- `~/airdrop-agent/scripts/galxe_api_discover.py` — Diagnostic
- `~/airdrop-agent/scripts/_archive/galxe_debug/` — 23 archived debug/experimental scripts

## References
- `references/galxe-api-types.md` — **NEW** Full API types: Address fields, CredentialSyncOptionsInput, CaptchaInput, Chain enum, CampaignStatus, ListType
- `references/auto-verify-workflow.md` — **NEW** Complete auto-verify Python patterns: auth, follow spaces, verify tasks, Twitter with captcha
- `references/galxe-api-schema.md` — GraphQL introspection results
- `references/geetest-claim.md` — GeeTest captcha solving approach (legacy, pre-WASM)
- `references/wasm-captcha.md` — WASM captcha internals (CDN paths, module structure)
- `references/wasm-captcha-chromium.md` — **Chromium headless solution** (working approach, error catalog, webpack shim patterns)
- `references/webpack-require-shim.md` — **NEW** Complete webpack require shim code with all helpers explained
- `references/galxe-social-account-switching.md` — **NEW** Investigation results: all attempts to switch connected Twitter, definitive blockers, Galxe frontend stack details

## Pitfalls

- **`campaignID` NOT `campaignId`**: GraphQL field is `campaignID` (capital D). Using wrong case → "Invalid request" on `variable.input.campaignId`
- **Auth header**: `Authorization: <token>` (NOT `Bearer <token>`)
- **`credId` in `syncOptions`**: Must nest inside `syncOptions`, not top level
- **Address format**: `EVM:0x...` prefix for `syncOptions.address` and `addressInfo`
- **Token expires**: ~7 days. Re-auth if empty responses.
- **GALXE_ID ambiguity**: "Visit" type tasks use GALXE_ID but need browser interaction. Check `syncCredentialValue` response: "Go button" = needs visit, "not eligible" = needs user action.
- **Browser auth FAILS**: MetaMask inject, email login, localStorage injection — all fail. Galxe uses server-side JWT. Don't waste time on browser auth.
- **Visit link tasks**: Can't auto-verify. "Please click Go button and visit the link first" is a dead end without browser auth.
- **EVM_ADDRESS tasks**: Often return "please wait for credential curator to update" — data refreshes periodically, run daily cron to catch updates.
- **Claim requires WASM captcha**: `PrepareParticipateInput` needs `captcha` field with WASM-generated params (lotNumber, captchaOutput, passToken, genTime, encryptedData). Without → "Invalid recaptcha token". Galxe migrated from GeeTest v4 to WASM captcha (Jun 2026).
- **WASM captcha FAILS in Camoufox, WORKS in Chromium**: Camoufox headless fails with "JsValue(Promise)" due to anti-fingerprinting API interception. **Use Playwright Chromium** (`playwright.chromium.launch(headless=True)`) — WASM works perfectly. See `scripts/galxe_captcha_solver.py` for working implementation.
- **Galxe scripts don't auto-execute in headless**: Next.js scripts load in DOM but don't hydrate. Fix: fetch+eval all `_next` scripts manually: `document.querySelectorAll('script[src*="_next"]').forEach(s => fetch(s.src).then(r=>r.text()).then(eval))`
- **`import.meta.url` undefined in eval context**: When eval'ing fetched scripts, `import.meta.url` is undefined. Fix: replace with script URL: `code.replace(/import\.meta\.url/g, JSON.stringify(s.src))`
- **Webpack runtime blocked**: `webpack-64ade34b243dbd78.js` throws "Permission denied to access property autoAllocateChunkSize". Fix: skip it, build manual webpack require shim with all helpers (d, o, r, n, e, U=URL, O, C, g, b, p).
- **Campaign URL**: `app.galxe.com/quest/<SpaceAlias>/<CampaignID>` — NOT `app.galxe.com/quest/<CampaignID>` (404).
- **Camoufox nesting**: Can't create multiple Camoufox instances in same process (Playwright sync API conflict). Use `subprocess.run()` for browser visits.
- **Rate limiting**: Random 1-3s delay between API calls. 0.5s for scan phase.
- **Anti-bot detection**: Even with valid captcha, Galxe may reject with "bot suspicious user". This is IP/fingerprint based (datacenter IPs flagged). Solutions: residential proxy, manual first claim to build wallet reputation, or different IP.
- **Twitter account mismatch**: Galxe may have a DIFFERENT Twitter connected than expected. Always check `addressInfo.twitterUserName` before attempting Twitter verify. "not eligible" means the connected account hasn't performed the action.
- **followSpace before verify**: Must follow spaces BEFORE verifying "Follow on Galxe" tasks. `followSpace(spaceId)` returns 1 on success. Get spaceId from campaign's `space.id` field.
- **WASM captcha for social tasks**: Twitter/Discord verify requires WASM captcha in the `twitter`/`discord` parameter, not just credId+address.
- **GraphQL introspection works**: `__type(name: "TypeName")` to discover all fields.
- **Captcha field `ok` must be removed**: WASM captcha solver returns `{ok: true, lotNumber, ...}`. The `ok` field is NOT part of `CaptchaInput` — must strip it before passing to API. Otherwise → `GRAPHQL_VALIDATION_FAILED` on `captcha.ok`.
- **`allow: false` with no error = expired OAuth token**: If `syncCredentialValue` returns `{allow: false}` with no error message and `mockFollow: true`, the connected Twitter/Discord OAuth token is expired. Need to reconnect social account via browser OAuth flow.
- **`deleteSocialAccount` may fail via API**: The mutation accepts `SocialAccountType` enum but may return `GRAPHQL_VALIDATION_ERROR`. Fallback: use browser to disconnect in settings page.
- **`getSocialAuthUrl` needs valid JWT**: Returns "Invalid JWT token" if the signin JWT is expired. Re-authenticate first.
- **Settings page 404 without auth**: `app.galxe.com/me/settings` returns 404 if wallet isn't authenticated in browser. Galxe uses server-side JWT, not MetaMask inject. Need to complete SIWE flow in browser context first.
- **Twitter OAuth flow requires browser**: Switching connected Twitter account can't be done purely via API. Need browser with: (1) wallet authenticated, (2) new Twitter's session cookies (auth_token + ct0) injected before OAuth redirect.
- **`syncCredentialValue` for non-Twitter tasks doesn't need captcha**: Only Twitter/Discord tasks need the `twitter`/`discord` parameter with captcha. Follow, EVM_ADDRESS, BALANCE tasks work with just `credId` + `address`.
- **Campaign scanning deduplication**: Fetch Trending + Popular + Newest (100 each) → deduplicate by ID → ~158 unique campaigns. Don't fetch same campaign twice.
- **`credentialGroups(address:)` shows eligibility**: Use this to filter only unverified tasks before attempting verification.

## GitHub References
- `C0mbustibll/galxe_claimer` ⭐53 — GeeTest v4 claim flow (legacy, pre-WASM). Shows GeeTest captcha_id, `gcaptcha4.geetest.com` endpoints, `PrepareParticipate` mutation format.
- `dante4rt/galxe-autocomplete-tasks` ⭐222 — Browser DevTools script for auto-completing Galxe tasks.

## Workflow

1. **Auth**: `galxe_signin(address, priv_key)` → JWT token (save to `config/credentials/galxe_token.json`)
2. **Check social**: `addressInfo` → verify connected Twitter/Discord accounts
3. **Check mock mode**: `twitterOauth2Status` → if `mockFollow: true`, social tasks may verify without actual actions
4. **Scan**: Fetch Trending + Popular + Newest (100 each) → deduplicate (~158 unique)
5. **Filter**: Classify each campaign's tasks → identify wallet-only campaigns
6. **Follow spaces**: `followSpace(spaceId)` for all active campaigns
7. **Verify basic tasks**: `syncCredentialValue` for EVM_ADDRESS, BALANCE, GALXE_ID (follow only) — NO captcha needed
8. **Generate captcha**: WASM captcha via Chromium (`galxe_captcha_solver.py`)
9. **Verify social tasks**: `syncCredentialValue` with `twitter` param (captcha + campaignID)
10. **Claim**: `prepareParticipate` with WASM captcha token
11. **Report**: Summary to user. Cron daily at 10:00 WIB.

**If social tasks return `allow: false`:**
1. Check `twitterOauth2Status` for mock mode
2. Check `addressInfo.twitterUserName` for correct account
3. If mock mode is on but still false → OAuth token expired
4. Reconnect Twitter via browser OAuth flow (see Social Account Management section)

## Auto-Verify Workflow (No Captcha Needed for Basic Tasks)

Task verification via `syncCredentialValue` does NOT require captcha for basic tasks (Follow, EVM_ADDRESS, BALANCE). Twitter/Discord tasks NEED captcha. Run daily:

```bash
# Scan + verify all auto-verifiable tasks (includes following spaces)
./venv/bin/python3 scripts/galxe_auto_verify.py scan

# Verify single campaign
./venv/bin/python3 scripts/galxe_auto_verify.py verify <campaign_id>
```

**What auto-verifies (NO captcha):**
- ✅ Follow on Galxe (GALXE_ID) — works after `followSpace(spaceId)`
- ✅ EVM_ADDRESS — if on-chain activity exists
- ✅ BALANCE — if wallet has required balance

**What needs captcha:**
- ⚠️ Twitter tasks — needs WASM captcha + correct Twitter account connected
- ⚠️ Discord tasks — needs WASM captcha + correct Discord account connected

**What CANNOT auto-verify:**
- ❌ Visit links — "Please click Go button" (needs browser)
- ❌ Telegram — needs OAuth binding
- ❌ Email — needs verification

**Key API calls:**
1. `followSpace(spaceId)` — follow all spaces from active campaigns (one-time, no captcha)
2. `syncCredentialValue` — verify tasks (credId + address, no captcha for basic tasks)
3. `syncCredentialValue` with `twitter` param — verify Twitter tasks (needs captcha)

**Typical results (100 campaigns):** ~20 verified (follow+twitter), ~50 failed (visit tasks), ~100 manual skipped

## Cron Setup

```bash
# Daily auto-verify at 10:00 WIB (03:00 UTC)
0 3 * * * cd ~/airdrop-agent && ./venv/bin/python3 scripts/galxe_auto_verify.py scan >> /tmp/galxe_verify.log 2>&1
```

## Nodriver Integration (Jun 2026)

**nodriver** (⭐4.3K) — Python anti-detect browser, CDP-based, no Selenium.
- `navigator.webdriver: false` — undetected!
- Galxe loads successfully
- Module 95088 accessible (WASM captcha module with `Ay` and `Qc` exports)
- WASM binary doesn't auto-load (lazy loading, only on claim/verify action)
- Best combo: **nodriver** (anti-detect navigation) + **Chromium** (WASM captcha solver)

```python
import nodriver as uc
CHROME = "/home/ubuntu/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome"

browser = await uc.start(headless=True, browser_executable_path=CHROME,
    browser_args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'])
tab = await browser.get("https://app.galxe.com")
await asyncio.sleep(15)
# navigator.webdriver = false (undetected!)
```

**nodriver vs Camoufox vs Playwright:**
| Feature | nodriver | Camoufox | Playwright |
|---------|----------|----------|------------|
| webdriver flag | false ✅ | false ✅ | true ❌ |
| WASM captcha | ❌ (lazy load) | ❌ (fingerprint) | ✅ works |
| Cloudflare bypass | ✅ | ✅ | ❌ |
| Anti-detect | ✅ best | ✅ good | ❌ bad |
| Async | ✅ native | ❌ sync | ✅ both |

**Social Account Management Limitations:**
- `deleteSocialAccount` mutation EXISTS in schema but CANNOT be called via API (`GRAPHQL_VALIDATION_FAILED`)
- `getSocialAuthUrl` requires browser session JWT (not API JWT from SIWE signin)
- Galxe uses AppKit/WalletConnect — `window.ethereum` injection doesn't work
- Browser wallet auth requires proper AppKit SDK connection
- **Conclusion:** Social account switching (disconnect/reconnect Twitter) requires manual browser action by user. One-time setup only.

- **Claim requires WASM captcha**: Can verify tasks via API but claim needs WASM captcha token. **Solution: Chromium headless** (Playwright) generates valid tokens. See `scripts/galxe_captcha_solver.py`. Fallback: 2captcha/CapSolver API (~$3/1000).
- **Visit tasks blocked**: No browser auth = can't auto-verify visit link tasks.
- **Social tasks need captcha**: Twitter/Discord verify requires WASM captcha in the `twitter`/`discord` parameter.
- **Twitter account mismatch**: Galxe may have different Twitter connected than expected. Check `addressInfo.twitterUserName` first.
- **Curator lag**: EVM_ADDRESS data may be stale. Daily cron catches updates.
- **Anti-bot detection**: VPS IPs flagged. Residential proxy or manual first claim needed for successful claiming.
- **Social OAuth token expiry**: Connected Twitter/Discord OAuth tokens expire silently. `allow: false` with no error = expired token. Need browser OAuth flow to reconnect.
- **Social account switching requires browser**: Can't disconnect/reconnect social accounts purely via API. Need browser with wallet auth + new social session cookies.
- **Settings page requires browser auth**: `app.galxe.com/me/settings` returns 404 without proper SIWE auth in browser context. MetaMask inject alone doesn't work.
- **deleteSocialAccount mutation is a SCHEMA GHOST**: The mutation exists in `__schema` introspection (not deprecated), but ALL calls return `GRAPHQL_VALIDATION_FAILED` at the mutation name level. Column position points to the mutation name itself. Tested every format: inline enum, variables with/without sig, EVM prefix, camelCase. This mutation is NOT callable via the public GraphQL API. Do NOT waste time retrying.
- **getSocialAuthUrl requires browser session JWT**: Returns "Invalid JWT token" even with a valid `signin` JWT. The `schema` parameter expects a redirect URL, but the auth mechanism is browser session cookies, NOT the API JWT. Cannot be called from curl/requests.
- **Galxe uses AppKit/WalletConnect, NOT MetaMask direct**: `window.ethereum` injection fails because Galxe's frontend uses `@appkit` SDK (WalletConnect v2), not direct `window.ethereum.request()`. localStorage key `@appkit/connection_status` tracks state. `wagmi.store` manages wallet connections. Even with a perfect MetaMask inject, the AppKit SDK won't detect it.
- **Social account switching CANNOT be done programmatically**: User MUST manually: (1) open Galxe in real browser, (2) connect wallet via AppKit, (3) settings → disconnect old social, (4) connect new social via OAuth. No API shortcut exists. This is a hard blocker, not a "haven't found the way yet."
- **nodriver works for Galxe browsing but not wallet connect**: `navigator.webdriver: false`, undetected. Can load Galxe, access webpack module 95088, find `captchaModal`. But wallet connection via AppKit still fails. Use nodriver for anti-detect page access, not for wallet auth.
- **nodriver async evaluate returns None for Promises**: `await tab.evaluate("async () => { ... }")` returns `None` in nodriver. Workaround: store result in `window.__result`, poll with sync evaluate. Or use callback pattern: `window.__result = 'pending'; promise.then(r => window.__result = r)`.
- **User preference: NO spam during work**: Do NOT send intermediate results/progress to Telegram. Work silently, send only final report. This is a hard preference, not optional.
