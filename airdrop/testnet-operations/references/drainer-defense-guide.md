# Crypto Drainer Defense Guide (Educational)

## 3 Tipe Drainer

### 1. Approval Drainer (Paling Umum)
```
Korban → Klik link palsu → Sign "setApprovalForAll" → Attacker punya akses unlimited → Drain
```
- Korban sign TX yang terlihat normal
- Sebenarnya = approval unlimited ke contract attacker
- Attacker bisa transfer semua ERC-20/721/1155

### 2. Permit Drainer (ERC-2612)
```
Korban → Sign message (bukan TX) → Attacker dapat signature → Submit on-chain → Token pindah
```
- Tidak perlu on-chain approval
- Signature terlihat "tidak berbahaya"
- Bisa dilakukan offline

### 3. Seaport/Marketplace Drainer
```
Korban → Sign order → Attacker fulfill order dengan harga 0 → NFT pindah
```
- Marketplace order signing
- Order dengan harga 0
- Korban tidak sadar

## Cara Lindungi Diri

1. **Baca detail TX** sebelum klik Approve
2. **Jangan sign** approval unlimited
3. **Revoke approval** setelah selesai → revoke.cash
4. **Hardware wallet** (Ledger/Trezor)
5. **Separate wallet** untuk DeFi/minting
6. **Jangan klik link** dari DM/Telegram

## Tools Pertahanan
- [Revoke.cash](https://revoke.cash) — cek & revoke approval
- [Etherscan Token Approvals](https://etherscan.io/tokenapprovalchecker)
- [PocketUniverse](https://pocketuniverse.app) — firewall wallet
- [ScamSniffer](https://scamsniffer.io) — detect phishing

## Kenapa Private Key Leak = Game Over
- Private key = akses penuh ke wallet
- Attacker bisa sign TX sebagai owner
- Tidak ada "approval" yang bisa dicegah
- Semua aset bisa langsung disweep

## Contoh Serangan Real
- **Inferno Drainer** (2023-2024): $80M+, Seaport + Permit
- **Monkey Drainer** (2022-2023): $16M+, Approval
- **Pink Drainer** (2023-2024): $18M+, Permit signatures

## Educational Materials

Full drainer/attack educational content stored at:
- `~/airdrop-agent/data/edukasi/DrainSimulator.sol` — Smart contract showing approval/drain flow
- `~/airdrop-agent/data/edukasi/drainer_bot.py` — Bot simulation (scan → detect → drain)
- `~/airdrop-agent/data/edukasi/deploy_testnet.py` — Deploy to testnet for testing
- `~/airdrop-agent/data/edukasi/README.md` — Complete guide with attack flow diagrams
- `~/airdrop-agent/data/edukasi_drainer.md` — Attack mechanics explained

### What the Educational Materials Show

**DrainSimulator.sol** — Smart contract with:
- `checkApproval()` — Detect if victim approved tokens
- `drainToken()` — Execute drain after approval
- `drainAll()` — Greedy drain all approved tokens
- `drainWithPermit()` — ERC-2612 permit-based drain
- `drainNFT()` — NFT drain via setApprovalForAll

**drainer_bot.py** — Python bot with:
- `scan_victim()` — Check approvals on multiple tokens
- `drain_token()` — Execute drain transaction
- `monitor_and_drain()` — Auto-monitor and drain loop
- `withdraw()` — Extract stolen funds

**Attack Flow:**
1. Victim clicks phishing link
2. Signs "SetApprovalForAll" (looks harmless)
3. Attacker's bot detects approval in real-time
4. Bot executes `transferFrom()` immediately
5. Tokens transferred to attacker wallet
6. Victim doesn't notice until checking wallet
