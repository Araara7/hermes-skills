#!/usr/bin/env python3
"""
Browser Auth Extractor — Universal token/cookie/auth harvester
Like pressing F12 on any website.

Usage:
  python3 browser_auth.py <url> [--output <file>] [--timeout 120] [--cookies existing.json]

Features:
  - Opens website in headless Chromium
  - Waits for login (manual or auto-detect)
  - Extracts: cookies, localStorage, sessionStorage, JWT tokens, API keys
  - Detects auth method (Privy, Firebase, Auth0, Supabase, Clerk, NextAuth)
  - Saves to JSON file

Token patterns detected:
  - JWT (eyJ...)
  - Bearer tokens
  - Slack tokens (xox[bpsa]-)
  - GitHub PATs (ghp_)
  - API keys (sk-)
  - Google API keys (AIza...)

Auth key patterns in storage:
  - token, auth, session, jwt, access_token, refresh_token
  - privy:, firebase:, auth0:, supabase:, clerk:
  - wallet, user, login, signed_in

Examples:
  python3 browser_auth.py https://pixiechess.xyz
  python3 browser_auth.py https://app.example.com --output config/credentials/example.json
  python3 browser_auth.py https://example.com --cookies cookies.json --output fresh_auth.json

Source: ~/airdrop-agent/scripts/browser_auth.py
"""
