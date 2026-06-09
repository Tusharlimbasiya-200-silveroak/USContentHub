#!/usr/bin/env python3
"""
Pinterest Board Setup & GitHub Secrets Generator
=================================================
Run this ONCE with your Pinterest access token to:

  1. Verify your token works
  2. List all existing Pinterest boards
  3. Auto-create any missing publication boards (public)
  4. Print exact `gh secret set` commands — copy-paste into your terminal

Usage:
    pip install requests
    export PINTEREST_ACCESS_TOKEN=your_long_lived_token_here
    python pinterest_bot/setup_secrets.py

How to get your access token:
    1. Go to https://developers.pinterest.com/
    2. Log in with your Pinterest Business account
    3. Click "My Apps" → "Create App"
    4. App name: "USContentHub Auto-Pin" (or anything)
    5. Under "Scopes", enable: boards:read, boards:write, pins:write
    6. Click "Generate token" — copy the access token
    7. Paste it below (export PINTEREST_ACCESS_TOKEN=...)

IMPORTANT: Pinterest requires a BUSINESS account to use the API.
    Convert at: https://business.pinterest.com/

This script does NOT post to Pinterest — it only sets up your boards and
prints the secrets you need. Safe to run multiple times.
"""

import json
import os
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests is not installed. Run:  pip install requests")
    sys.exit(1)

# ── Publication → GitHub Secret mapping ───────────────────────────────────────
PUBLICATIONS = [
    {
        "slug":        "tech-gadget-hub",
        "secret_name": "PINTEREST_BOARD_TECH",
        "board_name":  "Tech Gadget Hub",
        "description": "Tech reviews, gadget guides, and digital trends",
        "emoji":       "💻",
    },
    {
        "slug":        "health-wellness-daily",
        "secret_name": "PINTEREST_BOARD_HEALTH",
        "board_name":  "Health Wellness Daily",
        "description": "Health tips, wellness guides, and fitness advice",
        "emoji":       "🏃",
    },
    {
        "slug":        "smart-money-guide",
        "secret_name": "PINTEREST_BOARD_FINANCE",
        "board_name":  "Smart Money Guide",
        "description": "Personal finance tips, budgeting, and investing strategies",
        "emoji":       "💰",
    },
    {
        "slug":        "usa-travel-explorer",
        "secret_name": "PINTEREST_BOARD_TRAVEL",
        "board_name":  "USA Travel Explorer",
        "description": "Travel destinations, road trips, and vacation ideas",
        "emoji":       "✈️",
    },
    {
        "slug":        "recipe-kitchen-usa",
        "secret_name": "PINTEREST_BOARD_RECIPES",
        "board_name":  "Recipe Kitchen USA",
        "description": "Easy recipes, meal prep ideas, and food inspiration",
        "emoji":       "🍳",
    },
    {
        "slug":        "usa-news-digest",
        "secret_name": "PINTEREST_BOARD_NEWS",
        "board_name":  "USA News Digest",
        "description": "US news, current events, and trending topics",
        "emoji":       "📰",
    },
    {
        "slug":        "the-trading-blueprint",
        "secret_name": "PINTEREST_BOARD_TRADING",
        "board_name":  "The Trading Blueprint",
        "description": "Stock market strategies, trading tips, and investing insights",
        "emoji":       "📈",
    },
]

SITE_URL = "https://us-content-hub.vercel.app"
PINTEREST_API_BASE = "https://api.pinterest.com/v5"
BOARD_IDS_FILE = Path(__file__).parent / "board_ids.json"


# ── API helpers ───────────────────────────────────────────────────────────────

def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def verify_token(token: str) -> dict:
    """Call /user_account to verify token validity. Returns user info."""
    resp = requests.get(
        f"{PINTEREST_API_BASE}/user_account",
        headers=_headers(token),
        timeout=20,
    )
    if resp.status_code == 401:
        print("\nERROR: Pinterest API returned 401 Unauthorized.")
        print("       Your token is invalid, expired, or missing required scopes.")
        print("       Required scopes: boards:read  boards:write  pins:write\n")
        sys.exit(1)
    if resp.status_code == 403:
        print("\nERROR: Pinterest API returned 403 Forbidden.")
        print("       Your account may not be a Business account, or the app")
        print("       has not been approved for the required scopes.\n")
        sys.exit(1)
    resp.raise_for_status()
    return resp.json()


def get_all_boards(token: str) -> list:
    """Fetch all boards (handles pagination)."""
    boards = []
    cursor = None
    while True:
        url = f"{PINTEREST_API_BASE}/boards?page_size=250"
        if cursor:
            url += f"&bookmark={cursor}"
        resp = requests.get(url, headers=_headers(token), timeout=20)
        resp.raise_for_status()
        data = resp.json()
        boards.extend(data.get("items", []))
        cursor = data.get("bookmark")
        if not cursor:
            break
    return boards


