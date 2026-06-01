# Galxe API Types Reference

## Address Type Fields
```
id, address, username, avatar
hasEvmAddress, hasSolanaAddress, hasAptosAddress, hasSeiAddress, hasArchwayAddress
hasInjectiveAddress, hasFlowAddress, hasStarknetAddress, hasSuiAddress, hasBitcoinAddress
hasStacksAddress, hasAzeroAddress, hasBitcoinSignetAddress, hasXrplAddress, hasAlgorandAddress
hasKadenaAddress, hasTonAddress
hasEmail, hasTwitter, hasGithub, hasDiscord, hasTelegram, hasGoogle, hasVery, hasWorldcoin
displayEmail, displayTwitter, displayGithub, displayDiscord, displayTelegram, displayGoogle
email, twitterUserID, twitterUserName, githubUserID, githubUserName
discordUserID, discordUserName, telegramUserID, telegramUserName
googleUserID, googleUserName, worldcoinID
isVerifiedTwitterOauth2, isVerifiedDiscordOauth2
isBot, isVerified, isWhitelisted, isInvited, isAdmin
participatedCampaignCount, userXPLevel, userLevel
```

## CredentialSyncOptionsInput
```
credId: ID!           — credential ID
address: String!      — "EVM:0x..." format
twitter: TwitterCredentialValueSyncOptionsInput
  ├── captcha: CaptchaInput! (lotNumber, captchaOutput, passToken, genTime, encryptedData)
  └── campaignID: ID!
gitcoin: GitcoinCredentialValueSyncOptionsInput
survey: SurveyCredentialValueSyncOptionsInput
quiz: QuizCredentialValueSyncOptionsInput
worldCoin: WorldCoinCredentialValueSyncOptionsInput
prediction: PredictionCredentialValueSyncOptionsInput
```

## CaptchaInput
```
lotNumber: String!     — sha256(apiName)
captchaOutput: String! — WASM-generated proof
passToken: String!     — sha256(genTime)
genTime: String!       — unix timestamp (seconds)
encryptedData: String  — optional encrypted data
```

## PrepareParticipateInput
```
signature: String!     — any valid ETH signature
campaignID: ID!        — campaign ID (capital D!)
address: String!       — wallet address
addressType: AddressType — optional enum
chain: Chain           — optional enum (ETHEREUM, BSC, MATIC, etc.)
captcha: CaptchaInput  — WASM captcha required for claim
mintCount: Int
burnedNftIDs: [ID!]
optIn: OptInInput
referralCode: String
pointMintAmount: Int
claimVersion: SpaceStationVersion
premintTo: String
```

## Chain Enum Values
```
ETHEREUM, ROPSTEN, KOVAN, RINKEBY, GOERLI, BSC, BSC_TESTNET, MATIC, MUMBAI, XDAI,
ARBITRUM, ARBITRUM_TESTNET, HECO, HECO_TESTNET, FANTOM, FANTOM_TESTNET, AVALANCHE,
AVALANCHE_TESTNET, SOLANA, SOLANA_DEVNET, MOONBEAM, OPTIMISM, IOTEX, APTOS, APTOS_TESTNET,
OKC, BOBA_ETH, BOBA_AVAX, BOBA_BNB, BOBA_MOONBEAM, BOBA_FANTOM, ZKSYNC_ERA, SEI,
ATLANTIC2, BASE, BASE_TESTNET, LINEA, LINEA_TESTNET, SCROLL, SCROLL_TESTNET, SCROLL_SEPOLIA,
POLYGON_ZKEVM, INJECTIVE, FLOW, FLOW_TESTNET, SEPOLIA, STARKNET, STARKNET_TESTNET,
MODE_SEPOLIA, FNCY, LIGHTLINK_PHOENIX, MANTA_PACIFIC, KROMA, KROMA_SEPOLIA, HAQQ, OPBNB,
MANTLE, X1_TESTNET, ROOT, INJECTIVE_TESTNET, SUI, BITCOIN, QUAI_TESTNET, BLAST,
BLAST_SEPOLIA, ZIRCUIT_TESTNET, KLAYTN, SHARDEUM_SPHINX, STACKS, ZETACHAIN, AZERO,
CRONOS, MERLIN, X1_MAINNET, CYBER, ARCHWAY, BITCOIN_SIGNET, XRPL, ALGORAND, GRAVITY_ALPHA,
RSK, VICTION, KREST, MINT, MOVEMENT_SUZUKI, MOVEMENT_SUI, EMONEY_TESTNET, MEVM, SEI_EVM,
TON, SONEIUM_MINATO, SONEIUM, PEAQ, ZIRCUIT, ZERO, ABSTRACT, EMONEY_MAINNET, TAIKO,
KADENA, Nibiru, Superposition, PLUME, MONAD_TESTNET, ZERO_G_TESTNET, QURANIUM_TESTNET,
FLARE, NEURA_TESTNET, ZERO_G, DOGEOS_DEVNET, MEZO, DOGEOS_TESTNET
```

## CampaignStatus Enum
```
Draft, Active, NotStarted, Expired, CapReached, Deleted
```

## ListType Enum
```
Newest, Earliest, Trending, Tutorial, MostGG
```
