"""
Publish (or stage) a tech-blog draft written by the /tech-blog agent.

Usage:
    python3 publish_draft.py drafts/my-article.json            # create as DRAFT (preview only)
    python3 publish_draft.py drafts/my-article.json --publish  # create/flip to PUBLISHED
    python3 publish_draft.py --delete <slug>                   # remove a rejected draft from DB

Draft JSON schema:
{
  "publication": "tech-pulse",          # slug; auto-created with defaults if missing
  "title":            "...",            # required, <= 300 chars
  "subtitle":         "...",            # <= 500 chars
  "slug":             "...",            # required, unique
  "cover_image":      "https://...",    # optional
  "tags":             ["python", "ai"],
  "meta_description": "...",            # <= 300 chars, for SEO
  "content":          "<p>...</p>"      # required, HTML body
}
"""
import json
import os
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "writeflow.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.utils import timezone

from blog.models import Article, Publication, Tag

# Defaults used if the target publication doesn't exist yet
PUBLICATION_DEFAULTS = {
    "tech-pulse": {
        "name": "Tech Pulse",
        "description": (
            "Developer-focused technology news: Python and language releases, "
            "AI/ML model updates, frameworks, tooling, and what's new across tech."
        ),
        "color": "#7c3aed",
        "icon": "🧠",
    },
}

REQUIRED_FIELDS = ("title", "slug", "content")
WORDS_PER_MINUTE = 200


def load_draft(path):
    with open(path, encoding="utf-8") as f:
        draft = json.load(f)
    missing = [k for k in REQUIRED_FIELDS if not draft.get(k)]
    if missing:
        sys.exit(f"✗ Draft is missing required fields: {', '.join(missing)}")
    if len(draft["title"]) > 300:
        sys.exit("✗ title exceeds 300 chars")
    if len(draft.get("subtitle", "")) > 500:
        sys.exit("✗ subtitle exceeds 500 chars")
    if len(draft.get("meta_description", "")) > 300:
        sys.exit("✗ meta_description exceeds 300 chars")
    return draft


def get_publication(slug):
    defaults = PUBLICATION_DEFAULTS.get(slug)
    if defaults:
        pub, created = Publication.objects.get_or_create(slug=slug, defaults=defaults)
        if created:
            print(f"  ✓ Created publication: {pub.name} ({slug})")
        return pub
    try:
        return Publication.objects.get(slug=slug)
    except Publication.DoesNotExist:
        known = ", ".join(Publication.objects.values_list("slug", flat=True))
        sys.exit(f"✗ Unknown publication '{slug}'. Existing: {known}")


def upsert_article(draft, status):
    pub = get_publication(draft.get("publication", "tech-pulse"))
    # Strip HTML tags for an honest word count
    import re

    text = re.sub(r"<[^>]+>", " ", draft["content"])
    words = len(text.split())
    read_time = max(1, round(words / WORDS_PER_MINUTE))

    article, created = Article.objects.update_or_create(
        slug=draft["slug"],
        defaults={
            "title": draft["title"],
            "subtitle": draft.get("subtitle", ""),
            "content": draft["content"],
            "cover_image": draft.get("cover_image", ""),
            "publication": pub,
            "status": status,
            "read_time": read_time,
            "word_count": words,
            "meta_description": draft.get("meta_description", ""),
            "published_at": timezone.now(),
        },
    )
    tags = []
    for name in draft.get("tags", []):
        tag, _ = Tag.objects.get_or_create(name=name.strip().lower())
        tags.append(tag)
    article.tags.set(tags)

    verb = "Created" if created else "Updated"
    print(f"  ✓ {verb} [{status}]: {article.title}")
    print(f"    slug: {article.slug}  ({words} words, ~{read_time} min read)")
    print(f"    local preview: http://127.0.0.1:8799/article/{article.slug}/")
    print(f"    live (after push): https://us-content-hub.vercel.app/article/{article.slug}/")
    return article


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--delete":
        if len(args) < 2:
            sys.exit("✗ Usage: python3 publish_draft.py --delete <slug>")
        deleted, _ = Article.objects.filter(slug=args[1]).delete()
        print(f"  ✓ Deleted {deleted} object(s) for slug '{args[1]}'" if deleted else "  ⏭ Nothing to delete")
        return
    path = args[0]
    status = "published" if "--publish" in args else "draft"
    draft = load_draft(path)
    upsert_article(draft, status)


if __name__ == "__main__":
    main()
