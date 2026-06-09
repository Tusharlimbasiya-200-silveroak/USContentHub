#!/usr/bin/env python3
"""
Pinterest Auto-Pin Bot for USContentHub
========================================
Posts fresh blog articles to Pinterest TWICE per day:
  • Morning session  (10:00 AM IST / 04:30 UTC)
  • Evening session  (07:00 PM IST / 13:30 UTC)

HOW IT WORKS:
  - Runs via GitHub Actions cron (2x daily) or manually
  - Reads articles from sites/*/articles.json
  - Skips any article already in pinned_tracker.json (no duplicates, ever)
  - Generates a branded 1000x1500 pin image with Pillow
  - Posts to the correct Pinterest board via the v5 API
  - Saves pinned_tracker.json so it never reposts the same article

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

OPTIONAL ENV VARS:
  SESSION          → "morning" or "evening" (auto-detected from UTC hour if not set)
  PINS_PER_SESSION → How many pins to post this session (default: 7)
  DRY_RUN          → "true" to generate images but NOT post to Pinterest

HOW TO GET A PINTEREST BUSINESS API TOKEN:
  1. Go to https://developers.pinterest.com/
  2. Create an app → enable Business account access
  3. Request scopes: pins:write, boards:read
  4. Generate a long-lived access token
  5. Add it as PINTEREST_ACCESS_TOKEN in GitHub → Settings → Secrets

HOW TO GET BOARD IDs:
  GET https://api.pinterest.com/v5/boards?page_size=50
  with Authorization: Bearer <your_token>
  Each board object has an "id" field — copy that into your secrets.

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
PINS_PER_SESSION = int(os.environ.get("PINS_PER_SESSION", "8"))
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"
PINTEREST_API_BASE = "https://api.pinterest.com/v5"

# ── Session detection (morning / evening) ─────────────────────────────────────
_raw_session = os.environ.get("SESSION", "").lower()
if _raw_session in ("morning", "evening"):
    SESSION = _raw_session
else:
    _utc_hour = datetime.now(timezone.utc).hour
    SESSION = "morning" if _utc_hour < 12 else "evening"

# ── Publication config ────────────────────────────────────────────────────────
PUBLICATIONS = {
    "tech-gadget-hub": {
        "board_id": os.environ.get("PINTEREST_BOARD_TECH", ""),
        "name": "Tech Gadget Hub",
        "color": (37, 99, 235),      # #2563eb blue
        "hashtags": [
            "#TechNews", "#Gadgets", "#Technology", "#TechTips",
            "#Innovation", "#TechGadgets", "#FutureTech",
        ],
    },
    "health-wellness-daily": {
        "board_id": os.environ.get("PINTEREST_BOARD_HEALTH", ""),
        "name": "Health Wellness Daily",
        "color": (16, 185, 129),     # #10b981 green
        "hashtags": [
            "#HealthTips", "#Wellness", "#HealthyLiving", "#SelfCare",
            "#WellnessTips", "#HealthyHabits", "#MindBodySoul",
        ],
    },
    "smart-money-guide": {
        "board_id": os.environ.get("PINTEREST_BOARD_FINANCE", ""),
        "name": "Smart Money Guide",
        "color": (245, 158, 11),     # #f59e0b amber
        "hashtags": [
            "#PersonalFinance", "#MoneyTips", "#FinancialFreedom",
            "#SaveMoney", "#MoneyManagement", "#BudgetTips", "#Investing",
        ],
    },
    "usa-travel-explorer": {
        "board_id": os.environ.get("PINTEREST_BOARD_TRAVEL", ""),
        "name": "USA Travel Explorer",
        "color": (139, 92, 246),     # #8b5cf6 purple
        "hashtags": [
            "#USATravel", "#TravelTips", "#Wanderlust", "#RoadTrip",
            "#USAAdventure", "#TravelUSA", "#ExploreAmerica",
        ],
    },
    "recipe-kitchen-usa": {
        "board_id": os.environ.get("PINTEREST_BOARD_RECIPES", ""),
        "name": "Recipe Kitchen USA",
        "color": (239, 68, 68),      # #ef4444 red
        "hashtags": [
            "#Recipes", "#EasyRecipes", "#HomeCooking", "#MealPrep",
            "#FoodIdeas", "#CookingTips", "#DinnerIdeas",
        ],
    },
    "usa-news-digest": {
        "board_id": os.environ.get("PINTEREST_BOARD_NEWS", ""),
        "name": "USA News Digest",
        "color": (99, 102, 241),     # #6366f1 indigo
        "hashtags": [
            "#USANews", "#CurrentEvents", "#NewsDigest",
            "#AmericaNews", "#TodayNews", "#BreakingNews", "#Politics",
        ],
    },
    "the-trading-blueprint": {
        "board_id": os.environ.get("PINTEREST_BOARD_TRADING", ""),
        "name": "The Trading Blueprint",
        "color": (5, 150, 105),      # #059669 emerald
        "hashtags": [
            "#StockMarket", "#TradingTips", "#Investing", "#FinanceTips",
            "#WealthBuilding", "#StockTrading", "#DayTrading",
        ],
    },
}

# ── Session-specific call-to-action text ──────────────────────────────────────
SESSION_CTA = {
    "morning": "Start your morning right! Save this for later.",
    "evening": "Perfect evening read. Save this pin!",
}

# ── Image dimensions (Pinterest 2:3 best practice) ────────────────────────────
PIN_WIDTH = 1000
PIN_HEIGHT = 1500
IMAGE_AREA_HEIGHT = 900   # top 60%: article cover photo
TEXT_AREA_HEIGHT = 600    # bottom 40%: branded text panel


# ═══════════════════════════════════════════════════════════════════════════════
# TRACKER — remembers which articles have already been pinned
# Key format: "pub_slug/article_slug"  (namespaced to avoid cross-pub collisions)
# ═══════════════════════════════════════════════════════════════════════════════

def load_tracker() -> dict:
    """Load the pinned articles tracker from disk."""
    if TRACKER_FILE.exists():
        with open(TRACKER_FILE) as f:
            return json.load(f)
    return {}


def save_tracker(tracker: dict) -> None:
    """Save updated tracker to disk (CI commits this file back to the repo)."""
    TRACKER_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TRACKER_FILE, "w") as f:
        json.dump(tracker, f, indent=2, sort_keys=True)
    log.info("Tracker saved — %d total articles pinned so far", len(tracker))


def tracker_key(pub_slug: str, article_slug: str) -> str:
    """Unique key per article per publication."""
    return f"{pub_slug}/{article_slug}"


# ═══════════════════════════════════════════════════════════════════════════════
# ARTICLE SELECTION
# ═══════════════════════════════════════════════════════════════════════════════

def load_articles(pub_slug: str) -> list[dict]:
    """Read articles.json for a given publication slug."""
    articles_file = SITES_DIR / pub_slug / "articles.json"
    if not articles_file.exists():
        log.warning("No articles.json found for: %s", pub_slug)
        return []
    with open(articles_file) as f:
        articles = json.load(f)
    # Only published articles; prefer main-bucket (high quality) over low_quality
    published = [a for a in articles if a.get("status", "published") == "published"]
    main = [a for a in published if a.get("bucket", "main") != "low_quality"]
    return main if main else published


def select_articles_to_pin(tracker: dict) -> list[dict]:
    """
    Select articles to pin for this session.
    - Only uses publications that have a board_id configured.
    - 1 article per active publication, up to PINS_PER_SESSION total.
    - Picks newest articles first that haven't been pinned yet.
    - Prefers featured articles when available.
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

    to_pin = []

    for pub_slug, pub_info in active_pubs:
        if len(to_pin) >= PINS_PER_SESSION:
            break

        articles = load_articles(pub_slug)

        # Sort: featured first, then newest
        articles.sort(
            key=lambda a: (not a.get("featured", False), a.get("date", "")),
            reverse=True,
        )

        # Filter out already-pinned articles
        unpinned = [
            a for a in articles
            if tracker_key(pub_slug, a["slug"]) not in tracker
        ]

        if not unpinned:
            log.info("[%s] All %d articles already pinned — nothing new", pub_slug, len(articles))
            continue

        article = unpinned[0]  # pick the best unpinned article

        log.info(
            "[%s] %d total, %d unpinned → selecting: %s",
            pub_slug, len(articles), len(unpinned), article["title"][:60],
        )

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
    """Download an image from a URL, return as PIL Image."""
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        return Image.open(io.BytesIO(resp.content)).convert("RGB")
    except Exception as exc:
        log.warning("Image download failed (%s): %s", url, exc)
        return None


