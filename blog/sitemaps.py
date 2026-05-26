from django.contrib.sitemaps import Sitemap

from .models import Article, Publication, Tag


class ArticleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Article.objects.filter(status="published")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f"/article/{obj.slug}/"


class PublicationSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.6

    def items(self):
        return Publication.objects.all()

    def location(self, obj):
        return f"/pub/{obj.slug}/"


class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ["home", "about", "contact", "privacy", "explore"]

    def location(self, item):
        urls = {
            "home": "/",
            "about": "/about/",
            "contact": "/contact/",
            "privacy": "/privacy/",
            "explore": "/explore/",
        }
        return urls[item]
