# CAPTCHA Solver API Reference

## 2captcha

### API Endpoints
```
Submit: POST https://2captcha.com/in.php
Result: GET https://2captcha.com/res.php
Balance: GET https://2captcha.com/res.php?action=getbalance
```

### Harga (per 1000 solve)
| Type | Harga |
|------|-------|
| reCAPTCHA v2 | $2.99 |
| reCAPTCHA v3 | $3.50 |
| hCaptcha | $3.49 |
| Turnstile | $2.50 |

### Response Codes
- `OK|XXXX` — Success, task ID returned
- `CAPCHA_NOT_READY` — Still solving
- `ERROR_WRONG_CAPTCHA_ID` — Invalid ID
- `ERROR_ZERO_BALANCE` — No funds

## CapSolver

### API Endpoints
```
Create: POST https://api.capsolver.com/createTask
Result: POST https://api.capsolver.com/getTaskResult
Balance: POST https://api.capsolver.com/getBalance
```

### Task Types
| Type | Site |
|------|------|
| ReCaptchaV2Task | Google reCAPTCHA v2 |
| ReCaptchaV3Task | Google reCAPTCHA v3 |
| HCaptchaTask | hCaptcha |
| TurnstileTask | Cloudflare Turnstile |

## Speed Comparison

| Service | Avg Speed | Success Rate |
|---------|-----------|--------------|
| 2captcha | 15-60s | 95% |
| CapSolver | 5-30s | 98% |
| AntiCaptcha | 10-40s | 96% |

## Best Practices

1. **Check balance** before submitting
2. **Handle timeout** — max 120s polling
3. **Rotate service** if error rate > 5%
4. **Log solve rate** for monitoring
5. **Use proxy** matching for better success
