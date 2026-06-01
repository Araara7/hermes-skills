# Viewport Debugging Session (1 Jun 2026)

## Problem
"Ready up" button not clickable during SELECTING phase. Games forfeit because countdown expires.

## Root Cause
Button position: y=926px. Default viewport: 800px. Button was **126px below visible area**.

## Debugging Path

### v4-v5: Camoufox crashes
- `Page.reload: Timeout 30000ms` — Camoufox can't handle page.reload()
- `Keyboard.press: Connection closed` — driver crash from page errors
- Fix: use `page.goto(url, wait_until="commit")` instead of reload

### v6: Matchmaking works, SELECTING fails
- Login via OTP: ✅
- Match found in <5s: ✅
- SELECTING phase detected: ✅
- "Ready up" button found at (1265, 926): ✅
- Button click doesn't register: ❌ (viewport 800px, button at y=926)

### v7: Wrong button clicks
- "Play" button click triggered NEW matchmaking instead of ready up
- Script thought "Ready up SUCCESS!" because SELECTING text disappeared
- Actually just started a new search

### v8: Breakthrough
- Viewport changed to 1050px → button visible
- JS click: `btn.scrollIntoView({block: 'center'}); btn.click();` → WORKS
- "Ready up clicked (JS)!" confirmed in logs
- BUT: games 1-4 still forfeited because click happened too late (inside wait loop)
- Game 5: click succeeded, but script timed out before seeing game result

## Key Metrics
- Viewport 800px: ❌ button hidden
- Viewport 900px: ❌ button still at y=926
- Viewport 1050px: ✅ button visible and clickable
- Viewport 1200px: ✅ also works but Camoufox slower to start

## ELO Impact
Started: 1500 → Dropped to: ~798 (due to forfeit debugging)

## Lesson Learned
Always check button positions against viewport size. React buttons outside viewport silently fail — no error, no indication. Use `getBoundingClientRect()` to verify visibility.
