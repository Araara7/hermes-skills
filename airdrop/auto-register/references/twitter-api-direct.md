# Twitter API Direct Access

## Overview
Mengakses Twitter API langsung menggunakan auth_token dan ct0 cookie, tanpa xurl CLI.

## Credentials

### auth_token
- Dari cookie browser
- Format: hex string (40 karakter)
- Expire: ~2 tahun

### ct0
- CSRF token
- Format: hex string (32 karakter)
- Expire: per session

### Bearer Token
```
AAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA
```
- Ini adalah app-level bearer token Twitter (public)

## Headers

```python
headers = {
    'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
    'x-csrf-token': ct0,
    'cookie': f'auth_token={auth_token}; ct0={ct0}',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'x-twitter-active-user': 'yes',
    'x-twitter-auth-type': 'OAuth2Session',
    'x-twitter-client-language': 'en',
}
```

## Common Operations

### Follow User
```python
# 1. Get user ID
resp = requests.get(
    'https://x.com/i/api/graphql/xmU6X_CKVnQ5lSrCbAmJsg/UserByScreenName?variables=%7B%22screen_name%22%3A%22USERNAME%22%2C%22withSafetyModeUserFields%22%3Atrue%7D&features=%7B%22hidden_profile_subscriptions_enabled%22%3Atrue%2C%22rweb_tipjar_consumption_enabled%22%3Atrue%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_enabled%22%3Afalse%2C%22subscriptions_verification_info_is_identity_verified_enabled%22%3Atrue%2C%22subscriptions_verification_info_verified_since_enabled%22%3Atrue%2C%22highlights_tweets_tab_ui_enabled%22%3Atrue%2C%22responsive_web_twitter_article_notes_tab_enabled%22%3Atrue%2C%22subscriptions_feature_can_gift_premium%22%3Atrue%2C%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%7D',
    headers=headers
)
user_id = resp.json()['data']['user']['result']['rest_id']

# 2. Follow
follow_resp = requests.post(
    'https://x.com/i/api/1.1/friendships/create.json',
    headers={**headers, 'content-type': 'application/x-www-form-urlencoded'},
    data={'user_id': user_id}
)
```

### Like Tweet
```python
resp = requests.post(
    'https://x.com/i/api/1.1/favorites/create.json',
    headers={**headers, 'content-type': 'application/x-www-form-urlencoded'},
    data={'id': tweet_id}
)
```

### Retweet
```python
resp = requests.post(
    f'https://x.com/i/api/1.1/statuses/retweet/{tweet_id}.json',
    headers={**headers, 'content-type': 'application/x-www-form-urlencoded'}
)
```

### Post Tweet
```python
resp = requests.post(
    'https://x.com/i/api/1.1/statuses/update.json',
    headers={**headers, 'content-type': 'application/x-www-form-urlencoded'},
    data={'status': 'Tweet text here'}
)
```

## Session File Format

```json
{
  "twitter": {
    "auth_token": "...",
    "ct0": "...",
    "user_id": "...",
    "status": "connected"
  }
}
```

## Storage Location
```
~/airdrop-agent/config/credentials/twitter_session.json
```

## Best Practices

1. **Rate Limiting** - Twitter punya rate limit per endpoint
2. **Error Handling** - Cek response status code
3. **Session Refresh** - ct0 expire per session, auth_token ~2 tahun
4. **User-Agent** - Selalu gunakan User-Agent standar
5. **CSRF Token** - ct0 harus dikirim untuk write operations

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| 401 Unauthorized | Cek auth_token, mungkin expired |
| 403 Forbidden | Cek ct0, mungkin expired |
| Rate limit | Tunggu 15 menit |
| User not found | Cek username spelling |