def get_fonts() -> tuple:
    """
    Load system fonts for the pin image.
    Returns (title_font, pub_font, desc_font, cta_font).
    Falls back to PIL built-in fonts if system fonts not found.
    """
    bold_candidates = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf",
    ]
    regular_candidates = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
    ]

    bold = next((p for p in bold_candidates if Path(p).exists()), None)
    regular = next((p for p in regular_candidates if Path(p).exists()), None)

    def load(path, size, fallback_size):
        try:
            return ImageFont.truetype(path, size) if path else ImageFont.load_default(size=fallback_size)
        except Exception:
            return ImageFont.load_default(size=fallback_size)

    return (
        load(bold, 50, 50),       # title_font
        load(bold, 26, 26),       # pub_font
        load(regular, 28, 28),    # desc_font
        load(bold, 30, 30),       # cta_font
    )


def wrap_text(text: str, font, max_width: int) -> list[str]:
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


def add_gradient_overlay(img: Image.Image, height: int, gradient_zone: int) -> Image.Image:
    """
    Add a dark gradient fade at the bottom of img (for visual transition
    into the branded text panel below).
    """
    overlay = Image.new("RGBA", (img.width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for i in range(gradient_zone):
        alpha = int(180 * (i / gradient_zone))
        y = height - gradient_zone + i
        draw.line([(0, y), (img.width, y)], fill=(0, 0, 0, alpha))
    base = img.convert("RGBA")
    composited = Image.alpha_composite(base, overlay)
    return composited.convert("RGB")


def generate_pin_image(article: dict, pub_info: dict) -> bytes:
    """
    Build a 1000x1500 Pinterest pin image.

    Layout:
    ┌──────────────────────────────┐
    │                              │
    │      Article cover image     │  ← 1000 x 900 px
    │                              │
    │  ░░░ dark gradient fade ░░░  │  ← smooth transition
    ├──────────────────────────────┤
    │  ● PUBLICATION NAME          │  ← brand color panel (1000 x 600 px)
    │  ─────────────────────────── │
    │  Article Title Here          │
    │  (up to 3 lines)             │
    │                              │
    │  Short description text...   │
    │                              │
    │  [ READ NOW → ]              │  ← white CTA button
    │                    ○ ○ ○     │
    │  yoursite.com                │
    └──────────────────────────────┘

    Returns JPEG bytes.
    """
    theme_color = pub_info["color"]
    canvas = Image.new("RGB", (PIN_WIDTH, PIN_HEIGHT), color=(20, 20, 20))

    # ── Top area: article cover image ─────────────────────────────────────────
    image_url = article.get("image", "")

    # Picsum seed-based image: request correct dimensions
    if "picsum.photos" in image_url:
        slug = article.get("slug", "pin")
        image_url = f"https://picsum.photos/seed/{slug}/{PIN_WIDTH}/{IMAGE_AREA_HEIGHT}"

    bg_img = download_image(image_url)
    if bg_img:
        # Scale to fill, then center-crop
        orig_w, orig_h = bg_img.size
        scale = max(PIN_WIDTH / orig_w, IMAGE_AREA_HEIGHT / orig_h)
        new_w, new_h = int(orig_w * scale), int(orig_h * scale)
        bg_img = bg_img.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - PIN_WIDTH) // 2
        top_crop = (new_h - IMAGE_AREA_HEIGHT) // 2
        bg_img = bg_img.crop((left, top_crop, left + PIN_WIDTH, top_crop + IMAGE_AREA_HEIGHT))

        # Add smooth gradient fade at bottom of photo
        bg_img = add_gradient_overlay(bg_img, IMAGE_AREA_HEIGHT, gradient_zone=280)
        canvas.paste(bg_img, (0, 0))
    else:
        # Fallback: darker shade of the brand color
        fallback_color = tuple(max(0, c - 50) for c in theme_color)
        canvas.paste(Image.new("RGB", (PIN_WIDTH, IMAGE_AREA_HEIGHT), fallback_color), (0, 0))

    # ── Bottom area: branded text panel ───────────────────────────────────────
    panel = Image.new("RGB", (PIN_WIDTH, TEXT_AREA_HEIGHT), color=theme_color)
    draw = ImageDraw.Draw(panel)
    title_font, pub_font, desc_font, cta_font = get_fonts()

    padding = 48
    y = 32
    max_text_w = PIN_WIDTH - (padding * 2)

    # ── Publication name with colored dot ─────────────────────────────────────
    dot_r = 8
    dot_x, dot_y = padding, y + 9
    draw.ellipse(
        [(dot_x, dot_y), (dot_x + dot_r * 2, dot_y + dot_r * 2)],
        fill=(255, 255, 255, 220),
    )
    pub_name = pub_info["name"].upper()
    draw.text((padding + dot_r * 2 + 10, y), pub_name, fill=(255, 255, 255), font=pub_font)
    y += 38

    # ── Thin white divider ────────────────────────────────────────────────────
    draw.line([(padding, y), (PIN_WIDTH - padding, y)], fill=(255, 255, 255, 100), width=1)
    y += 20

    # ── Article title (up to 3 lines) ─────────────────────────────────────────
    title = article.get("title", "Untitled")
    title_lines = wrap_text(title, title_font, max_text_w)[:3]
    for line in title_lines:
        draw.text((padding, y), line, fill=(255, 255, 255), font=title_font)
        bbox = title_font.getbbox(line)
        y += (bbox[3] - bbox[1]) + 6
    y += 14

    # ── Meta description (up to 2 lines) ──────────────────────────────────────
    desc = article.get("meta_description", "")
    if desc:
        desc_lines = wrap_text(desc, desc_font, max_text_w)[:2]
        for line in desc_lines:
            draw.text((padding, y), line, fill=(235, 235, 215), font=desc_font)
            bbox = desc_font.getbbox(line)
            y += (bbox[3] - bbox[1]) + 4
    y += 18

    # ── CTA Button: "READ NOW →" ──────────────────────────────────────────────
    cta_text = "READ NOW  →"
    cta_bbox = cta_font.getbbox(cta_text)
    cta_w = cta_bbox[2] - cta_bbox[0] + 40
    cta_h = cta_bbox[3] - cta_bbox[1] + 18
    btn_x1, btn_y1 = padding, y
    btn_x2, btn_y2 = padding + cta_w, y + cta_h

    try:
        draw.rounded_rectangle(
            [(btn_x1, btn_y1), (btn_x2, btn_y2)],
            radius=6,
            fill=(255, 255, 255),
        )
    except AttributeError:
        # Pillow < 8.2: fallback to regular rectangle
        draw.rectangle([(btn_x1, btn_y1), (btn_x2, btn_y2)], fill=(255, 255, 255))

    draw.text(
        (btn_x1 + 20, btn_y1 + 9),
        cta_text,
        fill=theme_color,
        font=cta_font,
    )

    # ── Decorative dots (bottom right corner) ─────────────────────────────────
    dot_size = 7
    dot_spacing = 18
    dots_y = TEXT_AREA_HEIGHT - 48
    for i in range(3):
        dx = PIN_WIDTH - padding - (2 - i) * dot_spacing
        draw.ellipse(
            [(dx, dots_y), (dx + dot_size, dots_y + dot_size)],
            fill=(255, 255, 255, 80),
        )

    # ── Site URL watermark ────────────────────────────────────────────────────
    site_label = SITE_URL.replace("https://", "").replace("http://", "")
    draw.text(
        (padding, TEXT_AREA_HEIGHT - 42),
        site_label,
        fill=(255, 255, 255, 160),
        font=pub_font,
    )

    canvas.paste(panel, (0, IMAGE_AREA_HEIGHT))

    # ── Encode to JPEG ────────────────────────────────────────────────────────
    buf = io.BytesIO()
    canvas.save(buf, format="JPEG", quality=92, optimize=True)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════════
# DESCRIPTION BUILDER — Pinterest best practices
# ═══════════════════════════════════════════════════════════════════════════════

def build_description(article: dict, pub_slug: str, pub_info: dict) -> str:
    """
    Build a Pinterest-optimised pin description:
      - Session-specific CTA opener
      - Article meta description
      - Relevant hashtags (article tags + publication niche tags)

    Pinterest tips applied:
      • Keep under 500 characters
      • Use 5–15 hashtags
      • Include a clear call-to-action
      • Front-load the most important content
    """
    cta = SESSION_CTA.get(SESSION, "Save this pin for later!")
    meta = article.get("meta_description", "").strip()

    # Hashtags from article tags
    article_tags = article.get("tags", [])
    article_hashtags = [
        f"#{t.replace(' ', '').replace('-', '').capitalize()}"
        for t in article_tags[:5]
        if t
    ]

    # Publication-specific niche hashtags
    pub_hashtags = pub_info.get("hashtags", [])[:7]

    all_hashtags = list(dict.fromkeys(article_hashtags + pub_hashtags))  # deduplicate, preserve order
    hashtag_str = " ".join(all_hashtags[:12])  # Pinterest: use 5–15 hashtags

    # Build final description
    parts = [cta]
    if meta:
        parts.append(meta)
    parts.append(hashtag_str)

    description = "\n\n".join(parts)
    return description[:500]  # Pinterest maximum


# ═══════════════════════════════════════════════════════════════════════════════
# PINTEREST API — creates pins via Pinterest v5 API
# ═══════════════════════════════════════════════════════════════════════════════

def create_pin(article: dict, pub_info: dict, pub_slug: str, image_bytes: bytes) -> str | None:
    """
    POST a new pin to Pinterest using the v5 API.
    Returns the pin ID on success, None on failure.

    Pinterest best practices applied:
      • Title: keyword-rich, under 100 characters
      • Description: CTA + meta desc + hashtags, under 500 characters
      • Alt text: descriptive for accessibility and SEO
      • Link: direct URL to the article
      • Image: 2:3 ratio (1000x1500), JPEG, high quality
    """
    if DRY_RUN:
        log.info("[DRY RUN] Would post: '%s'", article["title"][:70])
        return "dry-run-no-pin-id"

    board_id = pub_info["board_id"]

    # Article URL — try to build the cleanest possible link
    article_url = f"{SITE_URL}/article/{article['slug']}/"

    title = article["title"][:100]
    description = build_description(article, pub_slug, pub_info)
    alt_text = (article.get("meta_description") or article["title"])[:500]

    payload = {
        "board_id": board_id,
        "title": title,
        "description": description,
        "link": article_url,
        "alt_text": alt_text,
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

    def _post() -> requests.Response:
        return requests.post(
            f"{PINTEREST_API_BASE}/pins",
            headers=headers,
            json=payload,
            timeout=60,
        )

    try:
        resp = _post()

        if resp.status_code == 201:
            pin_id = resp.json().get("id", "unknown")
            log.info("Pinned: '%s' → pin_id=%s", article["title"][:65], pin_id)
            return pin_id

        elif resp.status_code == 429:
            # Rate limited — wait and retry once
            retry_after = int(resp.headers.get("Retry-After", 60))
            log.warning("Rate limited. Waiting %ds...", retry_after)
            time.sleep(retry_after)
            resp2 = _post()
            if resp2.status_code == 201:
                pin_id = resp2.json().get("id", "unknown")
                log.info("Pinned (after retry): '%s' → pin_id=%s", article["title"][:65], pin_id)
                return pin_id
            log.error("Still rate-limited after retry. Skipping article.")
            return None

        elif resp.status_code == 401:
            log.error(
                "Pinterest 401 Unauthorized — "
                "check PINTEREST_ACCESS_TOKEN has 'pins:write' scope "
                "and that your Pinterest app is approved for business access."
            )
            sys.exit(1)  # Fatal: all pins will fail, stop immediately

        else:
            log.error(
                "Pinterest API error %d for '%s': %s",
                resp.status_code, article["title"][:60], resp.text[:400],
            )
            return None

    except requests.RequestException as exc:
        log.error("Network error posting '%s': %s", article["title"][:60], exc)
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    log.info("=" * 65)
    log.info("  Pinterest Auto-Pin Bot — USContentHub")
    log.info("  Date:    %s UTC", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"))
    log.info("  Session: %s", SESSION.upper())
    log.info("  DRY_RUN: %s", DRY_RUN)
    log.info("=" * 65)

    if not PINTEREST_ACCESS_TOKEN and not DRY_RUN:
        log.error(
            "PINTEREST_ACCESS_TOKEN is not set!\n"
            "  1. Create a Pinterest Business app at https://developers.pinterest.com/\n"
            "  2. Request 'pins:write' and 'boards:read' scopes\n"
            "  3. Add the token as a GitHub secret: PINTEREST_ACCESS_TOKEN"
        )
        sys.exit(1)

    log.info("Config: PINS_PER_SESSION=%d, SITE_URL=%s", PINS_PER_SESSION, SITE_URL)

    # Load tracker
    tracker = load_tracker()
    log.info("Tracker: %d articles already pinned (never re-pinned)", len(tracker))

    # Select articles for this session
    to_pin = select_articles_to_pin(tracker)
    log.info("Articles selected for this %s session: %d", SESSION, len(to_pin))

    if not to_pin:
        log.info(
            "Nothing to pin in this session. Possible reasons:\n"
            "  1. All articles already pinned — add more content!\n"
            "  2. No PINTEREST_BOARD_* secrets are configured"
        )
        return

    pinned_count = 0

    for article in to_pin:
        pub_slug = article.pop("_pub_slug")
        pub_info = article.pop("_pub_info")

        log.info("─" * 55)
        log.info("Processing [%s]: %s", pub_slug, article["title"][:65])

        # Generate the pin image
        try:
            image_bytes = generate_pin_image(article, pub_info)
            log.info("  Image generated: %d KB (1000x1500 JPEG)", len(image_bytes) // 1024)
        except Exception as exc:
            log.error("  Image generation failed: %s", exc)
            continue

        # Post to Pinterest (or skip if DRY_RUN)
        pin_id = create_pin(article, pub_info, pub_slug, image_bytes)

        if pin_id:
            key = tracker_key(pub_slug, article["slug"])
            tracker[key] = {
                "pin_id": pin_id,
                "pinned_at": datetime.now(timezone.utc).isoformat(),
                "session": SESSION,
                "publication": pub_slug,
                "title": article["title"],
                "board_id": pub_info["board_id"],
                "dry_run": DRY_RUN,
            }
            pinned_count += 1

        # Polite delay between API calls (avoid rate limits)
        time.sleep(3)

    # Persist tracker
    save_tracker(tracker)

    log.info("=" * 65)
    log.info(
        "  DONE: %d/%d pins posted (%s session)",
        pinned_count, len(to_pin), SESSION.upper(),
    )
    log.info("=" * 65)


if __name__ == "__main__":
    main()
