# 🛠️ Hermes Agent Skills

Skills collection for autonomous airdrop agent — automation, captcha solving, auth management, web3 operations.

## Categories

| Category | Skills | Focus |
|----------|--------|-------|
| `airdrop/` | 20+ | Airdrop farming, wallet ops, task automation |
| `creative/` | 15+ | ASCII art, diagrams, design, video |
| `devops/` | 3 | Kanban, orchestration, webhooks |
| `social-media/` | 1 | X/Twitter automation |
| `software-development/` | 12+ | Debugging, TDD, planning, code review |
| `web3/` | 1 | Airdrop project management |
| `gaming/` | 2 | Minecraft, Pokemon |
| `mlops/` | 8+ | ML training, serving, evaluation |
| `productivity/` | 10+ | Email, docs, calendars |
| `research/` | 5 | ArXiv, blog monitoring |
| `email/` | 1 | IMAP/SMTP CLI |
| `github/` | 6 | PR workflow, issues, code review |

## Key Skills

- **`galxe-automation`** — Galxe quest automation (SIWE auth, WASM captcha, social verification)
- **`unified-auth-manager`** — Autonomous auth for all platforms (Galxe, Twitter, Gmail, Discord)
- **`auto-resolve-captcha`** — Local captcha solving (WASM, Turnstile, GeeTest)
- **`auto-get-token`** — Auto extract API keys, JWT, cookies
- **`airdrop-wallet-connect`** — Wallet signing patterns (EVM, Cosmos, Solana)

## Usage

Skills live in `~/.hermes/skills/<category>/<skill-name>/SKILL.md`

Each skill contains:
- Frontmatter (name, description, tags, triggers)
- Documentation (APIs, workflows, examples)
- References (detailed guides)
- Scripts (automation code)
- Pitfalls (known issues)

## Auto-Sync

Skills are auto-pushed to this repo when:
- New skill created and tested
- Existing skill updated with new findings
- Pitfall discovered and documented

## License

Private use only.
