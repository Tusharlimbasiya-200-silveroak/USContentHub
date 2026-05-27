#!/usr/bin/env python3
"""
Pinterest Auto-Pin Bot for USContentHub
========================================
Reads articles from sites/*/articles.json, generates Pinterest-optimized
1000x1500 pin images using Pillow, and posts them to Pinterest via the v5 API.

HOW IT WORKS:
  - Runs daily via GitHub Actions (cron: every day at 9 AM UTC)
  - Selects 1 fresh article per publication (7 total) that hasn't been pinned yet
  - Generates a branded portrait image (1000x1500px) with title text overlay
  - Posts to the correct Pinterest board for each publication
  - Saves pinned_tracker.json so it never reposts the same article twice

REQUIRED GITHUB SECRETS:
  PINTEREST_ACCESS_TOKEN  → Your Pinterest API v5 Bearer token
  PINTEREST_BOARD_TECH    → Board ID for tech-gadget-hub
  PINTEREST_BOARD_HEALTH  → Board ID for health-wellness-daily
  PINTEREST_BOARD_FINANCE → Board ID for smart-money-guide
  PINTEREST_BOARD_TRAVEL  → Board ID for usa-travel-explorer
  PINTEREST_BOARD_RECIPES → Board ID for recipe-kitchen-usa
  PINTEREST_BOARD_NEWS    → Board ID for usa-news-digest
  PINTEREST_BOARD_TRADING → Board ID for the-trading-blueprint
  SITE_URL                → Your live site URL (e.g. https://us-content-hub.vercel.app)

HOW TO GET PINTEREST API TOKEN:
  1. Go to https://developers.pinterest.com/
  2. Create an app → request 'pins:write' and 'boards:read' scopes
  3. Generate a long-lived access token
  4. Add it as PINTEREST_ACCESS_TOKEN in GitHub repo → Settings → Secrets

HOW TO GET BOARD IDs:
  1. Open your Pinterest board in a browser
  2. The URL is: https://www.pinterest.com/<username>/<board-name>/
  3. Use the API: GET https://api.pinterest.com/v5/boards?page_size=50
     with your token to list all boards and their IDs

Run locally:
  export PINTEREST_ACCESS_TOKEN=your_token
  export PINTEREST_BOARD_TECH=your_board_id
  export SITE_URL=https://your-site.com
  python pinterest_bot/pinterest_auto_pin.py
"""

import base64
import io
import json
import logging
import math
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("pinterest_bot")

# ── Paths ─────────────────────────────────────────────────────────────────────
BOT_DIR = Path(__file__).parent
BASE_DIR = BOT_DIR.parent
SITES_DIR = BASE_DIR / "sites"
TRACKER_FILE = BOT_DIR / "pinned_tracker.json"

# ── Config from environment ───────────────────────────────────────────────────
PINTEREST_ACCESS_TOKEN = os.environ.get("PINTEREST_ACCESS_TOKEN", "")
SITE_URL = os.environ.get("SITE_URL", "https://us-content-hub.vercel.app").rstrip("/")
PINS_PER_DAY = int(os.environ.get("PINS_PER_DAY", "7"))
PINTEREST_API_BASE = "https://api.pinterest.com/v5"

# ── Publication config ────────────────────────────────────────────────────────
# Each entry maps publication slug → Pinterest board ID + branding
PUBLICATIONS = {
    "tech-gadget-hub": {
        "board_id": os.environ.get("PINTEREST_BOARD_TECH", ""),
        "name": "Tech Gadget Hub",
        "color": (37, 99, 235),    # #2563eb blue
    },
    "health-wellness-daily": {
        "board_id": os.environ.get("PINTEREST_BOARD_HEALTH", ""),
        "name": "Health Wellness Daily",
        "color": (16, 185, 129),   # #10b981 green
    },
    "smart-money-guide": {
        "board_id": os.environ.get("PINTEREST_BOARD_FINANCE", ""),
        "name": "Smart Money Guide",
        "color": (245, 158, 11),   # #f59e0b amber
    },
    "usa-travel-explorer": {
        "board_id": os.environ.get("PINTEREST_BOARD_TRAVEL", ""),
        "name": "USA Travel Explorer",
        "color": (139, 92, 246),   # #8b5cf6 purple
    },
    "recipe-kitchen-usa": {
        "board_id": os.environ.get("PINTEREST_BOARD_RECIPES", ""),
        "name": "Recipe Kitchen USA",
        "color": (239, 68, 68),    # #ef4444 red
    },
    "usa-news-digest": {
        "board_id": os.environ.get("PINTEREST_BOARD_NEWS", ""),
        "name": "USA News Digest",
        "color": (99, 102, 241),   # #6366f1 indigo
    },
    "the-trading-blueprint": {
        "board_id": os.environ.get("PINTEREST_BOARD_TRADING", ""),
        "name": "The Trading Blueprint",
        "color": (5, 150, 105),    # #059669 emerald
    },
}

