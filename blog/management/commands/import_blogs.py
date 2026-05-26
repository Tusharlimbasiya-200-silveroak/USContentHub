"""Import existing blog articles from sites/ into Django database."""
import json
import os
import re
from html.parser import HTMLParser

from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify

from blog.models import Article, Publication, Tag


SITES = [
    {"folder": "tech-gadget-hub", "name": "Tech Gadget Hub", "icon": "💻",
     "desc": "Latest tech reviews, gadget guides, and digital trends for Americans",
     "color": "#2563eb", "tags": ["technology", "gadgets", "ai", "apps"]},
    {"folder": "health-wellness-daily", "name": "Health Wellness Daily", "icon": "🏃",
     "desc": "Health tips, wellness guides, and fitness advice for everyday Americans",
     "color": "#10b981", "tags": ["health", "wellness", "fitness", "nutrition"]},
    {"folder": "smart-money-guide", "name": "Smart Money Guide", "icon": "💰",
     "desc": "Personal finance tips, budgeting, investing, and money-saving strategies",
     "color": "#f59e0b", "tags": ["finance", "budgeting", "investing", "savings"]},
    {"folder": "usa-travel-explorer", "name": "USA Travel Explorer", "icon": "✈️",
     "desc": "Travel destinations, road trips, and vacation planning across America",
     "color": "#8b5cf6", "tags": ["travel", "road-trips", "national-parks", "vacation"]},
    {"folder": "recipe-kitchen-usa", "name": "Recipe Kitchen USA", "icon": "🍳",
     "desc": "Easy recipes, meal prep ideas, and food trends popular in America",
     "color": "#ef4444", "tags": ["recipes", "cooking", "meal-prep", "food"]},
    {"folder": "usa-news-digest", "name": "USA News Digest", "icon": "📰",
     "desc": "Breaking down US news, trends, and issues that matter to Americans",
     "color": "#6366f1", "tags": ["news", "politics", "economy", "trends"]},
]


class BodyExtractor(HTMLParser):
    """Extract article body content from HTML."""
    def __init__(self):
        super().__init__()
        self.in_body = False
        self.depth = 0
        self.body_html = ""

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        cls = d.get("class", "")
        if "article-body" in cls or "article-content" in cls:
            self.in_body = True
            self.depth = 1
            return
        if self.in_body:
            self.depth += 1
            attr_str = " ".join(f'{k}="{v}"' for k, v in attrs)
            self.body_html += f"<{tag} {attr_str}>" if attr_str else f"<{tag}>"

    def handle_endtag(self, tag):
        if self.in_body:
            self.depth -= 1
            if self.depth <= 0:
                self.in_body = False
            else:
                self.body_html += f"</{tag}>"

    def handle_data(self, data):
        if self.in_body:
            self.body_html += data

    def handle_entityref(self, name):
        if self.in_body:
            self.body_html += f"&{name};"


class Command(BaseCommand):
    help = "Import blog articles from sites/ folder into Django database"

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Clear all existing data before import")

    def handle(self, *args, **options):
        from django.conf import settings
        sites_dir = os.path.join(settings.BASE_DIR, "sites")
        sites_dir = os.path.abspath(sites_dir)

        if options["clear"]:
            Article.objects.all().delete()
            Publication.objects.all().delete()
            Tag.objects.all().delete()
            self.stdout.write("Cleared existing data.")

        total = 0
        for site_cfg in SITES:
            folder = site_cfg["folder"]
            site_path = os.path.join(sites_dir, folder)
            json_path = os.path.join(site_path, "articles.json")

            if not os.path.exists(json_path):
                self.stdout.write(self.style.WARNING(f"  Skipping {folder}: no articles.json"))
                continue

            pub, _ = Publication.objects.get_or_create(
                slug=folder,
                defaults={
                    "name": site_cfg["name"],
                    "description": site_cfg["desc"],
                    "color": site_cfg["color"],
                    "icon": site_cfg["icon"],
                    "github_url": f"https://tusharlimbasiya-200-silveroak.github.io/{folder}/",
                },
            )

            # Create default tags
            tag_objects = []
            for tag_name in site_cfg["tags"]:
                tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                tag_objects.append(tag_obj)

            with open(json_path, "r", encoding="utf-8") as f:
                articles_data = json.load(f)

            imported = 0
            for item in articles_data:
                slug = item.get("slug", "")
                if not slug:
                    continue

                if Article.objects.filter(slug=slug).exists():
                    continue

                html_file = os.path.join(site_path, f"{slug}.html")
                body = ""
                if os.path.exists(html_file):
                    with open(html_file, "r", encoding="utf-8", errors="replace") as f:
                        html = f.read()
                    parser = BodyExtractor()
                    parser.feed(html)
                    body = parser.body_html.strip()

                if not body:
                    body = f"<p>{item.get('meta_description', item.get('title', ''))}</p>"

                date_str = item.get("date", "")
                pub_date = None
                if date_str:
                    pub_date = parse_datetime(date_str)
                    if not pub_date:
                        try:
                            from datetime import datetime
                            pub_date = datetime.fromisoformat(date_str[:10])
                        except (ValueError, TypeError):
                            pass

                article = Article(
                    title=item.get("title", slug),
                    slug=slug,
                    subtitle=item.get("meta_description", "")[:500],
                    content=body,
                    cover_image=item.get("image", f"https://picsum.photos/seed/{slug}/1200/630"),
                    publication=pub,
                    status="published",
                    read_time=item.get("read_time", 3),
                    word_count=item.get("word_count", 0),
                    meta_description=item.get("meta_description", "")[:300],
                )
                if pub_date:
                    from django.utils.timezone import make_aware, is_naive
                    if is_naive(pub_date):
                        pub_date = make_aware(pub_date)
                    article.published_at = pub_date
                article.save()

                # Add tags
                article.tags.set(tag_objects)

                # Add article-specific tags from data
                for tag_name in item.get("tags", []):
                    if tag_name:
                        tag_obj, _ = Tag.objects.get_or_create(name=tag_name.lower()[:100])
                        article.tags.add(tag_obj)

                imported += 1

            total += imported
            self.stdout.write(self.style.SUCCESS(f"  {folder}: {imported} articles imported"))

        self.stdout.write(self.style.SUCCESS(f"\nTotal: {total} articles imported across {len(SITES)} publications"))
