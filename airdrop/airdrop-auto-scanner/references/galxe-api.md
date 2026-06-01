# Galxe GraphQL API Reference

## Endpoint
```
POST https://graphigo.prd.galaxy.eco/query
```

## Headers
```
Content-Type: application/json
User-Agent: Mozilla/5.0
Origin: https://app.galxe.com
```

## Key Queries

### List Campaigns
```graphql
query {
  campaigns(input: {first: 20, status: Active}) {
    list {
      id name status
      space { id name }
      credentialGroups {
        id name
        credentials { id name type description }
      }
    }
  }
}
```

### Get Single Campaign
```graphql
query {
  campaign(id: "GCekQtgjfd") {
    id name status
    credentialGroups {
      id name
      credentials { id name type description }
    }
  }
}
```

### Search Space
```graphql
query {
  project(name: "theoproject") {
    id name
    campaigns(input: {first: 5, status: Active}) {
      list { id name status }
    }
  }
}
```

## Task Types (credential types)
| Type | Auto-completable? | Notes |
|------|-------------------|-------|
| TWITTER_LIKE | ✅ | Need Twitter session |
| TWITTER_RETWEET | ✅ | Need Twitter session |
| TWITTER_FOLLOW | ✅ | Need Twitter session |
| TWITTER_QUOTE | ✅ | Need Twitter session |
| TELEGRAM_JOIN | ✅ | Need Telegram session |
| DISCORD_JOIN | ❌ | Manual or Discord bot |
| BALANCE_CHECK | ❌ | On-chain verification |
| SWAP | ❌ | On-chain tx required |
| QUIZ | ❌ | Manual answer needed |

## Auth
- Galxe uses Privy for wallet auth (same as Pixie Chess)
- API queries work without auth (read-only)
- Task completion + claim requires wallet signature

## Discovered
- 1 Jun 2026 via Camoufox network interception
- Also: `https://savings-graphigo.prd.latch.io/query` (savings/staking API)

## Script
- `~/airdrop-agent/scripts/galxe_scanner.py` — scan active campaigns, categorize tasks
- `~/airdrop-agent/scripts/galxe_auto.py` — browser automation (Camoufox + wallet inject)