def create_board(token: str, name: str, description: str) -> dict | None:
    """Create a new public Pinterest board. Returns board dict or None."""
    payload = {"name": name, "description": description, "privacy": "PUBLIC"}
    resp = requests.post(
        f"{PINTEREST_API_BASE}/boards",
        headers=_headers(token),
        json=payload,
        timeout=20,
    )
    if resp.status_code in (200, 201):
        return resp.json()
    print(f"     WARNING: Could not create board '{name}': "
          f"{resp.status_code} — {resp.text[:300]}")
    return None


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("  Pinterest Board Setup — USContentHub")
    print("=" * 65)
    print()

    # Get token
    token = os.environ.get("PINTEREST_ACCESS_TOKEN", "").strip()
    if not token:
        print("ERROR: PINTEREST_ACCESS_TOKEN is not set.\n")
        print("  Step 1 — Get your token:")
        print("    1. Go to https://developers.pinterest.com/")
        print("    2. Log in with your Pinterest BUSINESS account")
        print("       (Convert at https://business.pinterest.com/ if needed)")
        print("    3. Click 'My Apps' → 'Create App'")
        print("    4. Enable scopes: boards:read  boards:write  pins:write")
        print("    5. Click 'Generate token' and copy it")
        print()
        print("  Step 2 — Run this script:")
        print("    export PINTEREST_ACCESS_TOKEN=your_token_here")
        print("    python pinterest_bot/setup_secrets.py")
        sys.exit(1)

    # Step 1: Verify token
    print("Step 1 — Verifying token...")
    user = verify_token(token)
    username = user.get("username", "unknown")
    print(f"  ✓  Logged in as: @{username}")
    print()

    # Step 2: Fetch existing boards
    print("Step 2 — Fetching existing Pinterest boards...")
    boards = get_all_boards(token)
    board_map = {b["name"].lower().strip(): b for b in boards}
    if boards:
        print(f"  ✓  Found {len(boards)} existing board(s):")
        for b in boards:
            print(f"     • {b['name']}  (ID: {b['id']})")
    else:
        print("  ℹ  No existing boards found — all 8 will be created.")
    print()

    # Step 3: Match or create boards
    print("Step 3 — Matching / creating boards for each publication...")
    result = {}  # secret_name → board_id

    for pub in PUBLICATIONS:
        key = pub["board_name"].lower().strip()
        existing = board_map.get(key)

        if existing:
            board_id = existing["id"]
            print(f"  ✓  {pub['emoji']}  {pub['board_name']:30s}  → existing  (ID: {board_id})")
        else:
            print(f"  +  {pub['emoji']}  {pub['board_name']:30s}  → creating...", end="", flush=True)
            created = create_board(token, pub["board_name"], pub["description"])
            if created:
                board_id = created["id"]
                board_map[key] = created  # update local map
                print(f"  ✓  ID: {board_id}")
            else:
                board_id = "REPLACE_WITH_BOARD_ID"
                print(f"  ✗  FAILED — set {pub['secret_name']} manually")
            time.sleep(1)  # rate limit: 1 create/sec

        result[pub["secret_name"]] = board_id

    print()

    # Step 4: Save board IDs to file
    board_ids_data = {
        "site_url": SITE_URL,
        "username": username,
        "boards": [
            {
                "publication":   pub["board_name"],
                "secret_name":   pub["secret_name"],
                "board_id":      result[pub["secret_name"]],
            }
            for pub in PUBLICATIONS
        ],
    }
    with open(BOARD_IDS_FILE, "w") as f:
        json.dump(board_ids_data, f, indent=2)
    print(f"  Board IDs saved to: {BOARD_IDS_FILE}")
    print()

    # Step 5: Print GitHub CLI commands
    print("=" * 65)
    print("  Step 4 — Copy-paste these commands in your terminal")
    print("           (run from the repo root)")
    print("=" * 65)
    print()
    print("  # Set SITE_URL")
    print(f"  gh secret set SITE_URL --body '{SITE_URL}'")
    print()
    print("  # Set Pinterest board IDs")
    for pub in PUBLICATIONS:
        bid = result[pub["secret_name"]]
        print(f"  gh secret set {pub['secret_name']:30s} --body '{bid}'")
    print()
    print("  # Set access token (enter value when prompted — not echoed)")
    print("  gh secret set PINTEREST_ACCESS_TOKEN")
    print()

    # Step 6: Dry-run instructions
    print("=" * 65)
    print("  Step 5 — Test with a dry run first")
    print("=" * 65)
    print()
    print("  After setting secrets:")
    print("  1. Go to: github.com/Tusharlimbasiya-200-silveroak/USContentHub")
    print("  2. Click Actions → Pinterest Auto-Pin (2x Daily)")
    print("  3. Click 'Run workflow'")
    print("  4. Set dry_run = true  →  Run")
    print("     (generates images + logs, but posts NOTHING to Pinterest)")
    print()
    print("  If the dry run shows '8 articles selected', you're ready.")
    print("  Run again with dry_run = false to go live!")
    print()
    print("=" * 65)
    print("  ALL DONE")
    print("=" * 65)


if __name__ == "__main__":
    main()
