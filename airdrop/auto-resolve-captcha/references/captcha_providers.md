# CAPTCHA Service Providers Reference

## Pricing Comparison (per 1000 solves)

| Service | reCAPTCHA v2 | reCAPTCHA v3 | hCaptcha | Turnstile | Speed |
|---------|--------------|--------------|----------|-----------|-------|
| 2captcha | $2.99 | $3.99 | $3.99 | N/A | 15-60s |
| CapSolver | $2.50 | $3.50 | $3.50 | $2.50 | 5-30s |
| AntiCaptcha | $2.00 | $3.00 | $3.00 | N/A | 10-40s |
| DeathByCaptcha | $1.39 | $2.39 | $2.39 | N/A | 15-90s |
| SolveCaptcha | $2.50 | $3.50 | $3.50 | N/A | 10-50s |

## API Examples

### 2captcha
```python
import requests

API_KEY = "your_api_key"

# Submit task
resp = requests.post("https://2captcha.com/in.php", data={
    "key": API_KEY,
    "method": "userrecaptcha",
    "googlekey": "site_key",
    "pageurl": "https://example.com",
    "json": 1
}).json()

task_id = resp["request"]

# Get result
result = requests.get("https://2captcha.com/res.php", params={
    "key": API_KEY,
    "action": "get",
    "id": task_id,
    "json": 1
}).json()

token = result["request"]
```

### CapSolver
```python
import requests

API_KEY = "your_api_key"

# Create task
resp = requests.post("https://api.capsolver.com/createTask", json={
    "clientKey": API_KEY,
    "task": {
        "type": "ReCaptchaV2Task",
        "websiteURL": "https://example.com",
        "websiteKey": "site_key"
    }
}).json()

task_id = resp["taskId"]

# Get result
result = requests.post("https://api.capsolver.com/getTaskResult", json={
    "clientKey": API_KEY,
    "taskId": task_id
}).json()

token = result["solution"]["gRecaptchaResponse"]
```

## Supported Types

| Type | 2captcha | CapSolver | AntiCaptcha | Camoufox (Lokal) |
|------|----------|-----------|-------------|------------------|
| reCAPTCHA v2 | ✅ | ✅ | ✅ | ❌ |
| reCAPTCHA v3 | ✅ | ✅ | ✅ | ❌ |
| hCaptcha | ✅ | ✅ | ✅ | ❌ |
| Turnstile | ❌ | ✅ | ❌ | ✅ GRATIS |
| FunCaptcha | ✅ | ✅ | ✅ | ❌ |
| Image CAPTCHA | ✅ | ✅ | ✅ | ❌ (pakai Tesseract) |

## Best Practices

1. **Balance check** - Verify API balance before batch
2. **Timeout handling** - Set 120s max wait
3. **Error retry** - Retry on transient errors
4. **Rotate services** - Use backup if primary fails
5. **Monitor rates** - Track success/failure ratio
