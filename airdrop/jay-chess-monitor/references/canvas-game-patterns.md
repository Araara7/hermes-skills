# Canvas Game Automation Quick Reference

## ❌ TIDAK WORK: Browser Console

```javascript
// Game state sering reset, variable scope hilang
handleClick(4 * CELL + CELL/2, 6 * CELL + CELL/2);
```

## ✅ WORK: Playwright Script

```python
# Gunakan Playwright untuk canvas games
cd ~/airdrop-agent && venv/bin/python scripts/chess_auto_claim.py
```

## Error Handling

### Context Destroyed Error
```
Error: Page.evaluate: Execution context was destroyed
```

**Solution:** Script otomatis reload game

### Error Limit
- Max 3 errors berturut → STOP
- Reset error count setelah success

### Max Moves
- Max 30 moves per session
- Stop jika game over

## Chess Functions

```javascript
handleClick(x, y)  // Click di koordinat canvas
doMove(fr, fc, tr, tc)  // Pindahkan piece
getMoves(r, c)  // Dapatkan valid moves
aiMove()  // Trigger AI response
startGame()  // Mulai/restart game
```

## Coordinate System

```javascript
// Canvas coordinates:
x = col * CELL + CELL/2
y = row * CELL + CELL/2

// Grid positions:
row 0 = top (black)
row 7 = bottom (white)
col 0 = left (a-file)
col 7 = right (h-file)
```
