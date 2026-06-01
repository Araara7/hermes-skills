# Canvas Game Automation Patterns

## Core Principle

Canvas-based games render everything on a `<canvas>` element. Standard Playwright click events may not work because:
1. Canvas captures all mouse events
2. Game logic is in JavaScript, not DOM
3. Coordinates are canvas-relative, not page-relative

## ❌ TIDAK WORK: Browser Console Injection

```javascript
// PROBLEM: Game state sering reset setelah beberapa moves
// PROBLEM: Variable scope hilang (CELL, board, playerTurn undefined)
// PROBLEM: Context error "Execution context was destroyed"

// Contoh yang TIDAK work:
handleClick(4 * CELL + CELL/2, 6 * CELL + CELL/2);
setTimeout(() => {
    handleClick(4 * CELL + CELL/2, 4 * CELL + CELL/2);
    playerTurn = false;
    aiMove();
}, 300);
```

## ✅ WORK: Playwright Python Script

```python
#!/usr/bin/env python3
"""
Canvas Game Automation via Playwright
- Lebih stabil dari browser_console
- Handle context destroyed error
- Bisa play multiple moves
"""
import asyncio
from playwright.async_api import async_playwright
import random

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        # Navigate to game
        await page.goto('https://games.thejaynetwork.com/preview.php?f=chess.html')
        await page.wait_for_timeout(2000)
        
        # Get canvas position
        canvas = page.locator('#board')
        box = await canvas.bounding_box()
        cell_size = box['width'] / 8
        
        # Click position function
        async def click_pos(row, col):
            x = box['x'] + col * cell_size + cell_size / 2
            y = box['y'] + row * cell_size + cell_size / 2
            await page.mouse.click(x, y)
            await page.wait_for_timeout(200)
        
        # Start game
        await page.evaluate('startGame()')
        await page.wait_for_timeout(500)
        
        # Play moves with error handling
        error_count = 0
        max_errors = 3
        
        for i in range(30):  # Max 30 moves
            try:
                # Get game state
                state = await page.evaluate('''() => ({
                    gameActive: gameActive,
                    playerTurn: playerTurn,
                    board: board,
                    score: score
                })''')
                
                if not state['gameActive']:
                    print("Game over!")
                    break
                
                if not state['playerTurn']:
                    await page.wait_for_timeout(800)
                    continue
                
                # Find white pieces
                board = state['board']
                white_pieces = []
                for r in range(8):
                    for c in range(8):
                        if board[r][c] and board[r][c].isupper():
                            white_pieces.append((r, c, board[r][c]))
                
                random.shuffle(white_pieces)
                
                # Try to make a move
                moved = False
                for r, c, piece in white_pieces:
                    try:
                        moves = await page.evaluate(f'getMoves({r}, {c})')
                    except:
                        continue
                    
                    if not moves:
                        continue
                    
                    # Prefer captures
                    captures = [m for m in moves if board[m[0]][m[1]] is not None]
                    if captures:
                        move = random.choice(captures)
                    else:
                        move = random.choice(moves)
                    
                    # Make move
                    await click_pos(r, c)
                    await page.wait_for_timeout(150)
                    
                    try:
                        sel = await page.evaluate('selected')
                    except:
                        continue
                    
                    if sel is None:
                        continue
                    
                    await click_pos(move[0], move[1])
                    await page.wait_for_timeout(150)
                    
                    moved = True
                    break
                
                if not moved:
                    print("No valid moves!")
                    break
                
                # Reset error count on success
                error_count = 0
                
                # Wait for AI
                await page.wait_for_timeout(1200)
                
            except Exception as e:
                print(f"Context error: {e}")
                error_count += 1
                if error_count >= max_errors:
                    print(f"Max errors ({max_errors}) reached. Stopping.")
                    break
                
                # Reload game
                await page.goto('https://games.thejaynetwork.com/preview.php?f=chess.html')
                await page.wait_for_timeout(2000)
                await page.evaluate('startGame()')
                await page.wait_for_timeout(500)
                
                # Recalculate canvas position
                canvas = page.locator('#board')
                box = await canvas.bounding_box()
                cell_size = box['width'] / 8
        
        # Take screenshot
        await page.screenshot(path='/home/ubuntu/airdrop-agent/data/screenshots/game_final.png')
        print("Screenshot saved!")
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
```

## Chess-Specific Patterns

### Game Functions
```javascript
// Available functions in chess game:
handleClick(x, y)  // Process click at canvas coordinates
doMove(fr, fc, tr, tc)  // Move piece from (fr,fc) to (tr,tc)
getMoves(r, c)  // Get valid moves for piece at (r,c)
aiMove()  // Trigger AI response
draw()  // Redraw canvas
startGame()  // Start/restart game
checkEnd()  // Check if game ended
endGame(msg)  // End game with message
```

### Coordinate System
```javascript
// Canvas coordinates:
// x = col * CELL + CELL/2
// y = row * CELL + CELL/2

// Grid positions:
// row 0 = top (black pieces)
// row 7 = bottom (white pieces)
// col 0 = left (a-file)
// col 7 = right (h-file)

// Example: e2 pawn = row 6, col 4
// Example: e4 = row 4, col 4
```

### Score System
```javascript
// Score calculation:
// Capture piece: +VALS[piece] * 10
// Pawn promotion: +8
// Piece values:
// p=1, n=3, b=3, r=5, q=9, k=0
```

## Error Handling

### Context Destroyed Error
```
Error: Page.evaluate: Execution context was destroyed, most likely because of a navigation
```

**Solution:**
```python
try:
    state = await page.evaluate('''() => ({...})''')
except Exception as e:
    if "context was destroyed" in str(e):
        # Reload game
        await page.goto(url)
        await page.wait_for_timeout(2000)
        await page.evaluate('startGame()')
        continue
```

### Game State Reset
**Problem:** Game state hilang setelah beberapa moves
**Cause:** Browser console context destroyed
**Solution:** Gunakan Playwright script

### No Valid Moves
**Problem:** Script stuck karena tidak ada moves valid
**Cause:** Game over atau error
**Solution:** Check gameActive status, restart jika perlu

## Best Practices

1. **Gunakan Playwright, bukan browser_console**
2. **Handle context destroyed error dengan reload**
3. **Set error limit (3x) untuk stop**
4. **Set max moves (30) per session**
5. **Prefer captures untuk score lebih tinggi**
6. **Randomize piece selection untuk variasi**
7. **Wait untuk AI response (1200ms)**
8. **Take screenshot untuk debugging**
