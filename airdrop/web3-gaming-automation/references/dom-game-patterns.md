# DOM-Based Game Automation Pattern

For games where game state is trapped inside IIFE (Immediately Invoked Function Expression) and not accessible via `page.evaluate()`.

## Problem

Many web games wrap their code in IIFE:
```javascript
(() => {
  "use strict";
  const state = { puzzle: [], solution: [], score: 0 };
  // ... game logic
})();
```

Variables like `state`, `solution`, `score` are NOT accessible from outside.

## Solution: Read → Solve → Fill

1. **Read** game state from DOM (not JS variables)
2. **Solve** the puzzle/game in Python
3. **Fill** solution via DOM interactions

## Example: JAY Sudoku

### Step 1: Read Puzzle from DOM
```javascript
// Read cell values from DOM
const cells = document.querySelectorAll("#board .cell");
const puzzle = [];
cells.forEach(cell => {
    let val = 0;
    for (const child of cell.childNodes) {
        if (child.nodeType === 3 && child.textContent.trim()) {
            val = parseInt(child.textContent.trim()) || 0;
            break;
        }
    }
    puzzle.push(val);
});
```

### Step 2: Solve in Python
```python
def solve_sudoku(grid):
    g = grid[:]
    def solve(pos):
        while pos < 81 and g[pos] != 0: pos += 1
        if pos == 81: return True
        for n in range(1, 10):
            if can_place(g, pos, n):
                g[pos] = n
                if solve(pos + 1): return True
                g[pos] = 0
        return False
    return g if solve(0) else None
```

### Step 3: Fill via DOM
```python
for i in range(81):
    if puzzle[i] == 0:
        val = solution[i]
        # Click cell
        await page.evaluate(f'''
            document.querySelectorAll("#board .cell")[{i}].click();
        ''')
        await asyncio.sleep(0.05)
        # Click number pad
        await page.evaluate(f'''
            document.querySelectorAll("#pad .num")[{val - 1}].click();
        ''')
        await asyncio.sleep(0.1)
```

## When to Use This Pattern

- Game code wrapped in IIFE
- `page.evaluate('state')` throws ReferenceError
- Game has DOM elements that reflect internal state
- Puzzle/game can be solved algorithmically

## Advantages

- No need to reverse-engineer game internals
- Works even when JS scope is locked
- Python solver can be optimized independently
- Deterministic success (100% for Sudoku)

## Pitfalls

1. **Frame Detection**: Main page may load iframe lazily. Wait 10s before checking frames.

2. **Cell Selection Order**: Must click cell first, then number pad. Order matters.

3. **Win Detection**: Check for win overlay in DOM, not JS variable:
   ```javascript
   document.getElementById("winOverlay").classList.contains("show")
   ```

4. **Claim Button**: May need to be enabled first:
   ```javascript
   const btn = document.getElementById("claimBtn");
   btn.disabled = false;
   btn.click();
   ```
