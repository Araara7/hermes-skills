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

Source: ~/airdrop-agent/scripts/browser_auth.py
"""
