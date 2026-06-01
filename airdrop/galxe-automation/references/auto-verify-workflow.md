# Galxe Auto-Verify Workflow

## Complete Python Script Pattern

```python
import json, requests, time
from eth_account import Account
from eth_account.messages import encode_defunct

GALXE_API = "https://graphigo.prd.galaxy.eco/query"
WALLET_KEY = "0x..."  # Private key
WALLET_ADDR = "0x..."

def gql(query, variables=None, token=None):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Origin": "https://app.galxe.com"
    }
    if token:
        headers["Authorization"] = token  # NOT "token"!
    r = requests.post(GALXE_API, json={"query": query, "variables": variables or {}}, headers=headers, timeout=30)
    return r.json()

def auth():
    acct = Account.from_key(WALLET_KEY)
    ts = int(time.time())
    exp = ts + 3600
    msg = f"""app.galxe.com wants you to sign in with your Ethereum account:
{WALLET_ADDR}

Sign in with Ethereum to Galxe.

URI: https://app.galxe.com
Version: 1
Chain ID: 1
Nonce: {ts}
Issued At: {time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(ts))}
Expiration Time: {time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(exp))}"""
    
    sig = acct.sign_message(encode_defunct(text=msg))
    r = gql('mutation SignIn($input: Auth!) { signin(input: $input) }',
            {"input": {"address": WALLET_ADDR, "message": msg, "signature": sig.signature.hex()}})
    return r.get("data", {}).get("signin")

def follow_all_spaces(token, camps):
    """Follow all spaces from active campaigns."""
    spaces = {}
    for camp in camps:
        if camp.get('status') != 'Active':
            continue
        space = camp.get('space', {})
        if space and space.get('id'):
            sid = space['id']
            if sid not in spaces:
                spaces[sid] = space.get('name', '?')
    
    followed = 0
    for sid, name in spaces.items():
        r = gql(f'mutation {{ followSpace(spaceId: {sid}) }}', token=token)
        if r.get('data', {}).get('followSpace'):
            followed += 1
        time.sleep(0.2)
    
    return followed

def verify_task(token, cred_id):
    """Verify a single task (no captcha needed for basic tasks)."""
    query = 'mutation SyncCredentialValue($input: SyncCredentialValueInput!) { syncCredentialValue(input: $input) { message value { allow } } }'
    return gql(query, {"input": {"syncOptions": {"credId": cred_id, "address": f"EVM:{WALLET_ADDR}"}}}, token)

def verify_twitter_task(token, cred_id, campaign_id, captcha):
    """Verify Twitter task with captcha."""
    query = 'mutation SyncCredentialValue($input: SyncCredentialValueInput!) { syncCredentialValue(input: $input) { message value { allow } } }'
    return gql(query, {"input": {"syncOptions": {
        "credId": cred_id,
        "address": f"EVM:{WALLET_ADDR}",
        "twitter": {
            "captcha": {
                "lotNumber": captcha['lotNumber'],
                "captchaOutput": captcha['captchaOutput'],
                "passToken": captcha['passToken'],
                "genTime": captcha['genTime'],
                "encryptedData": captcha.get('encryptedData', '')
            },
            "campaignID": campaign_id
        }
    }}}), token)

def check_connected_accounts(token):
    """Check which social accounts are connected."""
    r = gql('query { addressInfo(address: "' + WALLET_ADDR + '") { id username hasTwitter hasDiscord hasTelegram hasEmail twitterUserName discordUserName telegramUserName email isVerifiedTwitterOauth2 isVerifiedDiscordOauth2 }}', token=token)
    return r.get('data', {}).get('addressInfo')

# Main workflow
token = auth()
camps = get_campaigns(token, 100)  # Fetch campaigns

# Step 1: Follow all spaces (one-time)
followed = follow_all_spaces(token, camps)

# Step 2: Check connected accounts
accounts = check_connected_accounts(token)
print(f"Twitter: @{accounts.get('twitterUserName')} (verified: {accounts.get('isVerifiedTwitterOauth2')})")

# Step 3: Verify tasks
for camp in camps:
    creds = get_campaign_creds(token, camp['id'], WALLET_ADDR)
    for cred in creds:
        if cred['type'] == 'GALXE_ID' and not cred['eligible']:
            r = verify_task(token, cred['id'])
            # Check result...
```

## Key Patterns

1. **Always follow spaces first** — `followSpace(spaceId)` before verifying "Follow on Galxe" tasks
2. **Check connected accounts** — `addressInfo` query to see which social accounts are connected
3. **Basic tasks need no captcha** — Follow, EVM_ADDRESS, BALANCE can be verified without captcha
4. **Twitter/Discord need captcha** — Must generate WASM captcha and pass in `twitter`/`discord` parameter
5. **"not eligible" = account hasn't performed action** — Not a bug, just means the connected social account hasn't done the required action (follow, like, retweet)
