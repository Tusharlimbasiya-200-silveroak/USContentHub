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
        f"Host: {site_url}",
    ]
    # TEMP DIAGNOSTIC — remove after deploy debugging (2026-06-02)
    if request.GET.get("diag") == "1":
        import os as _os
        from django.db import connection as _conn
        from blog.models import Article as _A
        _db = str(_conn.settings_dict.get("NAME", "?"))
        try:
            _size = _os.path.getsize(_db)
        except OSError:
            _size = -1
        _latest = _A.objects.order_by("-published_at").values_list("slug", flat=True).first()
        lines += [
            "",
            f"# engine: {_conn.settings_dict['ENGINE'].rsplit('.', 1)[-1]}",
            f"# db: {_db} ({_size} bytes)",
            f"# articles: {_A.objects.filter(status='published').count()}",
            f"# latest: {_latest}",
            f"# cwd: {_os.getcwd()}",
        ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("robots.txt", robots_txt),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    # blog.urls must come before allauth so custom register/login/logout routes take precedence
    path("", include("blog.urls")),
    path("accounts/", include("allauth.urls")),
]

handler404 = custom_404
