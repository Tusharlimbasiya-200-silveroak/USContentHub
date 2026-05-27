#!/usr/bin/env python3
"""
bucket_low_quality.py
Reads each site's articles.json, moves HTML files with seo_score < 80
into sites/_low_quality/<site>/ and prints a full report.
"""
import json
import shutil
import os
from pathlib import Path

SITES_DIR = Path("/home/tlimbasitlimbasi/USContentHub/sites")
LOW_QUALITY_DIR = SITES_DIR / "_low_quality"
THRESHOLD = 80

SITES = [
    "health-wellness-daily",
    "smart-money-guide",
    "tech-gadget-hub",
    "usa-news-digest",
    "usa-travel-explorer",
    "recipe-kitchen-usa",
    "the-trading-blueprint",
]

grand_moved = 0
grand_kept = 0

for site in SITES:
    site_dir = SITES_DIR / site
    articles_path = site_dir / "articles.json"
    lq_dir = LOW_QUALITY_DIR / site

    if not articles_path.exists():
        print(f"[SKIP] {site}: articles.json not found")
        continue

    with open(articles_path, "r", encoding="utf-8") as f:
        articles = json.load(f)

    moved = []
    kept = []

    for article in articles:
        slug = article.get("slug", "")
        seo_score = article.get("seo_score", 0)
        html_file = site_dir / f"{slug}.html"

        if seo_score < THRESHOLD:
            # Move HTML file if it exists
            if html_file.exists():
                dest = lq_dir / f"{slug}.html"
                shutil.move(str(html_file), str(dest))
                moved.append((slug, seo_score, "MOVED"))
            else:
                moved.append((slug, seo_score, "NO FILE"))
        else:
            kept.append((slug, seo_score))

    grand_moved += len(moved)
    grand_kept += len(kept)

    print(f"\n{'='*60}")
    print(f"SITE: {site}")
    print(f"  Total articles: {len(articles)}")
    print(f"  Moved to _low_quality (score < {THRESHOLD}): {len(moved)}")
    print(f"  Kept in place (score >= {THRESHOLD}): {len(kept)}")

    if moved:
        print(f"\n  --- MOVED (score < {THRESHOLD}) ---")
        for slug, score, status in sorted(moved, key=lambda x: x[1]):
            print(f"    [{status}] score={score:3d}  {slug}")

    if kept:
        print(f"\n  --- KEPT (score >= {THRESHOLD}) ---")
        for slug, score in sorted(kept, key=lambda x: x[1]):
            print(f"    score={score:3d}  {slug}")

print(f"\n{'='*60}")
print(f"GRAND TOTAL:")
print(f"  Moved to _low_quality: {grand_moved}")
print(f"  Kept for improvement:  {grand_kept}")
print(f"  Total processed:       {grand_moved + grand_kept}")
