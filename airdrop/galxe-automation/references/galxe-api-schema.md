# Galxe GraphQL Schema — Key Types

Discovered via `__type` introspection. Use for building correct API calls.

## PrepareParticipateInput (Claim)
```
campaignID: ID! (required) — NOT "campaignId"
address: String! (required)
signature: String! (required) — any valid ETH signature
addressType: AddressType (enum)
mintCount: Int
chain: Chain (enum)
burnedNFTIDs: [ID]
optIn: OptInInput
captcha: CaptchaInput
premintTo: String
referralCode: String
pointMintAmount: Int
claimVersion: SpaceStationVersion (enum)
```

## CaptchaInput (GeeTest v4)
```
lotNumber: String! (required)
captchaOutput: String! (required)
passToken: String! (required)
genTime: String! (required)
encryptedData: String
```

## Campaign List Types
`Trending`, `Popular`, `Newest` — all return up to 100 campaigns each.

## Credential Types (credType)
- `GALXE_ID` — Follow space, visit link, loyalty points, survey, quiz (ambiguous!)
- `EVM_ADDRESS` — On-chain wallet/bridge check
- `SOLANA_ADDRESS` — Solana on-chain check
- `BALANCE` — Token balance check
- `VISIT_LINK` — Visit external link
- `TWITTER` — Twitter follow/like/retweet
- `DISCORD` — Discord join/verify
- `TELEGRAM` — Telegram join
- `EMAIL` — Email verification

## Auth Mutation
```graphql
mutation SignIn($input: Auth) { signin(input: $input) }
# input: {address, addressType: "EVM", publicKey: "1", message, signature}
# Returns: JWT token string
```

## Key Queries
- `addressInfo(address: "EVM:0x...")` — user info
- `campaigns(input: {first: N, listType: X})` — campaign list
- `campaign(id: "GC...")` — single campaign details

## Key Mutations
- `signin(input: Auth)` — authenticate
- `syncCredentialValue(input: SyncCredentialValueInput)` — verify task
- `prepareParticipate(input: PrepareParticipateInput)` — claim reward

## Rate Limiting
- ~0.5s between scan queries
- ~1-3s between verify queries
- No explicit rate limit headers observed, but random delays recommended
