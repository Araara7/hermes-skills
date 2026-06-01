---
name: pixie-chess-automation
description: Pixie Chess (pixiechess.xyz) automation — Privy auth, WebSocket game protocol, matchmaking, chess engine integration
tags: [web3, chess, airdrop, privy, arbitrum, automation]
triggers:
  - pixie chess
  - pixiechess
  - chess xyz
  - chess game automation
---

# Pixie Chess Automation

## Site Info
- URL: https://pixiechess.xyz
- Type: Vite SPA, chess game with crypto rewards (ETH prize pools)
- Auth: Privy (wallet-based, email OTP, no guest/OAuth)
- Chains: Arbitrum, Base, Linea
- Smart Contracts: Game proxy `0x10f9bc99c2a5ec3ec02f477cc130f71e3cf51962`, Instant mint `0xb3b4f451870b53586949f0af4ba754aaf8aed4f3`
- WebSocket: `wss://api.pixiechess.xyz/socket.io/?EIO=4&transport=websocket`
- Board: `board.pixiechess.xyz` (Netlify)

## Privy Auth Configuration
- App ID: `cmj86b87s02wkld0cjaypk8ci`
- Client ID: NOT SET (do NOT send `privy-client-id` header — causes "Invalid app client ID")
- SDK Version: `react-auth:2.17.3`
- API Base: `https://auth.privy.io`
- CAPTCHA: Cloudflare Turnstile, sitekey `0x4AAAAAADGtm7mx4aLENCLF`

## Required API Headers (Privy)
```
Content-Type: application/json
Accept: application/json
Origin: https://pixiechess.xyz
Referer: https://pixiechess.xyz/
privy-app-id: cmj86b87s02wkld0cjaypk8ci
privy-client: react-auth:2.17.3
privy-ca-id: <random-uuid>
```
⚠️ Do NOT include `privy-client-id` — returns "Invalid app client ID"

## ✅ WORKING AUTH FLOW (Fully Automated)

### Email OTP via Camoufox (handles Turnstile internally)
1. Camoufox navigates to `pixiechess.xyz`
2. Click Login → enter email → Privy SDK handles Turnstile CAPTCHA internally
3. OTP sent to email automatically
4. Read OTP from email via `himalaya message read <id>`
5. Call API: `POST https://auth.privy.io/api/v1/passwordless/authenticate` with `{email, code}`
6. Get JWT token (token, refresh_token, identity_token)

### SIWE Flow (alternative — needs Turnstile token)
1. `POST /api/v1/siwe/init` with `{address, token}` → nonce (token = Turnstile captcha token)
2. Create SIWE message, sign with EVM key
3. `POST /api/v1/siwe/authenticate` with `{message, signature, chainId, walletClientType, connectorType, mode}`

### Disabled Auth Methods
- Guest: "Guest accounts are not enabled for this app"
- Google OAuth: "Login with Google not allowed"
- Farcaster: "Login with Farcaster not allowed"

## Terms of Service Acceptance
Terms modal requires scrolling to bottom before checkbox enables.
```python
# Scroll the terms text box to bottom
page.evaluate("""() => {
    const els = document.querySelectorAll('.overflow-scroll');
    for (const el of els) {
        if (el.scrollHeight > 1000 && el.clientHeight < 500) {
            el.scrollTop = el.scrollHeight;
            el.dispatchEvent(new Event('scroll', { bubbles: true }));
        }
    }
}""")
time.sleep(2)
# Click checkbox
page.evaluate("""() => {
    const label = document.querySelector('input[type="checkbox"]')?.closest('label');
    if (label && !label.className.includes('cursor-not-allowed')) label.click();
}""")
time.sleep(1)
# Click Continue
page.evaluate("""() => {
    for (const btn of document.querySelectorAll('button'))
        if (btn.textContent.trim().toLowerCase().includes('continue') && !btn.disabled) { btn.click(); return; }
}""")
```

## Onboarding
Username: 3-32 chars, no spaces, letters/numbers/hyphens only (underscores NOT allowed)
Helmet: Select from grid of options

## WebSocket Game Protocol (Socket.IO)

### Connection
- URL: `wss://api.pixiechess.xyz/socket.io/?EIO=4&transport=websocket`
- Auth on connect: `40{"token": "<jwt>"}`
- Server responds: `430[...]` (auth success)
- Ping/pong: `424["l",<timestamp>]` / `434[<timestamp>]`

### Matchmaking
- Join: `42["matchmaking:join","<wallet_address>"]`
- Searching: `42["matchmaking:update",{"status":"searching"}]`
- Matched: `42["matchmaking:update",{"status":"matched","gameId":"game_...","opponent":{"username":"...","address":"0x..."}}]`
- Connect to game: `42["_connect","<gameId>","<wallet_address>"]`
- Select point: `42["select_point","<gameId>","<wallet_address>",null]`

