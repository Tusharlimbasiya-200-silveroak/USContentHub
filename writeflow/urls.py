"""URL configuration for writeflow project."""
from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import include, path

from blog.sitemaps import ArticleSitemap, PublicationSitemap, StaticSitemap, TagSitemap
from blog.views import custom_404

sitemaps = {
    "articles": ArticleSitemap,
    "publications": PublicationSitemap,
    "tags": TagSitemap,
    "static": StaticSitemap,
}


def robots_txt(request):
    site_url = getattr(settings, "SITE_URL", "http://localhost:8000").rstrip("/")
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "Disallow: /search/?q=",
        "Disallow: /api/",
        "",
        f"Sitemap: {site_url}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def ads_txt(request):
    """Authorized Digital Sellers file required by Google AdSense.

    The certification authority ID (f08c47fec0942fa0) is Google's constant for
    all AdSense publishers; the pub ID is this site's AdSense account.
    """
    pub_id = getattr(settings, "ADSENSE_PUBLISHER_ID", "pub-2673860903932624")
    line = f"google.com, {pub_id}, DIRECT, f08c47fec0942fa0"
    return HttpResponse(line + "\n", content_type="text/plain")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("robots.txt", robots_txt),
    path("ads.txt", ads_txt),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("", include("blog.urls")),
    path("accounts/", include("allauth.urls")),
]

handler404 = custom_404
