# GeeTest v4 API Reference

## Endpoints
- Load challenge: `GET https://gcaptcha4.geetest.com/load`
- Verify solution: `GET https://gcaptcha4.geetest.com/verify`

## Parameters

### Load
| Param | Type | Description |
|-------|------|-------------|
| captcha_id | string | Site-specific GeeTest ID |
| challenge | string | UUID v4, unique per request |
| client_type | string | "web" |
| lang | string | "et" (English) |
| callback | string | JSONP callback: `geetest_{timestamp}` |

### Verify
| Param | Type | Description |
|-------|------|-------------|
| captcha_id | string | Same as load |
| client_type | string | "web" |
| lot_number | string | From load response |
| payload | string | From load response |
| process_token | string | From load response |
| payload_protocol | string | "1" |
| pt | string | "1" |
| w | string | **Solution from solver** |
| callback | string | JSONP callback |

## Response Format (JSONP)
```javascript
geetest_1234567890({
    "status": "success",
    "data": {
        "lot_number": "...",
        "payload": "...",
        "process_token": "...",
        // After verify, also has:
        "seccode": {
            "captcha_output": "...",
            "pass_token": "...",
            "gen_time": "..."
        }
    }
})
```

## 2captcha API v2 for GeeTest v4

### Create Task
```
POST https://api.2captcha.com/createTask
{
    "clientKey": "API_KEY",
    "task": {
        "type": "GeeTestTaskProxyless",
        "websiteURL": "https://app.galxe.com",
        "gt": "244bcb8b9846215df5af4c624a750db4",
        "version": 4
    }
}
```

### Get Result
```
POST https://api.2captcha.com/getTaskResult
{
    "clientKey": "API_KEY",
    "taskId": 12345
}
```

### Solution Format
```json
{
    "status": "ready",
    "solution": {
        "captcha_id": "...",
        "lot_number": "...",
        "pass_token": "...",
        "gen_time": "...",
        "captcha_output": "..."
    }
}
```

## CapSolver for GeeTest v4

### Create Task
```
POST https://api.capsolver.com/createTask
{
    "clientKey": "API_KEY",
    "task": {
        "type": "GeeTestTaskProxyLess",
        "websiteURL": "https://app.galxe.com",
        "gt": "244bcb8b9846215df5af4c624a750db4",
        "version": 4
    }
}
```

## Known Galxe GeeTest ID
`244bcb8b9846215df5af4c624a750db4`

Source: `C0mbustibll/galxe_claimer` (⭐53, Python, updated 2026-03)
