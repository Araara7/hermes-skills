# Galxe Social Task Verification API Reference

## Overview
Galxe social tasks (Twitter follow, tweet, like, retweet, quote) are verified via `syncCredentialValue` mutation with a `twitter` field containing WASM captcha + campaignID.

## GraphQL Schema (Introspection Results)

### SyncCredentialValueInput
```
syncOptions: CredentialSyncOptionsInput! (required)
```

### CredentialSyncOptionsInput
```
credId: ID!
address: String!
twitter: TwitterCredentialValueSyncOptionsInput  (optional, for Twitter tasks)
gitcoin: GitcoinCredentialValueSyncOptionsInput
survey: SurveyCredentialValueSyncOptionsInput
quiz: QuizCredentialValueSyncOptionsInput
worldCoin: WorldCoinCredentialValueSyncOptionsInput
prediction: PredictionCredentialValueSyncOptionsInput
```

### TwitterCredentialValueSyncOptionsInput
```
captcha: CaptchaInput!    (required)
campaignID: ID!           (required)
```

### CaptchaInput
```
lotNumber: String!        (required)
captchaOutput: String!    (required)
passToken: String!        (required)
genTime: String!          (required)
encryptedData: String     (optional)
```

## Credential Types
- `TWITTER_FOLLOW` — Follow a Twitter account
- `TWITTER_TWEET` — Post a tweet
- `TWITTER_LIKE` — Like a tweet
- `TWITTER_RETWEET` — Retweet
- `TWITTER_QUOTE` — Quote tweet

## Verification Flow
1. Generate WASM captcha via Chromium (`galxe_captcha_solver.py`)
2. Strip `ok` field from captcha output (Galxe rejects it)
3. Call `syncCredentialValue` with `twitter.captcha` + `twitter.campaignID`
4. Response: `{data: {syncCredentialValue: {message, value: {allow: bool}}}}`

## Mock Mode
Query `twitterOauth2Status` to check:
```json
{
  "oauthRateLimited": false,
  "activeTokenDepleted": false,
  "serviceDown": false,
  "mockFollow": true,    // ← mock mode active
  "mockLike": true,
  "mockRetweet": true,
  "mockQuote": true
}
```

**Critical**: `mockFollow: true` means Galxe doesn't call Twitter API, BUT it still validates the connected Twitter account's OAuth2 token. If token expired → `allow: false` even in mock mode.

## Social Account Management

### Get OAuth URL
```graphql
query { getSocialAuthUrl(schema: "https://app.galxe.com", type: TWITTER) }
```
Returns: OAuth URL string. Requires valid JWT in Authorization header.
Error `"Invalid address"` = JWT expired or wrong format.

### Disconnect Twitter
```graphql
mutation { deleteSocialAccount(input: {address: "0x...", type: TWITTER, sig: "0x..."}) }
```
⚠️ GraphQL validation errors common — schema may have changed.

### Check Connected Twitter
```graphql
query { addressInfo(address: "EVM:0x...") {
    twitterUserID twitterUserName hasTwitter
}}
```

### Verify with OAuth2 Token
```graphql
mutation { VerifyTwitterOauth2Token(input: {address: "0x...", token: "oauth2_token"}) }
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `missing twitter args` | `twitter` field missing from `syncOptions` | Add `twitter: {captcha, campaignID}` |
| `must be defined` | `captcha` field missing inside `twitter` | Add captcha data |
| `allow: false` (no error) | Captcha invalid, OAuth expired, or action not done | Check twitterOauth2Status, regenerate captcha |
| `Invalid address` | getSocialAuthUrl JWT expired | Re-authenticate with SIWE |
| `GRAPHQL_VALIDATION_FAILED` | Wrong mutation syntax | Check introspection |

## Scripts
- `~/airdrop-agent/scripts/galxe_captcha_solver.py` — WASM captcha solver (Chromium)
- `~/airdrop-agent/scripts/galxe_auto_verify.py` — Auto scan + verify + follow
- `~/airdrop-agent/scripts/galxe_full_auto.py` — Full flow (scan + verify + claim)
