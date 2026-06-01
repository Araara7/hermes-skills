# GeeTest Captcha for Galxe Claims

Galxe claims require GeeTest captcha (NOT reCAPTCHA/hCaptcha). This is the #1 blocker for automated claiming.

## GeeTest v4 Parameters

Galxe's `PrepareParticipateInput.captcha` requires:
```json
{
  "lotNumber": "string (required)",
  "captchaOutput": "string (required)",
  "passToken": "string (required)",
  "genTime": "string (required)",
  "encryptedData": "string (optional)"
}
```

These are GeeTest v4 (GeeTest4) parameters. The `lotNumber` is the challenge session ID.

## Error Without Captcha
```
"disallowReason": "rpc error: code = InvalidArgument desc = valid quest info err: 1001:Invalid recaptcha token"
```

## Solving Options

### Option 1: 2captcha (~$3/1000 solves)
- Supports GeeTest v4: `GeeTestTaskProxyless`
- Submit: POST `https://2captcha.com/in.php` with `method=geetest_v4`, `geetestid=<captcha_id>`, `pageurl=https://app.galxe.com`
- Poll: GET `https://2captcha.com/res.php` until solved
- Returns: `lot_number`, `captcha_output`, `pass_token`, `gen_time`

### Option 2: CapSolver (~$2.50/1000 solves)
- Task type: `GeeTestTaskProxyLess`
- Submit: POST `https://api.capsolver.com/createTask`
- Returns: `lot_number`, `captcha_output`, `pass_token`, `gen_time`

### Option 3: Browser-based (manual)
1. Navigate to `https://app.galxe.com/quest/<SpaceAlias>/<CampaignID>` in Camoufox
2. Solve GeeTest captcha manually
3. Capture the captcha parameters from network request
4. Use captured params in API claim call

### Option 4: Hybrid (semi-auto)
1. Run API scan to find eligible campaigns
2. Open eligible campaign URLs in browser
3. User solves captcha manually
4. Script completes claim via API with captured captcha token

## GeeTest Sitekey Discovery

**Known Galxe GeeTest captcha_id**: `244bcb8b9846215df5af4c624a750db4`
(Source: `C0mbustibll/galxe_claimer` ⭐53, confirmed working)

GeeTest captcha on Galxe can be found by:
1. Network tab: Look for `gcaptcha4.geetest.com/load` requests → `captcha_id` param
2. JS bundle: Search for `geetest` or `captcha` initialization code
3. Known repos: `C0mbustibll/galxe_claimer` has the complete flow

### GeeTest v4 Flow (from C0mbustibll/galxe_claimer)
```python
from uuid import uuid4
import time, requests, json

GEETEST_ID = "244bcb8b9846215df5af4c624a750db4"
call = int(time.time() * 1e3)

# Step 1: Load challenge
resp = requests.get('https://gcaptcha4.geetest.com/load', params={
    'captcha_id': GEETEST_ID, 'challenge': str(uuid4()),
    'client_type': 'web', 'lang': 'et',
    'callback': f'geetest_{call}',
})
js_data = json.loads(resp.text.strip(f'geetest_{call}(').strip(')'))['data']

# Step 2: Verify with solution (W = GeeTest solve result)
resp2 = requests.get('https://gcaptcha4.geetest.com/verify', params={
    'captcha_id': GEETEST_ID, 'client_type': 'web',
    'lot_number': js_data['lot_number'], 'payload': js_data['payload'],
    'process_token': js_data['process_token'],
    'payload_protocol': '1', 'pt': '1', 'w': W,
    'callback': f'geetest_{call}',
})
completed = json.loads(resp2.text.strip(f'geetest_{call}(').strip(')'))['data']

# Step 3: Map to Galxe CaptchaInput
captcha = {
    'lotNumber': completed['lot_number'],
    'captchaOutput': completed['seccode']['captcha_output'],
    'passToken': completed['seccode']['pass_token'],
    'genTime': completed['seccode']['gen_time'],
}
```

The `W` parameter is the GeeTest slide puzzle solution — must come from a solver (2captcha/CapSolver) or manual browser interaction.

## Known Limitations

- GeeTest tokens are **domain-bound** — must solve on `app.galxe.com`
- GeeTest has **rate limiting** — too many solves trigger stricter challenges
- Headless browsers may get harder GeeTest challenges
- Camoufox may pass GeeTest without solving (anti-detection) — test first

## Integration Pattern

```python
def claim_with_captcha(token, campaign_id, address, captcha_params):
    """Claim with pre-solved GeeTest captcha."""
    from eth_account import Account
    from eth_account.messages import encode_defunct
    
    # Sign any message for the signature field
    msg = encode_defunct(text=f"claim {campaign_id}")
    signed = Account.sign_message(msg, priv_key)
    sig = "0x" + signed.signature.hex()
    
    query = """mutation PrepareParticipate($input: PrepareParticipateInput!) {
      prepareParticipate(input: $input) { allow disallowReason signature nonce }
    }"""
    
    variables = {
        "input": {
            "campaignID": campaign_id,  # capital ID!
            "address": address,
            "signature": sig,
            "captcha": {
                "lotNumber": captcha_params["lot_number"],
                "captchaOutput": captcha_params["captcha_output"],
                "passToken": captcha_params["pass_token"],
                "genTime": captcha_params["gen_time"],
            }
        }
    }
    
    return gql(query, variables, token)
```

## References
- 2captcha GeeTest docs: https://2captcha.com/p/geetest-v4
- CapSolver GeeTest docs: https://docs.capsolver.com/guide/captcha/Geetest.html
- Galxe GraphQL schema: `__type(name: "CaptchaInput")` for field discovery
