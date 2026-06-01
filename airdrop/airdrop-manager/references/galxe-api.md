# Galxe API Reference

## Auth (SIWE Wallet Sign)

Galxe uses Sign-In With Ethereum (SIWE). No browser needed.

```python
from eth_account import Account
from eth_account.messages import encode_defunct

nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=17))
issued_at = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
expired_at = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(time.time() + 7*24*3600))

message = f"""app.galxe.com wants you to sign in with your Ethereum account:
{address}

Sign in with Ethereum to the app.

URI: https://app.galxe.com
Version: 1
Chain ID: 1
Nonce: {nonce}
Issued At: {issued_at}
Expiration Time: {expired_at}"""

msg = encode_defunct(text=message)
signed = Account.sign_message(msg, priv_key)
signature = "0x" + signed.signature.hex()

# GraphQL mutation
result = gql('mutation SignIn($input: Auth) { signin(input: $input) }', {
    "input": {"address": address, "addressType": "EVM", "publicKey": "1", 
              "message": message, "signature": signature}
})
token = result['data']['signin']  # JWT token
```

Token valid ~7 days. Save to `config/credentials/galxe_token.json`.

## GraphQL API

**Endpoint:** `https://graphigo.prd.galaxy.eco/query`

**Headers:**
```python
headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 ...',
    'Origin': 'https://app.galxe.com',
    'Authorization': token  # JWT from signin
}
```

## Common Queries

### User Info
```graphql
query ($a: String!) {
  addressInfo(address: $a) {
    id username hasTwitter hasDiscord hasTelegram email
    twitterUserID twitterUserName
  }
}
# Variables: {"a": "EVM:0x..."}
```

### Scan Campaigns
```graphql
query {
  campaigns(input: {first: 50, listType: Trending}) {
    list { id name status space { id name alias } }
  }
}
# listType: Trending, Popular, Newest
```

### Campaign Details + Eligibility
```graphql
query ($id: ID!, $addr: String!) {
  campaign(id: $id) {
    id name status
    credentialGroups(address: $addr) {
      id
      credentials {
        id name type credType credSource
        eligible(address: $addr)
        referenceLink description
      }
      conditions { eligible }
    }
  }
}
```

### Verify Task (syncCredentialValue)
```graphql
mutation SyncCredentialValue($input: SyncCredentialValueInput!) {
  syncCredentialValue(input: $input) {
    message value { allow }
  }
}
```

**Non-Twitter tasks:**
```json
{"input": {"syncOptions": {"credId": "xxx", "address": "EVM:0x..."}}}
```

**Twitter tasks (requires captcha + campaignID):**
```json
{"input": {"syncOptions": {
  "credId": "xxx",
  "address": "EVM:0x...",
  "twitter": {
    "captcha": {"lotNumber", "captchaOutput", "passToken", "genTime", "encryptedData"},
    "campaignID": "GC..."
  }
}}}
```
Without `twitter` field → `"missing twitter args"` error.
Generate captcha via Chromium: `galxe_captcha_solver.py`

### Claim Campaign
```graphql
mutation PrepareParticipate($input: PrepareParticipateInput!) {
  prepareParticipate(input: $input) {
    allow disallowReason signature nonce
  }
}
# Variables: {"input": {"campaignId": "xxx", "address": "0x..."}}
```

## Task Types

### Auto-verifiable (API only)
| Type | Description | Notes |
|------|-------------|-------|
| `EVM_ADDRESS` | Bridge/wallet usage checks | Curator updates periodically |
| `GALXE_ID` | Follow Space, loyalty points | "Follow" works, "Visit" needs browser |
| `BALANCE` | Token balance checks | Direct API verify |
| `SOLANA_ADDRESS` | Solana wallet checks | Same as EVM_ADDRESS |
| **`TWITTER`** | **Follow, Like, Retweet, Tweet, Quote** | **Needs WASM captcha + campaignID. See below.** |

### Needs WASM captcha
| Type | How to verify |
|------|---------------|
| `TWITTER` | `syncCredentialValue` with `twitter: {captcha, campaignID}` |

See `auto-resolve-captcha` skill → `references/galxe-social-api.md` for full schema.

### Blocked (need manual/browser)
| Type | Why blocked |
|------|-------------|
| `VISIT_LINK` | Needs browser auth (server-side JWT) |
| `DISCORD` | Needs Discord OAuth binding |
| `TELEGRAM` | Needs Telegram OAuth binding |
| `EMAIL` | Needs email verification |
| `QUIZ` | Needs quiz answers |
| `SURVEY` | Needs survey answers |

## URL Format

Quest pages: `https://app.galxe.com/quest/{space_alias}/{campaign_id}`
- `space_alias` = from campaign.space.alias (e.g. "Myne")
- `campaign_id` = campaign.id (e.g. "GC2fptZpY3")

## Browser Auth Limitation

Galxe auth is server-side JWT. Cannot inject via:
- localStorage.setItem (frontend reads from different key)
- Cookies (HTTP-only, set by server)
- MetaMask inject (detected but handshake fails)

Only API SIWE auth works for automation.

## Pitfalls

1. **Token expiry** — JWT valid ~7 days. Re-auth if `addressInfo` returns null.
2. **Claim null data** — `prepareParticipate` may return `data: null`. Always use `result.get('data') or {}`.
3. **Curator delay** — EVM_ADDRESS tasks say "please wait for credential curator to update". Data refreshes periodically.
4. **GALXE_ID "Visit"** — Returns "Please click the Go button". These need browser interaction which is blocked.
5. **Rate limit** — Add 1-3s random delay between API calls.
6. **Duplicate campaigns** — Trending + Popular may overlap. Deduplicate by campaign ID.
7. **Twitter OAuth expired** — `allow: false` on Twitter tasks even in mock mode. Check `twitterOauth2Status`. Reconnect Twitter via browser OAuth.
8. **WASM captcha `ok` field** — Solver outputs `ok: true` but Galxe rejects it. Strip before sending.
9. **Twitter verify needs `campaignID`** — Not just `credId`. Both required inside `twitter` field.
