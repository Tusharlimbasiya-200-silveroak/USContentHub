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


# ONE-TIME PUBLISH ENDPOINT — remove after use
_PUBLISH_TOKEN = "PwS9RTTrdbQ8DbBKSUTPNNZ2BuFRnCvq"

def _one_time_publish(request):
    """Temporary endpoint: publishes the Microsoft Build 2026 draft to the production DB."""
    import json, re
    from django.utils import timezone
    from blog.models import Article, Publication, Tag
    from django.db import connection

    if request.GET.get("token") != _PUBLISH_TOKEN:
        return HttpResponse("forbidden", status=403)

    draft = {
        "publication": "tech-pulse",
        "title": "Microsoft Build 2026 Starts Today: AI Agents, New MAI Models, and What Developers Need to Know",
        "subtitle": "Satya Nadella takes the stage in San Francisco at 9:30 AM PT as Microsoft bets its biggest developer event of the year almost entirely on agentic AI",
        "slug": "microsoft-build-2026-developers-guide",
        "cover_image": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1200",
        "tags": ["microsoft build 2026", "ai agents", "developer tools", "copilot", "windows 11", "mai models", "tech conferences", "agentic ai"],
        "meta_description": "Microsoft Build 2026 kicks off June 2 in San Francisco. Here's the full developer guide: keynote times, expected MAI-Thinking-1 reasoning model, Copilot super app, Windows 11 developer mode, and how to watch.",
        "content": "<p>Microsoft Build 2026 kicks off today, June 2, in San Francisco \u2014 and if the session catalogue is any indication, this is shaping up to be the most AI-concentrated edition of Microsoft\u2019s developer conference yet. CEO Satya Nadella delivers the opening keynote at 9:30 AM PT, with the event running through June 3.</p><p>For developers, this year\u2019s Build matters more than most. Microsoft is expected to move beyond AI assistants that merely answer questions and put its full weight behind <strong>agentic AI</strong> \u2014 systems that act autonomously on a user\u2019s behalf across apps, running in the background for extended periods without supervision. Here\u2019s everything you need to know before the keynote.</p><h2>When and How to Watch</h2><p>Build 2026 runs <strong>June 2\u20133</strong> in San Francisco, with the headline moments streamed free:</p><ul><li><strong>Opening keynote:</strong> Tuesday, June 2 at 9:30 AM PT (12:30 PM ET / 10:00 PM IST), led by Satya Nadella</li><li><strong>Streaming:</strong> Microsoft\u2019s Build site and YouTube channel carry the keynotes and technical sessions live, with recordings available afterward</li><li><strong>Day 2:</strong> deeper technical sessions aimed squarely at working developers</li></ul><h2>MAI-Thinking-1: Microsoft\u2019s First Dedicated Reasoning Model</h2><p>The most anticipated announcement is expected from Microsoft AI chief <strong>Mustafa Suleyman</strong>: <strong>MAI-Thinking-1</strong>, the company\u2019s first dedicated reasoning model built in-house. Until now, Microsoft has leaned heavily on OpenAI\u2019s models to power Copilot while quietly building its own MAI family. A first-party reasoning model would mark a significant step toward independence \u2014 and give developers a new option in the Azure AI catalogue.</p><p>Reporting ahead of the event also points to <strong>MAI-Image-2.5</strong> and a faster <strong>MAI-Image-2.5-Flash</strong> joining the lineup, extending Microsoft\u2019s first-party image generation models.</p><h2>Copilot Is Becoming a \u2018Super App\u2019</h2><p>Microsoft is expected to push Copilot further toward an everything-app: one surface where chat, agents, search, and task automation converge across Windows, Office, and the web. The strategic logic is clear \u2014 whoever owns the surface where agents are launched owns the workflow. Expect new Copilot extensibility announcements aimed at developers who want their tools and services reachable from inside that surface.</p><h2>A Developer Mode for Windows 11</h2><p>One of the more practical rumors: a <strong>developer-optimized mode for Windows 11</strong> \u2014 described in pre-event reporting as a distraction-free setup that ships with the tools and configurations developers actually want, pre-loaded. If it materializes, it would be Microsoft\u2019s most direct answer yet to the long-standing complaint that setting up a fresh Windows machine for development takes half a day.</p><h2>The Hardware Context: NVIDIA\u2019s RTX Spark</h2><p>Build lands just days after NVIDIA unveiled its <strong>RTX Spark Superchip</strong> at Computex \u2014 a move beyond discrete GPUs into full AI-PC silicon for laptops and mini-PCs, combining Blackwell-generation RTX graphics with Grace CPU technology. Expect Microsoft to lean on that momentum: Windows 11\u2019s AI features increasingly assume capable NPU/GPU silicon underneath, and the Copilot+ PC story only works if the hardware keeps pace.</p><h2>Why This Build Matters: The Agentic Shift Is Real</h2><p>Build 2026 caps a frantic month for AI. May 2026 saw <strong>Google announce Gemini 3.5 at I/O</strong> on May 19 (with Gemini 3.5 Flash shipping the same day), <strong>OpenAI make GPT-5.5 Instant the ChatGPT default</strong> in early May, and a wave of releases from xAI, Alibaba\u2019s Qwen team, and DeepSeek. The common thread across every major lab: agents designed to run unsupervised in the background, not chatbots waiting for a prompt.</p><p>Microsoft\u2019s entire Build session catalogue is reportedly built around that same idea. For developers, that means the questions worth asking this week are practical ones:</p><ul><li>How do you <strong>expose your app\u2019s functionality to agents</strong> (rather than just users)?</li><li>What do <strong>identity, permissions, and auditing</strong> look like when software acts on a person\u2019s behalf?</li><li>Which agent frameworks will Microsoft bless inside Azure AI Foundry \u2014 and which will quietly fade?</li></ul><h2>What This Means for Developers</h2><p>If you build on the Microsoft stack, watch the keynote \u2014 but watch the Day 2 sessions more closely. Conference keynotes sell visions; the technical sessions reveal what actually ships and when. Three things to track:</p><ul><li><strong>MAI model pricing and availability.</strong> A first-party Microsoft reasoning model is only interesting if it\u2019s competitively priced against OpenAI and Anthropic models on Azure.</li><li><strong>Agent tooling maturity.</strong> Demos of autonomous agents are easy; debugging, evals, and guardrails are what make them production-ready. Look for announcements on observability and testing.</li><li><strong>Windows as a developer platform.</strong> Between the rumored dev mode and deeper WSL/AI integration, Microsoft has a chance to win back developers who drifted to macOS and Linux.</li></ul><p>And mark your calendar: <strong>Apple\u2019s WWDC 2026 follows immediately on June 8\u201312</strong>, with its own AI announcements expected. By mid-June, the developer landscape for the rest of 2026 will look a lot clearer. This week is where it starts.</p>",
    }

    db_engine = connection.settings_dict["ENGINE"].rsplit(".", 1)[-1]
    db_name = str(connection.settings_dict.get("NAME", "?"))

    pub_defaults = {
        "name": "Tech Pulse",
        "description": "Developer-focused technology news: Python and language releases, AI/ML model updates, frameworks, tooling, and what's new across tech.",
        "color": "#7c3aed",
        "icon": "\U0001f9e0",
    }
    pub, _ = Publication.objects.get_or_create(slug="tech-pulse", defaults=pub_defaults)

    text = re.sub(r"<[^>]+>", " ", draft["content"])
    words = len(text.split())
    read_time = max(1, round(words / 200))

    article, created = Article.objects.update_or_create(
        slug=draft["slug"],
        defaults={
            "title": draft["title"],
            "subtitle": draft["subtitle"],
            "content": draft["content"],
            "cover_image": draft["cover_image"],
            "publication": pub,
            "status": "published",
            "read_time": read_time,
            "word_count": words,
            "meta_description": draft["meta_description"],
            "published_at": timezone.now(),
        },
    )
    for name in draft["tags"]:
        tag, _ = Tag.objects.get_or_create(name=name.strip().lower())
        article.tags.add(tag)

    verb = "Created" if created else "Updated"
    total = Article.objects.filter(status="published").count()
    return HttpResponse(
        f"{verb}: {article.title}\nslug: {article.slug}\ndb: {db_engine} / {db_name}\ntotal published: {total}",
        content_type="text/plain",
    )


urlpatterns += [path("_otp/publish/", _one_time_publish)]
