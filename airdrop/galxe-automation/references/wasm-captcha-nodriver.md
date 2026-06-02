# Galxe WASM Captcha — Nodriver Findings (Jun 2026)

## Webpack Module Access
Galxe uses Next.js with `webpackChunk_N_E` for module loading.

### Access Pattern
```python
await tab.evaluate("""
(() => {
    let __webpack_require__;
    window.webpackChunk_N_E.push([
        ['__test__'], {}, (req) => { __webpack_require__ = req; }
    ]);
    // Now __webpack_require__ is available
    const mod = __webpack_require__('95088');
    window.__captcha_mod = mod;
})()
""")
```

### Module 95088 Exports
- `Ay` — WASM init function (returns Promise → WASM memory object)
- `Qc` — Captcha generate function (needs WASM initialized first)

### Init + Generate Flow
```python
# Step 1: Init WASM
await tab.evaluate("""
window.__captcha_result = 'initing';
window.__captcha_mod.Ay().then(wasm => {
    window.__wasm = wasm;
    window.__captcha_result = 'wasm_ready';
}).catch(e => {
    window.__captcha_result = JSON.stringify({error: e.message});
});
""")
await asyncio.sleep(5)

# Step 2: Check result
result = await tab.evaluate("window.__captcha_result")
# If "wasm_ready", can call Qc
# If error, WASM binary not loaded (lazy loading issue)
```

### Lazy Loading Issue
WASM binary (`wasm_lib_bg.*.wasm`) is NOT loaded on page load. It's only fetched when:
1. User triggers a claim/verify action
2. Galxe's frontend calls the captcha module
3. The binary is fetched from CDN: `https://b.galxestatic.com/new-web-prd/_next/static/media/wasm_lib_bg.*.wasm`

**Workaround:** Use Chromium Playwright (not nodriver) for WASM captcha — it handles the lazy loading properly via the existing `galxe_captcha_solver.py` script.

## CDN Paths
- Chunk: `https://b.galxestatic.com/new-web-prd/_next/static/chunks/64590-*.js`
- WASM: `https://b.galxestatic.com/new-web-prd/_next/static/media/wasm_lib_bg.*.wasm`

## Performance API Check
```python
perf = await tab.evaluate("""
(() => {
    const entries = performance.getEntriesByType('resource');
    const wasmEntries = entries.filter(e => e.name.includes('wasm'));
    return JSON.stringify(wasmEntries.map(e => ({name: e.name, type: e.initiatorType})));
})()
""")
# Empty array = WASM not loaded yet
```

## Best Approach
1. **nodriver** for anti-detect navigation + cookie management
2. **Chromium Playwright** for WASM captcha solving (subprocess)
3. **API** for task verification with captcha tokens