# ── Image dimensions (Pinterest best practice) ────────────────────────────────
PIN_WIDTH = 1000
PIN_HEIGHT = 1500
IMAGE_AREA_HEIGHT = 1000   # top 2/3: article cover photo
TEXT_AREA_HEIGHT = 500     # bottom 1/3: branded text panel


# ═══════════════════════════════════════════════════════════════════════════════
# TRACKER — remembers which articles have already been pinned
# ═══════════════════════════════════════════════════════════════════════════════

def load_tracker() -> dict:
    """Load the pinned articles tracker from disk."""
    if TRACKER_FILE.exists():
        with open(TRACKER_FILE) as f:
            return json.load(f)
    return {}


def save_tracker(tracker: dict) -> None:
    """Save updated tracker to disk (gets committed back to the repo by CI)."""
    TRACKER_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TRACKER_FILE, "w") as f:
        json.dump(tracker, f, indent=2, sort_keys=True)
    log.info("Tracker saved — %d total articles pinned so far", len(tracker))


# ═══════════════════════════════════════════════════════════════════════════════
# ARTICLE SELECTION
# ═══════════════════════════════════════════════════════════════════════════════

def load_articles(pub_slug: str) -> list[dict]:
    """Read articles.json for a given publication slug."""
    articles_file = SITES_DIR / pub_slug / "articles.json"
    if not articles_file.exists():
        log.warning("No articles.json found for publication: %s", pub_slug)
        return []
    with open(articles_file) as f:
        articles = json.load(f)
    return [a for a in articles if a.get("status", "published") == "published"]


def select_articles_to_pin(tracker: dict) -> list[dict]:
    """
    Select articles to pin today.
    - Only considers publications that have a board_id configured.
    - Distributes PINS_PER_DAY evenly across active publications.
    - Picks newest articles first that haven't been pinned yet.
    """
    active_pubs = [
        (slug, info)
        for slug, info in PUBLICATIONS.items()
        if info["board_id"]
    ]

    if not active_pubs:
        log.warning(
            "No Pinterest board IDs configured. "
            "Set at least one PINTEREST_BOARD_* environment variable."
        )
        return []

    per_pub = max(1, math.ceil(PINS_PER_DAY / len(active_pubs)))
    to_pin = []

    for pub_slug, pub_info in active_pubs:
        articles = load_articles(pub_slug)
        # Sort newest first
        articles.sort(key=lambda a: a.get("date", ""), reverse=True)
        # Remove already-pinned articles
        unpinned = [a for a in articles if a["slug"] not in tracker]
        selected = unpinned[:per_pub]

        log.info(
            "[%s] %d articles total, %d unpinned, selecting %d",
            pub_slug, len(articles), len(unpinned), len(selected),
        )

        for article in selected:
            # Attach publication metadata (removed before API call)
            to_pin.append({
                **article,
                "_pub_slug": pub_slug,
                "_pub_info": pub_info,
            })

    return to_pin


# ═══════════════════════════════════════════════════════════════════════════════
# IMAGE GENERATION — creates branded 1000x1500 Pinterest pin images
# ═══════════════════════════════════════════════════════════════════════════════

def download_image(url: str) -> Image.Image | None:
    """Download an image from a URL and return it as a PIL Image."""
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGB")
        return img
    except Exception as exc:
        log.warning("Image download failed (%s): %s", url, exc)
        return None


def get_fonts() -> tuple:
    """
    Try to load Liberation Sans (available on Ubuntu/GitHub Actions).
    Falls back to PIL's built-in default font.
    Returns (title_font, pub_font, desc_font).
    """
    font_paths = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf",
    ]
    regular_paths = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
    ]

    bold_path = next((p for p in font_paths if Path(p).exists()), None)
    regular_path = next((p for p in regular_paths if Path(p).exists()), None)

    try:
        if bold_path:
            title_font = ImageFont.truetype(bold_path, 46)
            pub_font = ImageFont.truetype(bold_path, 28)
        else:
            title_font = ImageFont.load_default(size=46)
            pub_font = ImageFont.load_default(size=28)

        if regular_path:
            desc_font = ImageFont.truetype(regular_path, 30)
        else:
            desc_font = ImageFont.load_default(size=30)

        return title_font, pub_font, desc_font
    except Exception:
        # Last resort: PIL default fonts
        return (
            ImageFont.load_default(size=46),
            ImageFont.load_default(size=28),
            ImageFont.load_default(size=30),
        )


