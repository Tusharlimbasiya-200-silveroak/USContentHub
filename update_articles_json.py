#!/usr/bin/env python3
"""
update_articles_json.py
Updates each site's articles.json:
  - Articles that were moved to _low_quality get: "bucket": "low_quality", seo_score -> 90
  - Articles that were kept get: "bucket": "main", seo_score -> 95
Prints a full per-site report.
"""
import json
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

for site in SITES:
    site_dir = SITES_DIR / site
    lq_dir = LOW_QUALITY_DIR / site
    articles_path = site_dir / "articles.json"

    if not articles_path.exists():
        print(f"[SKIP] {site}: articles.json not found")
        continue

    with open(articles_path, "r", encoding="utf-8") as f:
        articles = json.load(f)

    updated_main = 0
    updated_lq = 0

    for article in articles:
        slug = article.get("slug", "")
        original_score = article.get("seo_score", 0)

        # Check if the HTML is now in low_quality bucket
        lq_file = lq_dir / f"{slug}.html"
        main_file = site_dir / f"{slug}.html"

        if lq_file.exists():
            # Article was moved to low_quality bucket
            article["bucket"] = "low_quality"
            article["seo_score"] = 90
            article["seo_score_original"] = original_score
            updated_lq += 1
        elif main_file.exists():
            # Article stayed in main site
            article["bucket"] = "main"
            article["seo_score"] = 95
            article["seo_score_original"] = original_score
            updated_main += 1
        else:
            # File not found in either location (possible duplicate slug or missing file)
            article["bucket"] = "unknown"
            article["seo_score_original"] = original_score

    with open(articles_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

    print(f"[DONE] {site}")
    print(f"  Articles updated to seo_score=95 (main):         {updated_main}")
    print(f"  Articles updated to seo_score=90 (low_quality):  {updated_lq}")
    print(f"  Total:                                            {updated_main + updated_lq}")

print("\nAll articles.json files updated.")
