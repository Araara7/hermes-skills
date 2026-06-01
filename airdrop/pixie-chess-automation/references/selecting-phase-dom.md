# Pixie Chess SELECTING Phase DOM Analysis

## Date: 1 Jun 2026

## Piece Card Layout
5 piece cards in a horizontal row in the left panel:

| Piece | Position (x,y) | Size (w×h) | Notes |
|-------|----------------|------------|-------|
| Bouncer | (80, 252) | 171×200 | Red geometric knight |
| Fish | (259, 252) | 171×200 | Blue origami shark |
| Pawn with Knife | (439, 252) | 171×200 | Dark pawn, red weapon |
| Phase Rook | (618, 252) | 171×200 | Glowing cyan rook |
| War Automaton | (797, 252) | 171×200 | Red blocky pawn |

## Element Hierarchy
```
DIV.relative (171×200) ← card container, click target
  └─ DIV (169×198) ← inner card (piece image + text)
      └─ DIV.flex.flex-col (72×32) ← label area (piece name + "FREE")
```

## Key Findings
- **Clicking a card container** = focuses/hovers it (purple border glow) but does NOT select
- **CURRENT counter** stays at 0 after click — selection requires drag
- **Instruction text**: "Click or Drag to substitute in a Pixie piece"
- **3D board blocked** in headless: "Your browser blocked 3D graphics for this site"
- **READY button** at bottom-right of page (y=926, needs viewport ≥1050px)

## Selection States
- No border = unselected
- Purple glowing border = focused/hovered (NOT selected!)
- CURRENT counter = actual selection count (must be ≥3)

## Drag Target
Board area on right side: approximately x=800-1200, y=300-700
Drag from card center (~166,352) to board area (~900,500)

## Screenshot Reference
- `/tmp/pixie_diag/03_no_match.png` — SELECTING phase overview
- `/tmp/pixie_diag/piece_select_fail.png` — CURRENT=0 despite clicks (purple border visible)

## Viewport
Standard: 1280×1050 (button at y=926 requires ≥1050px height)
