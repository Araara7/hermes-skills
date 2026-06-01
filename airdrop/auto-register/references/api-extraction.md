# API Extraction from Websites

Teknik untuk mengekstrak API endpoints dari website target.

## Extraction Methods

### 1. Browser Console - Performance API
```javascript
performance.getEntriesByType('resource')
  .filter(r => r.name.includes('api') || r.name.includes('graphql') || r.name.includes('json'))
  .map(r => ({ url: r.name, type: r.initiatorType }))
```

### 2. Browser Console - Pattern Matching
```javascript
const html = document.documentElement.outerHTML;
const apiPattern = /api\.php\?api=([^'"&\s]+)/gi;
let endpoints = [];
let match;
while ((match = apiPattern.exec(html)) !== null) {
  endpoints.push(match[1]);
}
```

### 3. Curl + Grep (Paling Efektif)
```bash
curl -s "https://target.com/" | grep -oE "api\.php\?[a-z_]+=[^\"'&]+" | sort | uniq
```

### 4. Fetch Pattern Extraction
```bash
curl -s "https://target.com/" | grep -oE "fetch\([^)]+\)" | head -20
```

## Bot Detection Bypass

### ⚠️ PENTING: Browser vs Curl

| Method | Bot Detection | Notes |
|--------|---------------|-------|
| `fetch()` di browser | ❌ Terblokir | Bot detection aktif |
| `XMLHttpRequest` di browser | ❌ Terblokir | Bot detection aktif |
| `curl` tanpa User-Agent | ❌ Terblokir | Bot detection aktif |
| `curl` dengan User-Agent | ✅ Berhasil | Harus pakai UA browser |

### Working Curl Pattern
```bash
curl -s \
  -H "Accept: application/json" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  "https://target.com/api.php?api=endpoint"
```

### Common API Patterns
- `api.php?api=action`
- `api.php?act=action`
- `/api/v1/resource`
- `/graphql`
- `?action=doSomething`

## Response Parsing

### JSON Response
```bash
curl -s -H "User-Agent: Mozilla/5.0" "https://target.com/api.php?api=stats" | jq .
```

### Extract Specific Fields
```bash
curl -s -H "User-Agent: Mozilla/5.0" "https://target.com/api.php?api=stats" | jq '.claims, .total_ujay'
```

## Pitfalls

1. **Bot Detection** - Selalu pakai User-Agent header
2. **Rate Limiting** - Tambah delay antara requests
3. **CORS** - API mungkin hanya bisa diakses dari domain tertentu
4. **Session Required** - Beberapa API butuh session/cookie
5. **Authentication** - Beberapa API butuh token/auth

## Workflow

1. Buka website di browser
2. Cek network tab untuk API calls
3. Extract API patterns dari HTML source
4. Test dengan curl + User-Agent
5. Parse response untuk dapat endpoint lengkap
6. Simpan endpoint untuk automation
