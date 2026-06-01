# JAY Games Chess — Game Architecture

## Page Structure

```
game.php?id=77 (main page)
├── .game-header (Chess, 5 JAY reward pill)
├── #xBadge (verify with X prompt)
├── .game-frame
│   └── <iframe src="g/chess.html"> (chess game)
│       ├── <canvas> (chess board rendering)
│       ├── <button>DEPLOY</button> (start game)
│       ├── #status ("Score: X")
│       ├── #info ("Your turn (White)")
│       └── #overlay (pre-game screen)
└── .game-footer
    ├── .score-val (#scoreVal — receives score via postMessage)
    ├── .diff-info ("Expert (min: 200)")
    └── #claimBtn (disabled until score >= 200)
```

## Chess Game JS Globals (inside iframe)

```javascript
board[8][8]    // 8x8 array. null = empty, uppercase = white, lowercase = black
score          // integer, starts at 0
playerTurn     // boolean, true when it's white's turn
gameOver       // boolean
```

## Board Layout

```
Row 0 (top):    ["r","n","b","q","k","b","n","r"]  ← Black back rank
Row 1:          ["p","p","p","p","p","p","p","p"]  ← Black pawns
Row 2-5:        [null, null, ...]                   ← Empty
Row 6:          ["P","P","P","P","P","P","P","P"]  ← White pawns
Row 7 (bottom): ["R","N","B","Q","K","B","N","R"]  ← White back rank
```

Column mapping: a=0, b=1, c=2, d=3, e=4, f=5, g=6, h=7

## Key JS Functions (inside iframe)

### doMove(fr, fc, tr, tc)
Moves piece from board[fr][fc] to board[tr][tc].
- Handles pawn promotion (P at row 0 → Q, +8 score)
- On capture: `score += VALS[captured] * 10`
- On capture: sends `window.parent.postMessage({score: score}, '*')`
- Updates status text

### getMoves(r, c) → Array of [tr, tc]
Returns valid moves for piece at board[r][c].

### aiMove()
AI finds best black move (prefers captures + center control), calls doMove + draw + checkEnd.
Sets `playerTurn = true` and updates info text when done.

### checkEnd() → boolean
Checks for checkmate/stalemate/draw. Sets `gameOver = true` if game ended.

### draw()
Redraws the canvas.

### VALS object (piece values for scoring)
```
p=1, n=3, b=3, r=5, q=9  (lowercase = black)
P=1, N=3, B=3, R=5, Q=9  (uppercase = white)
Score = VALS[captured] * 10
```

## Score Propagation (iframe → parent)

Chess iframe sends: `window.parent.postMessage({score: score}, '*')`
Parent page listens:
```javascript
window.addEventListener('message', e => {
    if (e.data && typeof e.data.score === 'number') {
        currentScore = e.data.score;
        document.getElementById('scoreVal').textContent = currentScore.toLocaleString();
        if (currentScore >= MIN_SCORE && !claimed)
            document.getElementById('claimBtn').disabled = false;
    }
});
```

## Main Page JS Variables

```javascript
GAME_ID = 77
MIN_SCORE = 200        // Minimum score to claim
REWARD_JAY = '5'       // Full reward (X verified)
REWARD_UJAY = '5000000' // Full reward in micro-JAY
UNVERIFIED_DIV = 20    // Unverified reward divider (5/20 = 0.25 JAY)
currentScore = 0       // Updated via postMessage
sessionToken = ''      // Fetched from api.php?api=session_token
claimed = false
xVerified = false
```

## Stealth / Anti-Bot

- Use `--disable-blink-features=AutomationControlled` chromium arg
- Stats API may return `{"error": "bot blocked"}` from within Playwright without stealth
- Set proper User-Agent
- Wallet must be in sessionStorage BEFORE page loads (via `context.add_init_script`)
