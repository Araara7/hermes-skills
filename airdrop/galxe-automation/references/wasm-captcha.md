# Galxe WASM Captcha Internals (Jun 2026)

Galxe migrated from GeeTest v4 to a Rust→WASM captcha system. The WASM binary generates captcha proofs using browser fingerprinting.

**→ For the WORKING Chromium headless solution, see `wasm-captcha-chromium.md`**

## CDN Paths
- **Chunk**: `https://b.galxestatic.com/new-web-prd/_next/static/chunks/64590-bf86373c43b357a2.js`
- **WASM binary**: `https://b.galxestatic.com/new-web-prd/_next/static/media/wasm_lib_bg.9ba64712.wasm`

Hashes in filenames change per deploy. Search for `geetest_encrypted` in chunks to find the current one.

## Module Structure

Webpack module `95088` in chunk `64590`:
- Export `Ay` (default) — WASM initializer. Takes WASM binary bytes, returns after `__wbindgen_start()`.
- Export `Qc` (`generateData`) — Captcha generator. Takes `(apiName, genTime)`, returns JSON string.

`generateData` internals:
```javascript
let i = Math.floor(Date.now() / 1000).toString();
let o = JSON.parse(await generate_data(undefined, apiName, i));
return {
    lotNumber: sha256(apiName),       // e.g. sha256("PrepareParticipate")
    captchaOutput: o.geetest_encrypted, // WASM-generated proof
    passToken: sha256(i),              // sha256 of unix timestamp
    genTime: i,
    encryptedData: o.encrypted_data || ""
};
```

`generate_data` (WASM export): `fn(f64_array: Option<Vec<f64>>, api_name: String, extra: Option<String>) -> String`

## Captcha Field Mapping → CaptchaInput
- `lotNumber` ← `sha256(apiName)` — deterministic, same for all requests
- `captchaOutput` ← `wasm_output.geetest_encrypted` — the real proof
- `passToken` ← `sha256(genTime)` — deterministic per timestamp
- `genTime` ← unix timestamp in seconds (string)
- `encryptedData` ← `wasm_output.encrypted_data` (optional, when `shouldEncrypt: true`)

## SHA256 Library
Required for lotNumber/passToken. Local copy: `~/airdrop-agent/scripts/sha256.min.js`
CDN: `https://cdnjs.cloudflare.com/ajax/libs/js-sha256/0.11.0/sha256.min.js`

## GeeTest Legacy (pre-WASM)
Old GeeTest captcha_id for Galxe: `244bcb8b9846215df5af4c624a750db4`
Old endpoints: `gcaptcha4.geetest.com/load`, `gcaptcha4.geetest.com/verify`
Reference: `C0mbustibll/galxe_claimer` repo (cloned at `~/airdrop-agent/galxe_claimer/`)

## Fingerprint Detection — Camoufox vs Chromium

**Camoufox FAILS** with `"Fingerprint detection failed: JsValue(Promise)"` — anti-fingerprinting interceptors return Promises where synchronous values expected.

**Chromium headless WORKS** — no API interception, WASM gets correct synchronous responses.

See `wasm-captcha-chromium.md` for full error catalog and working implementation.

## Token NOT IP-Bound
The WASM captcha token is NOT tied to the generating IP. A browser can generate it, and the API can use it from a different IP. This means: generate in Chromium on VPS → use in API call from same IP.
