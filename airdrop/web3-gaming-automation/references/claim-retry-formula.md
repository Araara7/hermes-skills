# Claim Retry Formula (Universal untuk web3 gaming)

## Principle

Claim API sering gagal di attempt pertama karena server-side timing. Jangan langsung give up — retry dengan delay.

## Retriable vs Non-Retriable Errors

### Retriable (JANGAN hitung sebagai permanent failure):
- `"Play longer before claiming"` → main lagi 2-3 moves
- `"Transaction failed"` → server tx issue, tunggu 3s, retry
- `"Unexpected token '<'"` → server HTML response, tunggu 3s, retry
- `"Rate limited"` → tunggu lebih lama (10-30s), retry

### Non-Retriable (count as failure):
- `"Score too low!"` → main lagi sampai threshold
- `"Connect wallet first!"` → setup issue
- `"Session error, refresh page"` → refresh page
- `"bot blocked"` → anti-bot detected, ganti context
- `"Already claimed"` → sudah claim, stop

## Optimal Settings

```python
MAX_CLAIM_ATTEMPTS = 5      # Bukan 3!
CLAIM_RETRY_DELAY = 3       # detik antara retry
PRE_CLAIM_DELAY = (3, 8)    # random delay sebelum claim pertama
```

## Pola Sukses yang Terobservasi

```
Attempt 1: "Play longer" → main 2-3 moves lagi
Attempt 2: "Transaction failed" → retry (3s delay)
Attempt 3: "Transaction failed" → retry (3s delay)
Attempt 4: ✅ SUCCESS
```

## Implementation Pattern

```python
async def do_claim_with_retry(self, page, max_attempts=5):
    for attempt in range(max_attempts):
        result = await self.try_claim(page)
        
        if result.get("success"):
            return result
        
        error = result.get("error", "")
        
        # Check if retriable
        retriable = ["play longer", "transaction failed", 
                     "unexpected token", "rate limited"]
        is_retriable = any(kw in error.lower() for kw in retriable)
        
        if is_retriable:
            print(f"⏳ Retriable: {error} (retry in 3s)")
            await asyncio.sleep(3)
            continue  # Don't count as failure
        else:
            print(f"❌ Permanent fail: {error}")
            break
    
    return {"success": False, "error": "Max attempts reached"}
```

## Key Insight

**Server-side claim processing tidak instant.** Transaction memang gagal di attempt 1-3, tapi sukses di attempt 4 karena:
1. Server butuh waktu process PoW verification
2. Blockchain tx butuh waktu propagate
3. Rate limiting internal server

**Jangan assume first failure = permanent.** Always retry retriable errors.
