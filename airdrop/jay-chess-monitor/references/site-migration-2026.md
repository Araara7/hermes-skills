# JAY Games Site Migration (30 Mei 2026)

## Perubahan

Site `games.thejaynetwork.com` migrasi dari PHP ke Next.js.

### URLs yang BERUBAH:
- `game.php?id=77` → 404 (chess dihapus)
- `api.php?api=stats` → 404
- `api.php?api=claim` → 404
- `api.php?api=session_token` → 404
- `api.php?api=x_check` → 404
- `api.php?api=x_connect` → 404

### URLs baru:
- Homepage: `https://games.thejaynetwork.com/`
- Games: `/play/tower-defense`, `/play/jay-sudoku`, `/play/jay-squad`, dll

### Games tersedia (12):
1. Tower Defense - Arcade
2. JAY Sudoku - Puzzle
3. JAY Squad - Action
4. JAY Cresta - Arcade (retro space shooter)
5. JAY Tank - Arcade (battle tanks)
6. Othello Arena - Strategy
7. **Janggi Arena** - Strategy (Korean chess - paling mirip chess)
8. Connect Four - Puzzle
9. JAY Tetris - Puzzle
10. Cryptogram - Puzzle (cipher decode)
11. JAY Outpost - Strategy (build & defend)
12. JAY Picross - Puzzle (picture logic)

### Reward system:
- Unverified: 0.05× reward
- Verified (X/Twitter): up to 250 JAY/hari
- Per game: 5 JAY (verified)

### Twitter verification:
- Button "Verify with X" ada di homepage
- Disabled saat belum connect wallet
- OAuth flow belum diketahui (belum dicoba)

## Impact ke automation

Semua script chess v5 **TIDAK BISA DIPAKAI** karena:
1. URL game.php?id=77 → 404
2. Chess iframe (g/chess.html) → tidak ada
3. API endpoints → 404

## Next steps

1. Explore API endpoints baru di site Next.js
2. Pilih game yang paling mudah di-automate
3. Buat script automation baru
4. Test Twitter verification flow