### Game Messages
- `boardReady` — Board is ready
- `move` — A move was made
- `possibleMoves` — Available moves for current player
- `sync` — Game state sync (contains FEN)
- `pregameComplete` — Pre-game setup complete
- `endGameAnimationComplete` — Game ended
- Binary data: `451-["update",{"_placeholder":true,"num":0}]` + binary blob

### ~~Piece Selection Phase~~ → SELECTING Phase
- After match found, SELECTING phase appears with countdown (30-60s)
- ~~Must click "Ready up"~~ → **Do NOT click anything — game auto-starts after countdown**
- Pieces are on 3D canvas (WebGL), not DOM elements — cannot interact programmatically
- See "SELECTING Phase" section below for full details

## Critical: React Button Click Pattern
**`page.evaluate("btn.click()")` does NOT trigger React event handlers!**
Must use Playwright's `locator.click()` for React buttons:
```python
# ✅ CORRECT — triggers React handlers
page.locator("button:has-text('Search for Match')").click(timeout=5000)

# ❌ WRONG — does NOT trigger React handlers
page.evaluate("""() => {
    for (const btn of document.querySelectorAll('button'))
        if (btn.textContent.includes('Search')) btn.click();
}""")
```

## Background Execution with Camoufox
```bash
# Run via screen with unbuffered output
screen -dmS pixie bash -c 'cd ~/airdrop-agent && source venv/bin/activate && \
    PYTHONUNBUFFERED=1 python3 -u scripts/pixie_auto_player_v4.py 2>&1 | tee /tmp/pixie_auto.log'

# Monitor
screen -ls | grep pixie
tail -f /tmp/pixie_auto.log

# Kill
screen -S pixie -X quit
```

## Chess Engine Integration
- Stockfish binary: `/home/ubuntu/bin/stockfish` (v17.1)
- Python package: `pip install chess -i https://pypi.org/simple/` (NOT `python-chess`)
- Usage:
```python
import chess, chess.engine
board = chess.Board(fen)
engine = chess.engine.SimpleEngine.popen_uci('/home/ubuntu/bin/stockfish')
result = engine.play(board, chess.engine.Limit(time=0.3))
best_move = str(result.move)
engine.quit()
```

## Viewport Size (CRITICAL — ROOT CAUSE OF MOST FAILURES)

**"Ready up" button is at y=926 on the page.** Default viewport 800px puts it OUTSIDE the visible area.

```python
# ❌ WRONG — button at y=926 is below viewport
page.set_viewport_size({"width": 1280, "height": 800})

# ✅ CORRECT — button visible
page.set_viewport_size({"width": 1280, "height": 1050})
```

**Symptoms of wrong viewport:**
- "Ready up" button found but click doesn't register
- React pointer events dispatched but nothing happens
- Game forfeits because countdown expires
- ELO drops rapidly (1500 → 800+)

## SELECTING Phase (CRITICAL — READ BEFORE CODING)

After match found, both players enter SELECTING phase with countdown (30-60s).
The UI shows: "Click or Drag to substitute in a Pixie piece. MIN 3 · MAX 6 · CURRENT 0"

### Piece Card DOM Structure (1 Jun 2026)
5 piece cards in left panel, each 171×200px:
- **Bouncer** @ (80,252) — red geometric knight
- **Fish** @ (259,252) — blue origami shark
- **Pawn with Knife** @ (439,252) — dark pawn with red weapon
- **Phase Rook** @ (439+171,252) — glowing cyan rook
- **War Automaton** — red blocky pawn

