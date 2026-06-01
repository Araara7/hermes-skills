#!/usr/bin/env python3
"""
JAY Games Chess Auto-Play via Playwright
Reliable canvas automation using mouse clicks
"""
import asyncio
from playwright.async_api import async_playwright
import random

CHESS_URL = 'https://games.thejaynetwork.com/preview.php?f=chess.html'

# Piece values for move selection
PIECE_VALS = {'p':1,'n':3,'b':3,'r':5,'q':9,'k':0,'P':1,'N':3,'B':3,'R':5,'Q':9,'K':0}

# Good opening moves (book)
OPENING_MOVES = [
    # 1.e4 (King's Pawn)
    {'from': (6, 4), 'to': (4, 4), 'name': 'e2→e4'},
    # 1.d4 (Queen's Pawn)
    {'from': (6, 3), 'to': (4, 3), 'name': 'd2→d4'},
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        print("Loading chess game...")
        await page.goto(CHESS_URL)
        await page.wait_for_timeout(2000)
        
        # Get canvas
        canvas = page.locator('#board')
        box = await canvas.bounding_box()
        cell_size = box['width'] / 8
        
        async def click_pos(row, col):
            x = box['x'] + col * cell_size + cell_size / 2
            y = box['y'] + row * cell_size + cell_size / 2
            await page.mouse.click(x, y)
            await page.wait_for_timeout(200)
        
        async def get_state():
            return await page.evaluate('''() => ({
                gameActive, playerTurn, board, score, selected
            })''')
        
        async def find_white_pieces(board):
            pieces = []
            for r in range(8):
                for c in range(8):
                    if board[r][c] and board[r][c].isupper():
                        pieces.append((r, c, board[r][c]))
            return pieces
        
        async def pick_move(board, moves):
            """Pick best move: prefer captures, then center control"""
            captures = [m for m in moves if board[m[0]][m[1]] is not None]
            if captures:
                # Pick highest value capture
                return max(captures, key=lambda m: PIECE_VALS.get(board[m[0]][m[1]], 0))
            
            # Prefer center squares
            center_moves = [m for m in moves if 2 <= m[0] <= 5 and 2 <= m[1] <= 5]
            if center_moves:
                return random.choice(center_moves)
            
            return random.choice(moves)
        
        # Start game
        print("Starting game...")
        await page.evaluate('startGame()')
        await page.wait_for_timeout(500)
        
        moves_played = []
        move_num = 0
        
        while move_num < 50:
            try:
                state = await get_state()
            except Exception as e:
                if "context" in str(e).lower():
                    print("Context destroyed, reloading...")
                    await page.goto(CHESS_URL)
                    await page.wait_for_timeout(2000)
                    await page.evaluate('startGame()')
                    await page.wait_for_timeout(500)
                    canvas = page.locator('#board')
                    box = await canvas.bounding_box()
                    cell_size = box['width'] / 8
                    continue
                raise
            
            if not state['gameActive']:
                print(f"Game over! Score: {state['score']}")
                break
            
            if not state['playerTurn']:
                await page.wait_for_timeout(1000)
                continue
            
            board = state['board']
            white_pieces = await find_white_pieces(board)
            random.shuffle(white_pieces)
            
            moved = False
            for r, c, piece in white_pieces:
                try:
                    moves = await page.evaluate(f'getMoves({r},{c})')
                except:
                    continue
                
                if not moves:
                    continue
                
                move = await pick_move(board, moves)
                
                # Select piece
                await click_pos(r, c)
                await page.wait_for_timeout(100)
                
                # Verify selection
                try:
                    sel = await page.evaluate('selected')
                except:
                    continue
                
                if sel is None:
                    continue
                
                # Move piece
                await click_pos(move[0], move[1])
                await page.wait_for_timeout(100)
                
                from_str = chr(97 + c) + str(8 - r)
                to_str = chr(97 + move[1]) + str(8 - move[0])
                move_num += 1
                moves_played.append(f"{piece} {from_str}→{to_str}")
                print(f"Move {move_num}: {piece} {from_str}→{to_str}")
                moved = True
                break
            
            if not moved:
                print("No valid moves, restarting...")
                await page.evaluate('startGame()')
                await page.wait_for_timeout(500)
                continue
            
            # Wait for AI
            await page.wait_for_timeout(1500)
        
        # Save screenshot
        await page.screenshot(path='/home/ubuntu/airdrop-agent/data/screenshots/chess_final.png')
        print(f"\nScreenshot saved!")
        print(f"Total moves: {len(moves_played)}")
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
