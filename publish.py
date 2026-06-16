"""Unified publish pipeline — the single source-of-truth path.

One command takes a draft, writes it to the database (the source of truth),
regenerates the matching static files (article HTML + articles.json card +
homepage card + sitemap URL) via `export_static`, and optionally commits — so
the Vercel/Neon site and the GitHub Pages static site can never drift apart
again. Push afterwards and `deploy-sites.yml` ships the static side.

Usage:
    # Target whichever DB env you point at (local by default; prod via env):
    python3 publish.py drafts/my-article.json --commit
    DATABASE_URL='postgres://…neon…' python3 publish.py drafts/my-article.json --commit

Draft JSON schema (content MUST be the clean article body only — the prose
that goes inside `.article-body`; export_static adds all surrounding chrome):
{
  "publication":      "the-trading-blueprint",   # required, existing pub slug
  "title":            "...",                      # required
  "slug":             "...",                      # required, unique
  "meta_description": "...",                       # <= 300 chars
  "cover_image":      "https://...",              # required (real, hotlinkable)
  "tags":             ["trading", "stocks"],
  "subtitle":         "...",
  "date":             "2026-06-16T12:00:00",      # optional ISO; default now
  "content":          "<p>...</p><h2>...</h2>..." # required, CLEAN body HTML
}
"""
import json
import os
import re
import subprocess
import sys

import django

try:
    from dotenv import load_dotenv
    load_dotenv(os.environ.get("DOTENV_FILE", ".env"))  # does NOT override an env-set DATABASE_URL
except ImportError:
    pass

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "writeflow.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.management import call_command
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from blog.models import Article, Publication, Tag

REQUIRED = ("publication", "title", "slug", "content", "cover_image")
WORDS_PER_MINUTE = 200


def load_draft(path):
    with open(path, encoding="utf-8") as f:
        draft = json.load(f)
    missing = [k for k in REQUIRED if not draft.get(k)]
    if missing:
        sys.exit(f"✗ Draft missing required fields: {', '.join(missing)}")
    if re.search(r'class="(article-body|newsletter-signup|share-buttons|breadcrumb)"', draft["content"]):
        sys.exit("✗ `content` must be the CLEAN body only (no breadcrumb/article-body/newsletter/share chrome).")
    return draft


def upsert(draft):
    try:
        pub = Publication.objects.get(slug=draft["publication"])
    except Publication.DoesNotExist:
        known = ", ".join(Publication.objects.values_list("slug", flat=True))
        sys.exit(f"✗ Unknown publication '{draft['publication']}'. Existing: {known}")

    words = len(re.sub(r"<[^>]+>", " ", draft["content"]).split())
    read_time = max(1, round(words / WORDS_PER_MINUTE))
    pub_date = parse_datetime(draft["date"]) if draft.get("date") else timezone.now()
    if pub_date and timezone.is_naive(pub_date):
        pub_date = timezone.make_aware(pub_date)

    article, created = Article.objects.update_or_create(
        slug=draft["slug"],
        defaults={
            "title": draft["title"],
            "subtitle": draft.get("subtitle", "")[:500],
            "content": draft["content"],
            "cover_image": draft["cover_image"],
            "publication": pub,
            "status": "published",
            "read_time": read_time,
            "word_count": words,
            "meta_description": draft.get("meta_description", "")[:300],
            "published_at": pub_date,
        },
    )
    tags = [Tag.objects.get_or_create(name=n.strip().lower()[:100])[0] for n in draft.get("tags", []) if n]
    article.tags.set(tags)
    print(f"  ✓ {'Created' if created else 'Updated'} DB [published]: {article.title}  ({words} words, ~{read_time} min)")
    return article


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    do_commit = "--commit" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        sys.exit("✗ Provide a draft JSON path.")

    published = []
    for path in paths:
        draft = load_draft(path)
        article = upsert(draft)
        print(f"  → generating static files for {article.publication.slug}/{article.slug} …")
        call_command("export_static", slug=[article.slug])
        published.append(article)

    if do_commit and published:
        site_dirs = sorted({f"sites/{a.publication.slug}/" for a in published})
        subprocess.run(["git", "add", *site_dirs], check=True)
        titles = "; ".join(a.title for a in published)
        subprocess.run(
            ["git", "commit", "-m",
             f"feat(content): publish {len(published)} article(s)\n\n{titles}\n\n"
             "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"],
            check=True,
        )
        print("  ✓ Committed. Run `git push` to deploy the static side via deploy-sites.yml.")
    else:
        print("  ℹ Static files written + staged-ready. Re-run with --commit to commit, then `git push`.")


if __name__ == "__main__":
    main()
