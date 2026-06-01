# Pixie Chess Platform Reference

**URL:** https://pixiechess.xyz
**Type:** Web3 Chess PvP with real money (ETH)
**Company:** The Dutch East Internet Company
**Status:** Live (as of May 2026)

## Architecture

- **Main site:** pixiechess.xyz (Vite SPA)
- **Game board:** board.pixiechess.xyz (Netlify, separate app)
- **API:** api.pixiechess.xyz (CloudFront WAF protected)
- **WebSocket:** wss://api.pixiechess.xyz (real-time game)
- **Assets:** assets.pixiechess.xyz

## Auth System (Privy)

- **Provider:** Privy (app ID: `cmj86b87s02wkld0cjaypk8ci`)
- **Methods:** Email (Turnstile CAPTCHA blocked), MetaMask, Phantom, WalletConnect, Coinbase, Rabby, Rainbow
- **WalletConnect Project ID:** `34357d3c125c2bcf2ce2bc3309d98715`
- **CAPTCHA:** Cloudflare Turnstile (site key: `0x4AAAAAADGtm7mx4aLENCLF`)

### Login Flow
1. User clicks LOGIN → modal with email/wallet options
2. Accept Terms of Entry (must scroll terms to bottom, then check "I agree")
3. Wallet: MetaMask injected provider detected → connects → SIWE challenge → sign → auth token
4. Email: blocked by Turnstile CAPTCHA from headless/datacenter IPs

### localStorage Keys
- `privy:connections` — wallet connection info (address, connectorType, walletClientType)
- `privy:caid` — client analytics ID
- `privy:sent:{app_id}:{id}` — tracking
- `privy:token` — **auth JWT (only after SIWE completion)**
- `wagmi.store` — wagmi connection state
- `wagmi.recentConnectorId` — last used connector
- `app-store` — app state (userId, tutorialCompleted, redirectLink)
- `@appkit/connection_status` — appkit connection status
- `@appkit/active_namespace` — active chain namespace
- `@appkit/active_caip_network_id` — active network

### Key Finding: MetaMask Injection Works for Connection but Not Auth
- Injecting `window.ethereum` with `isMetaMask: true` via `add_init_script` BEFORE page load → Privy detects it
- Wallet connects: `privy:connections` shows wallet address with `connectorType: "injected"`
- **BUT:** SIWE signing flow does NOT auto-trigger
- `userId` stays `null`, no `privy:token` created
- Without SIWE token, game actions (SEARCH FOR MATCH) trigger Turnstile CAPTCHA

## Game Modes

1. **Quickplay** — PvP matchmaking (live)
2. **Tournaments** — "The Vault" system, ETH prize pools (live)
3. **Brawl** — On-demand brackets, tickets to enter, win ETH (coming soon)
4. **Custom Match** — Play with friends via link
5. **Tutorial** — 1-minute onboarding

## Pieces

- **58 special pieces** with unique abilities
- Purchased via ETH (Dutch auction system) or Mystery Packs
- Pieces are sacrificed to enter tournaments
- Examples: Bouncer (bishop bounces off edges), Sumo Rook, ElectroKnight, Epee Pawn, Rocketman, Pilgrim, Pinata, Banker, Fission Reactor

## Ranking System

Wood → Silver → Gold → Jade → Diamond → Onyx → Master

## Game Board Communication

The board (board.pixiechess.xyz) communicates with the main site via `postMessage`:
- `boardReady` — Board initialized
- `move` — Move made
- `possibleMoves` — Get legal moves
- `sync` — Sync game state
- `pregameComplete` — Pre-game animation done
- `endGameAnimationComplete` — Game over animation done
- `InvalidMove` — Illegal move attempted
- `selectTile` — Tile selected
- `pieceHover` — Piece hover event

## Smart Contracts (from JS bundle)

- Game Proxy: `0x10f9bc99c2a5ec3ec02f477cc130f71e3cf51962`
- Instant Mint: `0xb3b4f451870b53586949f0af4ba754aaf8aed4f3`

## Airdrop Potential

- Points/quests system exists in code (`/quests`, `/points` routes) but redirects to homepage (not live yet)
- Invite system exists (`/invite` route)
- Leaderboard system active
- Worth monitoring for future token launch

## Automation Status (31 Mei 2026)

| Feature | Status | Blocker |
|---------|--------|---------|
| Wallet connect | ✅ Works | MetaMask injection detected |
| SIWE auth | ❌ Blocked | No auto-trigger, needs real MetaMask signing |
| Play game | ❌ Blocked | Turnstile CAPTCHA on game actions |
| API access | ❌ Blocked | CloudFront WAF challenge |
| Token extraction | ⚠️ Manual | Need user to export from real browser |

**Next step:** User needs to export `privy:token` from their logged-in browser (F12 → Console → `localStorage.getItem('privy:token')`).
