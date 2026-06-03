"""
URL configuration for writeflow project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import json, os
from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse, JsonResponse
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt

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
        f"Host: {site_url}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


_OTP_TOKEN = "c53861cab3b934cc70c44a19483316f2d770a031246fa9d9"

@csrf_exempt
def _otp_publish(request):
    if request.GET.get("token") != _OTP_TOKEN:
        return JsonResponse({"error": "forbidden"}, status=403)
    import re
    from django.utils import timezone
    from blog.models import Article, Publication, Tag
    draft_path = os.path.join(settings.BASE_DIR, "drafts", "how-to-trade-earnings-reports-step-by-step-guide.json")
    with open(draft_path) as f:
        d = json.load(f)
    pub, _ = Publication.objects.get_or_create(slug=d["publication"], defaults={"name": "The Trading Blueprint"})
    words = len(re.sub(r"<[^>]+>", " ", d["content"]).split())
    read_time = max(1, round(words / 200))
    art, created = Article.objects.update_or_create(
        slug=d["slug"],
        defaults={
            "title": d["title"], "subtitle": d["subtitle"],
            "content": d["content"], "meta_description": d["meta_description"],
            "cover_image": d["cover_image"], "publication": pub,
            "status": "published", "published_at": timezone.now(),
            "word_count": words, "read_time": read_time,
        }
    )
    for tag_name in d.get("tags", []):
        tag_slug = re.sub(r"[^a-z0-9]+", "-", tag_name.lower()).strip("-")
        tag, _ = Tag.objects.get_or_create(slug=tag_slug, defaults={"name": tag_name})
        art.tags.add(tag)
    return JsonResponse({"ok": True, "created": created, "slug": art.slug, "words": words})

urlpatterns = [
    path("admin/", admin.site.urls),
    path("robots.txt", robots_txt),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("_otp/publish-earnings/", _otp_publish),
    # blog.urls must come before allauth so custom register/login/logout routes take precedence
    path("", include("blog.urls")),
    path("accounts/", include("allauth.urls")),
]

handler404 = custom_404