def wrap_text(text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    """Word-wrap text so each line fits within max_width pixels."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        bbox = font.getbbox(candidate)
        if bbox[2] - bbox[0] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def generate_pin_image(article: dict, pub_info: dict) -> bytes:
    """
    Build a 1000x1500 Pinterest pin image:
      ┌─────────────────────┐
      │                     │ ← Article cover photo (1000x1000)
      │   [cover image]     │
      │                     │
      ├─────────────────────┤
      │  PUBLICATION NAME   │ ← Branded color panel (1000x500)
      │                     │
      │  Article Title Here │
      │  Short description  │
      │  yoursite.com       │
      └─────────────────────┘
    Returns JPEG bytes.
    """
    theme_color = pub_info["color"]
    canvas = Image.new("RGB", (PIN_WIDTH, PIN_HEIGHT), color=(30, 30, 30))

    # ── Top area: article cover image ─────────────────────────────────────────
    image_url = article.get("image", "")

    # Picsum images: make them square for the top area
    if "picsum.photos" in image_url:
        slug = article.get("slug", "pin")
        image_url = f"https://picsum.photos/seed/{slug}/{PIN_WIDTH}/{IMAGE_AREA_HEIGHT}"

    bg_img = download_image(image_url)
    if bg_img:
        # Scale to fill the top area, then center-crop
        orig_w, orig_h = bg_img.size
        scale = max(PIN_WIDTH / orig_w, IMAGE_AREA_HEIGHT / orig_h)
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)
        bg_img = bg_img.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - PIN_WIDTH) // 2
        top_crop = (new_h - IMAGE_AREA_HEIGHT) // 2
        bg_img = bg_img.crop((left, top_crop, left + PIN_WIDTH, top_crop + IMAGE_AREA_HEIGHT))
        canvas.paste(bg_img, (0, 0))
    else:
        # Fallback: gradient-style colored block
        fallback = Image.new("RGB", (PIN_WIDTH, IMAGE_AREA_HEIGHT), color=tuple(max(0, c - 40) for c in theme_color))
        canvas.paste(fallback, (0, 0))

    # ── Bottom area: branded text panel ───────────────────────────────────────
    panel = Image.new("RGB", (PIN_WIDTH, TEXT_AREA_HEIGHT), color=theme_color)
    draw = ImageDraw.Draw(panel)
    title_font, pub_font, desc_font = get_fonts()

    padding = 44
    y = 28
    max_text_w = PIN_WIDTH - (padding * 2)

    # Publication name (uppercase, slightly transparent white)
    pub_name = pub_info["name"].upper()
    draw.text((padding, y), pub_name, fill=(255, 255, 255, 210), font=pub_font)
    y += 36

    # Thin white divider
    draw.line([(padding, y), (PIN_WIDTH - padding, y)], fill=(255, 255, 255, 120), width=2)
    y += 18

    # Article title — up to 3 lines
    title = article.get("title", "Untitled")
    title_lines = wrap_text(title, title_font, max_text_w)[:3]
    for line in title_lines:
        draw.text((padding, y), line, fill=(255, 255, 255), font=title_font)
        bbox = title_font.getbbox(line)
        y += (bbox[3] - bbox[1]) + 8
    y += 10

    # Meta description — up to 2 lines
    desc = article.get("meta_description", "")
    desc_lines = wrap_text(desc, desc_font, max_text_w)[:2]
    for line in desc_lines:
        draw.text((padding, y), line, fill=(235, 235, 215), font=desc_font)
        bbox = desc_font.getbbox(line)
        y += (bbox[3] - bbox[1]) + 5

    # Site URL watermark at very bottom
    site_label = SITE_URL.replace("https://", "").replace("http://", "")
    draw.text(
        (padding, TEXT_AREA_HEIGHT - 44),
        f"Read more: {site_label}",
        fill=(255, 255, 255, 180),
        font=pub_font,
    )

    canvas.paste(panel, (0, IMAGE_AREA_HEIGHT))

    # Encode to JPEG bytes
    buf = io.BytesIO()
    canvas.save(buf, format="JPEG", quality=92, optimize=True)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════════
# PINTEREST API — creates pins via Pinterest v5 API
# ═══════════════════════════════════════════════════════════════════════════════

def create_pin(article: dict, pub_info: dict, image_bytes: bytes) -> str | None:
    """
    POST a new pin to Pinterest using the v5 API.
    Returns the pin ID string on success, None on failure.

    API docs: https://developers.pinterest.com/docs/api/v5/#operation/pins/create
    """
    board_id = pub_info["board_id"]
    article_url = f"{SITE_URL}/article/{article['slug']}/"

    # Build hashtags from tags (Pinterest allows hashtags in description)
    tags = article.get("tags", [])
    if tags:
        hashtags = " ".join(f"#{t.replace(' ', '').replace('-', '')}" for t in tags[:8])
        description = f"{article.get('meta_description', '')}\n\n{hashtags}"
    else:
        description = article.get("meta_description", "")

    payload = {
        "board_id": board_id,
        "title": article["title"][:100],        # Pinterest max: 100 chars
        "description": description[:500],        # Pinterest max: 500 chars
        "link": article_url,
        "alt_text": article.get("meta_description", article["title"])[:500],
        "media_source": {
            "source_type": "image_base64",
            "content_type": "image/jpeg",
            "data": base64.b64encode(image_bytes).decode("utf-8"),
        },
    }

    headers = {
        "Authorization": f"Bearer {PINTEREST_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(
            f"{PINTEREST_API_BASE}/pins",
            headers=headers,
            json=payload,
            timeout=60,
        )

        if resp.status_code == 201:
            pin_data = resp.json()
            pin_id = pin_data.get("id", "unknown")
            log.info("✅ Pinned: '%s' → pin_id=%s", article["title"][:65], pin_id)
            return pin_id

        elif resp.status_code == 429:
            # Rate limited — wait 60 seconds and retry once
            retry_after = int(resp.headers.get("Retry-After", 60))
            log.warning("Rate limited. Waiting %ds before retry...", retry_after)
            time.sleep(retry_after)
            # Retry once
            resp2 = requests.post(
                f"{PINTEREST_API_BASE}/pins",
                headers=headers,
                json=payload,
                timeout=60,
            )
            if resp2.status_code == 201:
                pin_id = resp2.json().get("id", "unknown")
                log.info("✅ Pinned (after retry): '%s' → pin_id=%s", article["title"][:65], pin_id)
                return pin_id
            log.error("Still rate-limited after retry. Skipping.")
            return None

        elif resp.status_code == 401:
            log.error(
                "Pinterest API: 401 Unauthorized. "
                "Check that PINTEREST_ACCESS_TOKEN is valid and has 'pins:write' scope."
            )
            return None

        else:
            log.error(
                "Pinterest API error %d for '%s': %s",
                resp.status_code, article["title"][:60], resp.text[:300],
            )
            return None

    except requests.RequestException as exc:
        log.error("Network error posting '%s': %s", article["title"][:60], exc)
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    log.info("=" * 60)
    log.info("  Pinterest Auto-Pin Bot — USContentHub")
    log.info("  Date: %s UTC", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"))
    log.info("=" * 60)

    if not PINTEREST_ACCESS_TOKEN:
        log.error(
            "PINTEREST_ACCESS_TOKEN is not set!\n"
            "1. Get a token from https://developers.pinterest.com/\n"
            "2. Add it as a GitHub secret named PINTEREST_ACCESS_TOKEN"
        )
        sys.exit(1)

    log.info("Config: PINS_PER_DAY=%d, SITE_URL=%s", PINS_PER_DAY, SITE_URL)

    # Load tracker
    tracker = load_tracker()
    log.info("Tracker: %d articles already pinned", len(tracker))

    # Select articles for today
    to_pin = select_articles_to_pin(tracker)
    log.info("Articles selected for today: %d", len(to_pin))

    if not to_pin:
        log.info(
            "Nothing to pin today. Either:\n"
            "  - All articles are already pinned (add more content!)\n"
            "  - No PINTEREST_BOARD_* secrets are configured"
        )
        return

    pinned_count = 0

    for article in to_pin:
        # Remove internal metadata keys before processing
        pub_slug = article.pop("_pub_slug")
        pub_info = article.pop("_pub_info")

        log.info("─" * 50)
        log.info("Processing: [%s] %s", pub_slug, article["title"][:70])

        # Step 1: Generate the pin image
        try:
            image_bytes = generate_pin_image(article, pub_info)
            log.info("  Image generated: %d KB", len(image_bytes) // 1024)
        except Exception as exc:
            log.error("  Image generation failed: %s", exc)
            continue

        # Step 2: Post to Pinterest
        pin_id = create_pin(article, pub_info, image_bytes)

        if pin_id:
            tracker[article["slug"]] = {
                "pin_id": pin_id,
                "pinned_at": datetime.now(timezone.utc).isoformat(),
                "publication": pub_slug,
                "title": article["title"],
                "board_id": pub_info["board_id"],
            }
            pinned_count += 1

        # Be polite to the API — 3-second gap between pins
        time.sleep(3)

    # Save tracker (CI will commit this file back to the repo)
    save_tracker(tracker)

    log.info("=" * 60)
    log.info("  DONE: %d/%d pins created successfully", pinned_count, len(to_pin))
    log.info("=" * 60)


if __name__ == "__main__":
    main()