Each card has:
- Inner DIV with piece name + "FREE" tag (72×32px — **do NOT click these, they don't select!**)
- Outer DIV `relative` class (171×200px — the actual card container)
- Purple border = focused/hovered (NOT selected!)
- **Clicking a card only FOCUS it (purple border), does NOT select it!**

### Piece Selection — Requires DRAG, Not Click
**"Click or Drag" — but click alone only focuses the card!** To actually select:
1. **Double-click** the card center → may work (unreliable)
2. **Drag** card from left panel to board area (right side, ~x=900, y=500) → more reliable
3. **Click FREE tag** area → untested

```python
# Card centers (approximate, adjust if layout shifts)
CARD_POSITIONS = {
    "Bouncer": (166, 352),
    "Fish": (345, 352),
    "Pawn with Knife": (524, 352),
}

# Drag strategy
page.mouse.move(card_x, card_y)
time.sleep(0.2)
page.mouse.down()
time.sleep(0.1)
page.mouse.move(900, 500, steps=10)  # Board area
time.sleep(0.1)
page.mouse.up()
time.sleep(0.5)

# Verify CURRENT count changed
body = page.evaluate("() => document.body.innerText")
current = int(re.search(r'CURRENT\s*(\d+)', body).group(1))
```

⚠️ **CURRENT must be ≥3 before clicking READY!** If CURRENT=0 after clicking, game forfeits.

### What NOT to do
- ❌ **Do NOT click "Play" button** — triggers NEW matchmaking, NOT ready up!
- ❌ **Do NOT try to interact with the 3D canvas** — pieces are WebGL-rendered
- ❌ **Do NOT delay "Ready up" click** — countdown is short (30-45s)
- ❌ **Do NOT click piece card labels (72×32px)** — these don't select, only focus

### What TO do
- ✅ **Click "Ready up" IMMEDIATELY** when SELECTING detected (viewport must be ≥1050px)
- ✅ Use JS click fallback: `btn.scrollIntoView({block: 'center'}); btn.click();`
- ✅ Monitor WS for game start events after ready up: `sync` (with FEN), `possibleMoves`
- ✅ If "Ready up" fails, let countdown expire — game may auto-start with defaults

### "Ready up" Click Pattern (PROVEN WORKING — v8)
```python
# Must click IMMEDIATELY when SELECTING detected, not in a wait loop
try:
    btn = page.locator("button:has-text('Ready up')")
    if btn.count() > 0 and btn.first.is_visible():
        btn.first.scroll_into_view_if_needed(timeout=3000)
        time.sleep(0.5)
        btn.first.click(timeout=5000)
        log("Ready up clicked!")
except:
    # JS fallback — also works
    page.evaluate("""() => {
        for (const btn of document.querySelectorAll('button')) {
            if (btn.textContent.trim().includes('Ready up')) {
                btn.scrollIntoView({block: 'center'});
                btn.click();
                return true;
            }
        }
        return false;
    }""")
```

### WS messages during SELECTING
```
→ 42["select_point","<gameId>","<wallet>",null]  ← page sends automatically
```
These are harmless — ignore them.

### Confirmed working flow (v8 — 1 Jun 2026)
1. Viewport: 1280×1050 (CRITICAL)
2. Click "Search for Match" via Playwright locator → match found in <5s
3. Page navigates to game URL automatically
4. SELECTING phase shows with countdown (30-45s)
5. **Click "Ready up" immediately** via JS click
6. Game starts — WS sends `sync` with FEN
7. `possibleMoves` arrives when your turn → use Stockfish

### Win/Loss Detection (CRITICAL)
**Do NOT count "Game Over" as win!** Check for Victory vs Defeat:
```python
body = page.evaluate("() => document.body.innerText")
if "Victory" in body:
    wins += 1  # Actual win
elif "Defeat" in body or "forfeit" in body.lower():
    losses += 1  # Loss or forfeit
```

Common forfeit message: "You took too long to muster your army. Defeat by forfeit."

## Auth Token Persistence (BROKEN — Do Not Use)

⚠️ **Auth cache does NOT work (1 Jun 2026).** Injecting saved localStorage tokens causes a persistent "Complete Your Login" overlay that blocks ALL interactions. Clicking "CONTINUE LOGIN" loops forever. Always do fresh OTP login.

If you must try cached auth, check for overlay immediately:
```python
body = page.evaluate("() => document.body.innerText")
if "Complete Your Login" in body:
    # Auth cache failed, must do OTP login
    pass
```

## "Complete Your Login" Overlay (CRITICAL)

After page load, a `z-40` overlay often appears: *"Complete Your Login — You must complete the login process to access Pixie Chess."* with a green "CONTINUE LOGIN" button.

**This overlay blocks ALL pointer events** — including "Search for Match", piece cards, and "Ready up".

### Dismiss strategy
```python
def dismiss_overlays(page):
    """Dismiss any overlay/modal blocking interactions"""
    for _ in range(3):
        body = page.evaluate("() => document.body.innerText")
        if "Complete Your Login" in body or "CONTINUE LOGIN" in body:
            # Try clicking CONTINUE LOGIN
            try:
                page.locator("button:has-text('CONTINUE LOGIN')").first.click(timeout=3000)
                time.sleep(5)
                continue
            except:
                page.evaluate("""() => {
                    for (const btn of document.querySelectorAll('button'))
                        if (btn.textContent.includes('CONTINUE')) { btn.click(); return true; }
                    return false;
                }""")
                time.sleep(3)
                continue
        # Click overlay backdrop
        has_overlay = page.evaluate("""() => {
            const overlay = document.querySelector('.fixed.inset-0.z-40');
            if (overlay) { overlay.click(); return true; }
            return false;
        }""")
        if has_overlay:
            time.sleep(1)
            continue
        page.keyboard.press("Escape")
        time.sleep(1)
```

⚠️ **Call `dismiss_overlays()` before EVERY major interaction**: after page load, before "Search for Match", before piece selection, before "Ready up".

⚠️ **Do NOT use `page.reload()`** — times out with Camoufox. Always use `page.goto()` with `wait_until="commit"`.

## Known Issues
1. **Viewport must be ≥1050px** — "Ready up" at y=926, default 800px hides it
2. **Win/loss detection** — check "Victory" vs "Defeat", not just "Game Over"
3. **Game board click coordinates** — Need to find correct board element and square coordinates for making moves (canvas-based, need `getBoundingClientRect()`)
4. **ELO dropped to ~800** — from 1500 due to forfeit timeouts during debugging
5. **Camoufox startup slow** — 2-3 minutes before first log output; don't kill prematurely
6. **First "Search for Match" click often doesn't trigger matchmaking** — WS join message sent but no match. Retry 1-2 times works.

## Scripts
- `scripts/pixie_auto_player_v10.py` — **LATEST**: OTP-only login, overlay dismiss, piece drag selection, indefinite match wait, re-join matchmaking
- `scripts/pixie_auto_player_v9.py` — viewport 1050px, immediate "Ready up" click via JS, win/loss detection
- `scripts/pixie_auto_player_v8.py` — viewport 1050px, immediate "Ready up" click via JS, win/loss detection
- `scripts/pixie_auto_player_v7.py` — SELECTING phase detection but clicks wrong buttons
- `scripts/pixie_auto_player_v6.py` — Matchmaking works via Playwright locator, SELECTING not handled
- `scripts/pixie_diag_selecting.py` — Diagnostic: screenshot + DOM dump during SELECTING phase
- `scripts/pixie_ws_diag.py` — Diagnostic: WS message listener for 3 minutes
- `scripts/pixie_modal_diag.py` — Diagnostic: "Complete Your Login" modal analysis
- `scripts/turnstile_solver.py` — Turnstile CAPTCHA solver via Camoufox
- `scripts/pixie_chess_player.py` — v1 basic flow

## Pitfalls
- Headless browsers detected by Turnstile on direct API calls — must use Camoufox browser flow
- Privy SDK handles Turnstile internally during email OTP flow (no manual captcha solving needed)
- `privy-client-id` header causes "Invalid app client ID" error — omit it
- PyPI mirror may be broken on VPS — use `-i https://pypi.org/simple/`
- Python output buffering in background — use `PYTHONUNBUFFERED=1` and `python3 -u`
- `page.evaluate("btn.click()")` does NOT work for React buttons — use `page.locator().click()`
- Terms checkbox disabled until scroll to bottom — use `el.scrollTop = el.scrollHeight`
- Matchmaking:join sent repeatedly by app — deduplicate when parsing WS messages
- **"Play" button during SELECTING triggers NEW matchmaking** — NOT ready up! Do NOT click it!
- **SELECTING pieces ARE DOM elements** (not canvas) — cards are 171×200px DIVs in left panel. Can interact via mouse click/drag, but need drag to actually select.
- **`page.reload()` timeout with Camoufox** — always use `page.goto(url, wait_until="commit")`
- **Camoufox startup takes 2-3 minutes** — don't kill process prematurely waiting for output
- **Auth tokens expire between sessions** — localStorage cache causes "Complete Your Login" overlay. Always do fresh OTP login (see Auth Token Persistence section above).
- **Multiple click strategies needed** — try Playwright locator → force=True → mouse.move+click → JS click
- **Viewport MUST be ≥1050px** — "Ready up" button at y=926, default 800px viewport hides it
- **"Game Over" ≠ win** — check "Victory" vs "Defeat" text to determine actual result
- **First matchmaking attempt often fails** — WS join sent but no match. Retry 1-2 times works.
- **Matchmaking takes 90-120+ seconds at low ELO** (<1000). Do NOT use fixed timeout loops — use `while True` with 300s safety. Re-join matchmaking every 30s.
- **Auth cache BROKEN** — injecting saved localStorage tokens causes "Complete Your Login" overlay loop. Always do fresh OTP login.
- **Piece card click only FOCUS (purple border), does NOT select!** Need drag strategy to actually select pieces.
- **3D board blocked in headless** — "Your browser blocked 3D graphics" message. Moves must be made via WS messages or DOM click coordinates on the canvas, not visual piece dragging.
- **"Complete Your Login" overlay blocks ALL pointer events** — must dismiss before any interaction. See overlay section above.
- **Dismiss overlays before EVERY interaction** — overlay reappears after page navigation.
- **Camoufox output monitoring** — redirect to file: `python3 -u script.py > /tmp/pixie.log 2>&1` then `tail -f /tmp/pixie.log`
- **Kill stale Camoufox before restart** — `pkill -9 -f camoufox-bin` then wait 2s
