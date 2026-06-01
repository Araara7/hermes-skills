# Webpack Require Shim for Galxe WASM

When loading Galxe scripts via `fetch()+eval()`, the webpack runtime (`webpack-64ade34b243dbd78.js`) fails with "Permission denied to access property autoAllocateChunkSize". Must build manual require shim.

## Working Shim Code

```javascript
// After fetch+eval of all _next scripts, chunks are in window.webpackChunk_N_E
const arr = window.webpackChunk_N_E;
const allModules = {};
for (const item of arr) {
    if (Array.isArray(item) && item[1]) Object.assign(allModules, item[1]);
}

const installed = {};
function req(id) {
    if (installed[id]) return installed[id].exports;
    const m = installed[id] = { id, loaded: false, exports: {} };
    if (allModules[id]) allModules[id](m, m.exports, req);
    m.loaded = true;
    return m.exports;
}

// Required webpack helpers (ALL needed for WASM module)
req.m = allModules;
req.o = (o, p) => Object.prototype.hasOwnProperty.call(o, p);
req.d = (e, d) => {
    for (const k in d) {
        if (req.o(d, k) && !req.o(e, k))
            Object.defineProperty(e, k, { enumerable: true, get: d[k] });
    }
};
req.r = (e) => { Object.defineProperty(e, "__esModule", { value: true }); };
req.n = (m) => {
    const g = m && m.__esModule ? () => m["default"] : () => m;
    req.d(g, { a: g });
    return g;
};
req.e = () => Promise.resolve();
req.f = {};
req.p = "https://b.galxestatic.com/new-web-prd/_next/";
req.U = URL;  // KEY: URL constructor (not a string!)
req.O = (r, c, f) => { if (!c) return r; f(); return r; };
req.C = (c) => c;
req.g = globalThis;
req.b = "https://app.galxe.com/";
```

## Why Each Helper is Needed

| Helper | Purpose | Error if missing |
|--------|---------|-----------------|
| `req.d` | Define property getters on exports | `t.d is not a function` |
| `req.o` | hasOwnProperty check | Used by `req.d` |
| `req.r` | Mark as ES module | Module format detection |
| `req.n` | Get default export | Import resolution |
| `req.U` | **URL constructor** | `__webpack_require__.U is not a constructor` |
| `req.O` | On-chunks-loaded callback | Chunk loading |
| `req.p` | Public path (CDN base) | WASM binary URL resolution |
| `req.g` | Global object reference | Window access |
| `req.b` | Base URI | Relative URL resolution |

## Critical: `req.U = URL`

The WASM module uses `new req.U(path, base)` to construct URLs for fetching the WASM binary. Must be the actual `URL` constructor, NOT a string or function returning string.

## import.meta.url Fix

When eval'ing fetched scripts, `import.meta.url` is undefined. Fix before eval:

```python
code = code.replace('import.meta.url', json.dumps(script_url))
```

## Script Load Order

1. Fetch all `script[src*="_next"]` URLs
2. Replace `import.meta.url` in each
3. `eval()` each script
4. Chunks populate `window.webpackChunk_N_E`
5. Build require shim
6. Load WASM module: `req(95088)`
7. Init: `await mod.Ay()`
8. Generate: `await mod.Qc(apiName, timestamp)`
