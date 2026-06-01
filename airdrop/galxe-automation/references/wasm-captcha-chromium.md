# Galxe WASM Captcha — Chromium Headless Solution (Jun 2026)

## Breakthrough: Chromium Headless WORKS ✅

After extensive debugging (V1-V21 scripts), discovered that **Playwright Chromium headless** generates valid WASM captcha tokens. Camoufox fails due to anti-fingerprinting API interception.

## Root Cause Chain

1. **Camoufox modifies browser APIs** (canvas, WebGL, audio) for anti-detection
2. WASM's Rust code calls these APIs synchronously via wasm-bindgen
3. Camoufox interceptors return `JsValue(Promise)` instead of resolved values
4. WASM gets Promise objects → "Fingerprint detection failed: JsValue(Promise)"

Chromium doesn't modify these APIs → WASM gets correct values → captcha generates successfully.

## Working Implementation: `scripts/galxe_captcha_solver.py`

### Approach
1. Load Galxe page in Chromium headless (`wait_until="commit"`)
2. Wait 15-20s for scripts to appear in DOM
3. Fetch+eval all `_next` scripts manually (they don't auto-execute in headless)
4. Replace `import.meta.url` with script URL before eval (undefined in eval context)
5. Build manual webpack require shim (runtime script blocked by permission error)
6. Load module 95088 (WASM), call `Ay()` (init), then `Qc(apiName, genTime)`
7. Parse JSON response → `{lotNumber, captchaOutput, passToken, genTime, encryptedData}`

### Key Code Patterns

**Fetch+eval scripts:**
```javascript
const scripts = document.querySelectorAll('script[src*="_next"]');
for (const s of Array.from(scripts)) {
    const r = await fetch(s.src);
    if (r.ok) {
        let code = await r.text();
        code = code.replace(/import\.meta\.url/g, JSON.stringify(s.src));
        eval(code);
    }
}
```

**Webpack require shim (all helpers required):**
```javascript
function req(id) {
    if (installed[id]) return installed[id].exports;
    const m = installed[id] = { id, loaded: false, exports: {} };
    if (allModules[id]) allModules[id](m, m.exports, req);
    m.loaded = true; return m.exports;
}
req.m = allModules;
req.o = (o, p) => Object.prototype.hasOwnProperty.call(o, p);
req.d = (e, d) => { /* define getters */ };
req.r = (e) => { Object.defineProperty(e, "__esModule", { value: true }); };
req.n = (m) => { /* get default export */ };
req.e = () => Promise.resolve();
req.f = {};
req.p = "https://b.galxestatic.com/new-web-prd/_next/";
req.U = URL;  // CRITICAL: must be URL constructor, not string function
req.O = (r, c, f) => { if (!c) return r; f(); return r; };
req.C = (c) => c;
req.g = globalThis;
req.b = "https://app.galxe.com/";
```

**Captcha generation:**
```javascript
const sha = req(25091);   // SHA256 module
const wasm = req(95088);  // WASM module
await wasm.Ay();          // Init WASM binary
let i = Math.floor(Date.now() / 1000).toString();
let raw = await wasm.Qc(apiName, i);  // Generate captcha
let o = JSON.parse(raw);
```

## Errors Encountered & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `webpackChunk_N_E` undefined | Scripts don't auto-execute in headless | Manual fetch+eval |
| `import.meta.url` undefined | Eval context has no module scope | Replace with script URL string |
| `Permission denied: autoAllocateChunkSize` | Webpack runtime script blocked | Skip it, build manual require shim |
| `__webpack_require__.U is not a constructor` | `req.U` was string function | Set `req.U = URL` (constructor) |
| `t.d is not a function` | Missing webpack helper | Add `req.d` (define getters) |
| `Fingerprint detection failed: JsValue(Promise)` | Camoufox anti-fingerprint | Switch to Chromium |
| `JSON.parse: unexpected character` | Qc returns error string, not JSON | Check Qc output before parsing |

## Captcha Field Mapping → CaptchaInput

All fields required by Galxe's `CaptchaInput` GraphQL type:
- `lotNumber` = `sha256(apiName)` — deterministic, same for all requests with same apiName
- `captchaOutput` = `wasm_output.geetest_encrypted` — the real proof (base64)
- `passToken` = `sha256(genTime)` — deterministic per timestamp
- `genTime` = unix timestamp in seconds (string)
- `encryptedData` = `wasm_output.encrypted_data` (optional, when `shouldEncrypt: true`)

## Token NOT IP-Bound
The WASM captcha token is NOT tied to the generating IP. Generate in Chromium on VPS → use in API call from same or different IP.

## CDN Paths
- Base: `https://b.galxestatic.com/new-web-prd/_next/`
- Chunks: `_next/static/chunks/<id>-<hash>.js`
- WASM: `_next/static/media/wasm_lib_bg.<hash>.wasm`
- Hashes change per deploy; search for `geetest_encrypted` in chunk source to find current captcha module

## Module IDs
- **Module 28021** — geetest_encrypted entry point, exports `H` (the builder function)
- **Module 95088** — WASM wrapper, exports `Ay` (init) and `Qc` (generate)
- **Module 25091** — SHA256 helper, exports `sha256`
- Module IDs may change per deploy; search by function content, not hardcoded ID
