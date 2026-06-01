#!/usr/bin/env python3
"""
JAY Games Auto-Play Template
Template untuk自动化 JAY Games. Sesuaikan dengan kebutuhan.
"""

import asyncio
import json
import time
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

class JAYGamePlayer:
    def __init__(self, wallet_address):
        self.wallet = wallet_address
        self.data_dir = Path.home() / "airdrop-agent" / "data" / "jay_games"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir = Path.home() / "airdrop-agent" / "data" / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
    async def connect_wallet(self, page):
        """Hubungkan wallet ke JAY Games"""
        print("🔗 Menghubungkan wallet...")
        
        # Simpan wallet ke sessionStorage
        await page.evaluate(f'''
            sessionStorage.setItem('jay_games_wallet', '{self.wallet}');
        ''')
        
        # Reload halaman
        await page.reload()
        await asyncio.sleep(3)
        
        # Verifikasi koneksi
        wallet_status = await page.evaluate('''
            () => {
                return sessionStorage.getItem('jay_games_wallet');
            }
        ''')
        
        if wallet_status == self.wallet:
            print("✅ Wallet berhasil terhubung!")
            return True
        else:
            print("❌ Gagal menghubungkan wallet")
            return False
    
    async def get_stats(self, page):
        """Ambil statistik wallet"""
        stats = await page.evaluate('''
            async () => {
                const wallet = sessionStorage.getItem('jay_games_wallet');
                if (!wallet) return { error: 'Wallet not connected' };
                
                try {
                    const response = await fetch('api.php?api=stats&wallet=' + wallet);
                    const data = await response.json();
                    return data;
                } catch (e) {
                    return { error: e.message };
                }
            }
        ''')
        return stats
    
    async def play_chess(self, page, moves=10):
        """Mainkan game Chess"""
        print("♟️ Memulai Chess...")
        
        # Buka game
        await page.goto('https://games.thejaynetwork.com/preview.php?f=chess.html', 
                       wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(3)
        
        # Deploy game
        print("🎯 Deploy game...")
        await page.evaluate('''
            () => {
                const btn = document.querySelector('button');
                if (btn) btn.click();
            }
        ''')
        await asyncio.sleep(2)
        
        # Mainkan beberapa langkah
        print(f"🎮 Bermain {moves} langkah...")
        
        for i in range(moves):
            # Cek apakah giliran player
            is_player_turn = await page.evaluate('''
                () => {
                    return typeof playerTurn !== 'undefined' && playerTurn && gameActive;
                }
            ''')
            
            if not is_player_turn:
                print(f"   ⏳ Menunggu AI... (langkah {i+1})")
                await asyncio.sleep(2)
                continue
            
            # Dapatkan langkah yang tersedia
            move_result = await page.evaluate('''
                () => {
                    // Cari semua bidak putih yang bisa bergerak
                    for (let r = 0; r < 8; r++) {
                        for (let c = 0; c < 8; c++) {
                            if (board[r][c] && board[r][c] === board[r][c].toUpperCase()) {
                                const moves = getMoves(r, c);
                                if (moves.length > 0) {
                                    return {
                                        from: [r, c],
                                        to: moves[0],  // Ambil langkah pertama
                                        piece: board[r][c]
                                    };
                                }
                            }
                        }
                    }
                    return null;
                }
            ''')
            
            if move_result:
                fr, fc = move_result['from']
                tr, tc = move_result['to']
                piece = move_result['piece']
                
                print(f"   📍 Langkah {i+1}: {piece} dari ({fr},{fc}) ke ({tr},{tc})")
                
                # Buat langkah
                await page.evaluate(f'''
                    () => {{
                        doMove({fr}, {fc}, {tr}, {tc});
                        draw();
                        playerTurn = false;
                        infoEl.textContent = "AI thinking...";
                        setTimeout(aiMove, 300);
                    }}
                ''')
                
                await asyncio.sleep(2)
            else:
                print(f"   ⚠️  Tidak ada langkah tersedia")
                break
        
        # Ambil screenshot
        await page.screenshot(path=self.screenshots_dir / "chess_auto.png")
        print("📸 Screenshot disimpan")
        
        return True
    
    async def run(self, game='chess', **kwargs):
        """Jalankan auto-play"""
        print("🚀 Memulai JAY Games Auto-Player")
        print("=" * 50)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            try:
                # Buka halaman utama
                print("🌐 Membuka JAY Games...")
                await page.goto('https://games.thejaynetwork.com/', wait_until='domcontentloaded', timeout=60000)
                await asyncio.sleep(3)
                
                # Hubungkan wallet
                if not await self.connect_wallet(page):
                    return
                
                # Ambil statistik awal
                print("\n📊 Statistik awal:")
                stats_before = await self.get_stats(page)
                print(f"   Claims: {stats_before.get('claims', 0)}")
                print(f"   Total UJAY: {stats_before.get('total_ujay', 0)}")
                
                # Mainkan game
                if game == 'chess':
                    await self.play_chess(page, **kwargs)
                else:
                    print(f"⚠️  Game {game} belum didukung")
                
                # Ambil statistik akhir
                print("\n📊 Statistik akhir:")
                stats_after = await self.get_stats(page)
                print(f"   Claims: {stats_after.get('claims', 0)}")
                print(f"   Total UJAY: {stats_after.get('total_ujay', 0)}")
                
                # Simpan log
                log_data = {
                    'timestamp': datetime.now().isoformat(),
                    'wallet': self.wallet,
                    'game': game,
                    'stats_before': stats_before,
                    'stats_after': stats_after
                }
                
                log_file = self.data_dir / f"play_log_{int(time.time())}.json"
                with open(log_file, 'w') as f:
                    json.dump(log_data, f, indent=2)
                
                print(f"\n💾 Log disimpan: {log_file}")
                print("\n✅ Auto-play selesai!")
                
            except Exception as e:
                print(f"\n❌ Error: {e}")
                await page.screenshot(path=self.screenshots_dir / "auto_play_error.png")
                
            finally:
                await browser.close()

async def main():
    # Wallet address
    wallet = "yjay19t8u26z70aeqvuj28y3jlnqznzh57vzcqc8tr9"
    
    # Buat player
    player = JAYGamePlayer(wallet)
    
    # Jalankan auto-play chess
    await player.run(game='chess', moves=10)

if __name__ == "__main__":
    asyncio.run(main())
