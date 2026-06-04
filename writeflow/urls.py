"""URL configuration for writeflow project."""
from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import include, path

from blog.sitemaps import ArticleSitemap, PublicationSitemap, StaticSitemap, TagSitemap
from blog.views import custom_404

# ── OTP: bulk cover-image update for all 49 Trading Blueprint articles ────────
_IMG_TOKEN = "img_fix_tb_2026_zQ7"
_IMG_MAP = {
    "commodity-trading-gold-oil-agricultural-markets-2026": "https://images.unsplash.com/photo-1610375461246-83df859d849d?w=1200",
    "fear-greed-psychology-financial-markets-2026": "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=1200",
    "warren-buffett-value-investing-philosophy-guide-2026": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=1200",
    "tax-efficient-investing-guide-2026": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1200",
    "hedge-fund-strategies-explained-2026": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200",
    "retirement-portfolio-building-guide-2026": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=1200",
    "compound-interest-long-term-investing-guide-2026": "https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?w=1200",
    "currency-risk-international-investing-guide-2026": "https://images.unsplash.com/photo-1580519542036-c47de6196ba5?w=1200",
    "emerging-markets-investing-guide-2026": "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=1200",
    "global-macro-investing-top-down-guide-2026": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200",
    "quantitative-investing-data-driven-strategies-2026": "https://images.unsplash.com/photo-1509228627152-72ae9ae6848d?w=1200",
    "high-frequency-trading-algorithms-explained-2026": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1200",
    "esg-investing-guide-2026": "https://images.unsplash.com/photo-1466611653911-95081537e5b7?w=1200",
    "options-greeks-delta-gamma-theta-vega-guide-2026": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=1200",
    "efficient-market-hypothesis-explained-2026": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1200",
    "ipo-investing-guide-evaluate-new-listings-2026": "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=1200",
    "margin-trading-risks-rewards-guide-2026": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=1200",
    "index-funds-passive-investing-guide-2026": "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=1200",
    "bond-yields-interest-rates-investor-guide-2026": "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=1200",
    "portfolio-diversification-asset-allocation-guide-2026": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200",
    "etfs-vs-mutual-funds-complete-guide-2026": "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=1200",
    "pe-ratio-stock-valuation-metrics-guide-2026": "https://images.unsplash.com/photo-1460472178825-e5240623afd5?w=1200",
    "dollar-cost-averaging-strategy-guide-2026": "https://images.unsplash.com/photo-1565372195458-9de0b320ef04?w=1200",
    "best-semiconductor-stocks-to-buy-2026": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200",
    "sp500-mid-2026-outlook-key-levels-trader-guide": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200",
    "bitcoin-below-70k-2026-buy-the-dip-or-wait": "https://images.unsplash.com/photo-1518546305927-5a555bb7020d?w=1200",
    "energy-stocks-2026-oil-gas-trading-guide": "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=1200",
    "biotech-stocks-trading-guide-fda-pdufa-2026": "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=1200",
    "financial-statements-stock-trading-guide-2026": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1200",
    "sector-rotation-strategy-business-cycle-guide-2026": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200",
    "value-vs-growth-investing-strategy-guide-2026": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=1200",
    "dividend-investing-portfolio-guide-2026": "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=1200",
    "reit-real-estate-investment-trusts-guide-2026": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200",
    "forex-trading-beginners-guide-currency-markets-2026": "https://images.unsplash.com/photo-1580519542036-c47de6196ba5?w=1200",
    "position-trading-strategy-guide-2026": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=1200",
    "swing-trading-strategies-2026-step-by-step-playbook": "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=1200",
    "options-trading-beginners-complete-guide-2026": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=1200",
    "how-to-short-a-stock-short-selling-guide": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=1200",
    "pattern-day-trader-rule-explained-2026": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200",
    "stock-screening-guide-find-best-setups-2026": "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=1200",
    "trading-psychology-mental-edge-guide-2026": "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=1200",
    "how-to-build-a-trading-plan-2026": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1200",
    "volume-analysis-trading-obv-volume-profile-guide-2026": "https://images.unsplash.com/photo-1460472178825-e5240623afd5?w=1200",
    "bollinger-bands-strategy-complete-guide-2026": "https://images.unsplash.com/photo-1565372195458-9de0b320ef04?w=1200",
    "fibonacci-retracements-extensions-trading-guide-2026": "https://images.unsplash.com/photo-1509228627152-72ae9ae6848d?w=1200",
    "support-resistance-complete-technical-analysis-guide-2026": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1200",
    "rsi-macd-explained-technical-indicators-trading-guide": "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=1200",
    "moving-averages-trading-strategy-guide-2026": "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=1200",
    "candlestick-patterns-complete-traders-guide-2026": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200",
}


def _otp_img(request):
    from blog.models import Article
    if request.GET.get("token") != _IMG_TOKEN:
        return HttpResponse("forbidden", status=403)
    updated = 0
    skipped = 0
    for slug, url in _IMG_MAP.items():
        n = Article.objects.filter(slug=slug).update(cover_image=url)
        if n:
            updated += n
        else:
            skipped += 1
    return HttpResponse(f"updated={updated} skipped={skipped}", status=200)
# ─────────────────────────────────────────────────────────────────────────────

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


urlpatterns = [
    path("admin/", admin.site.urls),
    path("robots.txt", robots_txt),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("_otp_img/update/", _otp_img),
    path("", include("blog.urls")),
    path("accounts/", include("allauth.urls")),
]

handler404 = custom_404
