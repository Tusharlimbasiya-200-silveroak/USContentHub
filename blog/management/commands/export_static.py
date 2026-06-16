"""Render published Article rows from the database back into the static
``sites/<publication>/`` tree (article HTML + articles.json entry + homepage
card + sitemap URL).

This is the inverse of ``import_blogs`` and the foundation of the "DB is the
single source of truth, the static site is a generated artifact" architecture.

It is **per-article and idempotent**: it upserts each given slug across all
four surfaces without touching unrelated articles, so it never mass-rewrites
the live sites and never drops the extra ``articles.json`` fields (seo_score,
source, bucket, …) that the DB model does not store.

Usage:
    python manage.py export_static --slug fed-june-2026-rate-decision-traders-guide
    python manage.py export_static --publication the-trading-blueprint        # all published in pub
    python manage.py export_static --slug a --slug b --check                  # diff only, write nothing
"""
import html
import json
import os
import re
from urllib.parse import quote

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from blog.models import Article, Publication

GTAG_ID = "G-PJ50891X0J"
NEWSLETTER_EMAIL = "200203041018@silveroakuni.ac.in"
PAGES_BASE = "https://Tusharlimbasiya-200-silveroak.github.io"

PLATFORM_LINKS = [
    ("tech-gadget-hub", "💻 Tech"),
    ("health-wellness-daily", "🏃 Health"),
    ("smart-money-guide", "💰 Money"),
    ("usa-travel-explorer", "✈️ Travel"),
    ("recipe-kitchen-usa", "🍳 Recipes"),
    ("usa-news-digest", "📰 News"),
    ("the-trading-blueprint", "📈 Trading"),
]


def esc(s):
    """HTML-escape for text/attribute contexts (quotes included)."""
    return html.escape(s or "", quote=True)


def img_host(url):
    m = re.match(r"https?://([^/]+)/", url or "")
    return m.group(1) if m else "images.unsplash.com"


def card_html(article):
    """A single homepage `<article class="article-card">` block."""
    slug = article.slug
    date = article.published_at.strftime("%Y-%m-%d")
    return (
        '                <article class="article-card">\n'
        '                    <div class="card-image">\n'
        f'                        <img src="{esc(article.cover_image)}"\n'
        f'                             alt="{esc(article.title)}"\n'
        '                             loading="lazy" decoding="async"\n'
        '                             width="640" height="360">\n'
        '                    </div>\n'
        '                    <div class="card-body">\n'
        f'                        <h3><a href="{slug}.html">{esc(article.title)}</a></h3>\n'
        '                        <div class="article-meta">\n'
        f'                            <time datetime="{date}">📅 {date}</time>\n'
        f'                            <span class="read-time">⏱️ {article.read_time} min</span>\n'
        '                        </div>\n'
        f'                        <p class="article-excerpt">{esc(article.meta_description)}</p>\n'
        f'                        <a href="{slug}.html" class="read-more">Read More</a>\n'
        '                    </div>\n'
        '                </article>'
    )


def article_html(article, pub):
    """Full standalone article page, faithful to the existing site template."""
    slug = article.slug
    base = f"{PAGES_BASE}/{pub.slug}/"
    url = f"{base}{slug}.html"
    date = article.published_at.strftime("%Y-%m-%d")
    title = article.title
    desc = article.meta_description or article.subtitle
    keywords = ", ".join(t.name for t in article.tags.all())
    img = article.cover_image
    host = img_host(img)
    qtitle = quote(title)
    qurl = quote(url, safe="")

    return f"""<!DOCTYPE html>
<html lang="en-US" dir="ltr">
<head>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GTAG_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GTAG_ID}');
    </script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(desc)}">
    <meta name="keywords" content="{esc(keywords)}">
    <meta name="author" content="{esc(pub.name)}">
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
    <meta name="theme-color" content="{esc(pub.color)}" media="(prefers-color-scheme: light)">
    <meta name="theme-color" content="#0f172a" media="(prefers-color-scheme: dark)">
    <link rel="canonical" href="{url}">
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>{pub.icon}</text></svg>">
    <link rel="manifest" href="manifest.json">

    <!-- Open Graph -->
    <meta property="og:title" content="{esc(title)}">
    <meta property="og:description" content="{esc(desc)}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{url}">
    <meta property="og:site_name" content="{esc(pub.name)}">
    <meta property="og:locale" content="en_US">
    <meta property="og:image" content="{esc(img)}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="article:published_time" content="{date}">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{esc(title)}">
    <meta name="twitter:description" content="{esc(desc)}">
    <meta name="twitter:image" content="{esc(img)}">

    <!-- Structured Data -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": {json.dumps(title)},
        "description": {json.dumps(desc)},
        "image": {json.dumps(img)},
        "datePublished": "{date}",
        "dateModified": "{date}",
        "author": {{"@type": "Organization", "name": {json.dumps(pub.name)}}},
        "publisher": {{"@type": "Organization", "name": {json.dumps(pub.name)}}},
        "mainEntityOfPage": {{"@type": "WebPage", "@id": "{url}"}},
        "inLanguage": "en-US",
        "wordCount": "{article.word_count}"
    }}
    </script>

    <!-- BreadcrumbList -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {{"@type": "ListItem", "position": 1, "name": "Home", "item": "{base}"}},
            {{"@type": "ListItem", "position": 2, "name": {json.dumps(title)}}}
        ]
    }}
    </script>

    <!-- Resource Hints -->
    <link rel="preconnect" href="https://{host}" crossorigin>
    <link rel="dns-prefetch" href="https://{host}">
    <link rel="preconnect" href="https://fonts.googleapis.com" crossorigin>
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preload" href="style.css?v=1" as="style">
    <link rel="stylesheet" href="style.css?v=1">

    <script>
    (function(){{var t=localStorage.getItem('theme');if(t)document.documentElement.setAttribute('data-theme',t);}})();
    </script>
</head>
<body>
    <a href="#main-content" class="skip-link">Skip to content</a>

    <!-- Platform Top Bar -->
    <nav class="platform-bar" aria-label="Platform navigation">
        <div class="platform-bar-inner">
            <a href="{PAGES_BASE}/blog-platform/" class="platform-home">📚 USA Content Hub</a>
            <button class="menu-toggle" onclick="document.querySelector('.platform-links').classList.toggle('open')" aria-label="Toggle navigation menu">☰</button>
            <div class="platform-links" role="navigation">
{chr(10).join(f'                <a href="{PAGES_BASE}/{s}/">{label}</a>' for s, label in PLATFORM_LINKS)}
            </div>
            <button class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle dark mode">
                <span class="icon" id="themeIcon">🌙</span>
            </button>
        </div>
    </nav>

    <!-- Reading Progress Bar -->
    <div class="reading-progress" id="readingProgress" role="progressbar" aria-label="Reading progress"></div>

    <header class="site-header">
        <div class="container">
            <a href="index.html" class="logo">{esc(pub.name)}</a>
            <p class="tagline">{esc(pub.description)}</p>
        </div>
    </header>

    <!-- Hero Image -->
    <div class="hero-image">
        <img src="{esc(img)}"
             alt="{esc(title)}"
             loading="eager" decoding="async"
             width="1200" height="600"
             fetchpriority="high">
        <span class="image-credit">Photo: <a href="https://{host}" target="_blank" rel="noopener noreferrer">{host}</a></span>
    </div>

    <main class="container" id="main-content">
        <article class="article-content" itemscope itemtype="https://schema.org/Article">
                <nav class="breadcrumb" aria-label="Breadcrumb"><a href="index.html">Home</a><span class="sep">&rsaquo;</span><span class="current">{esc(title)}</span></nav>
            <header class="article-header">
                <h1 itemprop="headline">{esc(title)}</h1>
                <div class="article-meta">
                    <time datetime="{date}" itemprop="datePublished">
                        📅 {date}
                    </time>
                    <span class="read-time">⏱️ {article.read_time} min read</span>
                    <span class="word-count">📝 {article.word_count} words</span>
                </div>
            </header>

            <div class="article-body" itemprop="articleBody">
{article.content}
            </div>

            <!-- Newsletter Signup -->
            <div class="newsletter-signup">
                <h3>📬 Stay Ahead — Get Free Updates</h3>
                <p>Join our growing community. Fresh insights delivered to your inbox every week — written by Tushar.</p>
                <form class="newsletter-form" action="https://formsubmit.co/{NEWSLETTER_EMAIL}" method="POST">
                    <input type="email" name="email" placeholder="Your best email address" required aria-label="Email address">
                    <input type="hidden" name="_subject" value="🎉 New Subscriber — {esc(pub.name)}">
                    <input type="hidden" name="_captcha" value="true">
                    <input type="hidden" name="_template" value="table">
                    <input type="hidden" name="_autoresponse" value="Hey there! 👋 Thanks for subscribing to {esc(pub.name)}. You'll receive our best articles every week — no spam, ever. Welcome aboard! — Tushar">
                    <input type="hidden" name="_next" value="{base}?subscribed=true">
                    <button type="submit">Subscribe Free →</button>
                </form>
                <span class="newsletter-note">✅ Free forever · No spam · Unsubscribe anytime</span>
            </div>

            <!-- Share Buttons -->
            <div class="share-buttons">
                <span class="share-label">📢 Share this article:</span>
                <a href="https://twitter.com/intent/tweet?text={qtitle}&url={qurl}" target="_blank" rel="noopener noreferrer" class="share-btn share-twitter">𝕏 Twitter</a>
                <a href="https://www.facebook.com/sharer/sharer.php?u={qurl}" target="_blank" rel="noopener noreferrer" class="share-btn share-facebook">📘 Facebook</a>
                <a href="https://www.linkedin.com/sharing/share-offsite/?url={qurl}" target="_blank" rel="noopener noreferrer" class="share-btn share-linkedin">💼 LinkedIn</a>
                <a href="https://www.reddit.com/submit?url={qurl}&title={qtitle}" target="_blank" rel="noopener noreferrer" class="share-btn share-reddit">🔴 Reddit</a>
                <a href="https://api.whatsapp.com/send?text={qtitle}%20{qurl}" target="_blank" rel="noopener noreferrer" class="share-btn share-whatsapp">💬 WhatsApp</a>
            </div>
        <section class="related-articles" aria-label="Related articles"><h2>Read Next</h2><div class="related-grid" id="relatedGrid"></div></section>
        </article>

        <aside class="sidebar" aria-label="Sidebar">
            <div class="sidebar-section">
                <h3>About</h3>
                <p>{esc(pub.description)}</p>
            </div>
        </aside>
    </main>

    <footer class="site-footer" role="contentinfo">
        <div class="container">
            <p>&copy; 2026 {esc(pub.name)}. All rights reserved.</p>
            <nav aria-label="Footer navigation" data-enhanced="1">
                <a href="index.html">Home</a>
                <a href="about.html">About</a>
                <a href="contact.html">Contact</a>
                <a href="sitemap.xml">Sitemap</a>
            </nav>
        </div>
    </footer>

    <button class="back-to-top" id="backToTop" aria-label="Back to top">↑</button>

    <script>
    function toggleTheme(){{
        var h=document.documentElement;
        var c=h.getAttribute('data-theme');
        var n=(c==='dark')?'light':'dark';
        if(!c){{n=getComputedStyle(document.body).backgroundColor==='rgb(255, 255, 255)'?'dark':'light';}}
        h.setAttribute('data-theme',n);
        localStorage.setItem('theme',n);
        updateThemeIcon(n);
    }}
    function updateThemeIcon(t){{
        var i=document.getElementById('themeIcon');
        if(i) i.textContent=(t==='dark')?'☀️':'🌙';
    }}
    (function(){{
        var t=localStorage.getItem('theme');
        if(!t&&window.matchMedia('(prefers-color-scheme:dark)').matches) t='dark';
        updateThemeIcon(t||'light');
    }})();
    var ticking=false;
    window.addEventListener('scroll',function(){{
        if(!ticking){{
            requestAnimationFrame(function(){{
                var bar=document.getElementById('readingProgress');
                var btn=document.getElementById('backToTop');
                var s=window.scrollY;
                var d=document.documentElement.scrollHeight-window.innerHeight;
                if(d>0&&bar) bar.style.width=(s/d*100)+'%';
                if(btn){{if(s>400)btn.classList.add('visible');else btn.classList.remove('visible');}}
                ticking=false;
            }});
            ticking=true;
        }}
    }},{{passive:true}});
    document.getElementById('backToTop').addEventListener('click',function(){{
        window.scrollTo({{top:0,behavior:'smooth'}});
    }});
    </script>

    <script>
    if ('serviceWorker' in navigator) {{
        navigator.serviceWorker.register('/{pub.slug}/sw.js')
            .then(r => console.log('SW registered'))
            .catch(e => console.log('SW failed', e));
    }}
    </script>
<script>
/* related-articles v1 */
(function(){{
  var grid=document.getElementById('relatedGrid'); if(!grid) return;
  var cur=location.pathname.split('/').pop().replace(/\\.html$/,'');
  function esc(s){{return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}}
  fetch('articles.json').then(function(r){{return r.json();}}).then(function(d){{
    var idx=-1,i; for(i=0;i<d.length;i++){{if(d[i].slug===cur){{idx=i;break;}}}}
    var others=d.filter(function(a){{return a.slug!==cur;}});
    if(!others.length){{grid.parentElement.style.display='none';return;}}
    var start=(idx>0?idx:0)%others.length;
    var pick=others.slice(start).concat(others.slice(0,start)).slice(0,3);
    grid.innerHTML=pick.map(function(a){{
      return '<article class="r-card"><h3><a href="'+a.slug+'.html">'+esc(a.title)+'</a></h3>'
        +'<p class="r-excerpt">'+esc(a.meta_description||'')+'</p>'
        +'<a href="'+a.slug+'.html" class="read-more">Read More →</a></article>';
    }}).join('');
  }}).catch(function(){{grid.parentElement.style.display='none';}});
}})();
</script>
</body>
</html>
"""


def upsert_articles_json(path, article):
    """Insert/replace this article's entry, preserving every other entry and
    all extra fields (seo_score, source, bucket, …) the DB does not store."""
    data = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    entry = next((e for e in data if e.get("slug") == article.slug), None)
    fields = {
        "title": article.title,
        "slug": article.slug,
        "meta_description": article.meta_description,
        "date": article.published_at.strftime("%Y-%m-%dT%H:%M:%S.%f"),
        "word_count": article.word_count,
        "read_time": article.read_time,
        "category": article.publication.slug,
        "tags": [t.name for t in article.tags.all()],
        "author": article.publication.name,
        "image": article.cover_image,
        "status": article.status,
    }
    if entry is None:
        # New: default the export-only metadata, then prepend (newest first).
        entry = {"seo_score": 95, "source": "db_export", "featured": False, "bucket": "main", "seo_score_original": 90}
        entry.update(fields)
        data.insert(0, entry)
    else:
        entry.update(fields)  # keep its existing seo_score/source/bucket/featured
    return data


def upsert_index_card(html_text, article):
    """Remove any existing card for this slug, then insert a fresh card at the
    top of the grid. Returns updated html (everything else untouched)."""
    anchor = '<div class="articles-grid" id="articlesGrid">'
    if anchor not in html_text:
        return html_text, False
    # Drop an existing card that links to this slug (idempotent re-runs).
    pat = re.compile(
        r'\n\s*<article class="article-card">.*?<a href="' + re.escape(article.slug + ".html") + r'".*?</article>',
        re.DOTALL,
    )
    html_text = pat.sub("", html_text)
    insert_at = html_text.index(anchor) + len(anchor)
    html_text = html_text[:insert_at] + "\n\n" + card_html(article) + html_text[insert_at:]
    # Sync the published count to the number of cards now present.
    count = html_text.count('<article class="article-card">')
    html_text = re.sub(r'<p class="articles-count">\d+ articles published</p>',
                       f'<p class="articles-count">{count} articles published</p>', html_text)
    return html_text, True


def upsert_sitemap(xml_text, article, pub):
    loc = f"{PAGES_BASE}/{pub.slug}/{article.slug}.html"
    if loc in xml_text:
        return xml_text, False
    date = article.published_at.strftime("%Y-%m-%d")
    block = (f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{date}</lastmod>\n"
             f"    <changefreq>weekly</changefreq>\n    <priority>0.9</priority>\n  </url>\n")
    # Insert right after the homepage <url> block.
    m = re.search(r"(</url>\s*\n)", xml_text)
    if not m:
        return xml_text, False
    idx = m.end()
    return xml_text[:idx] + block + xml_text[idx:], True


class Command(BaseCommand):
    help = "Render published DB articles into the static sites/<pub>/ tree (article HTML + json + index card + sitemap)."

    def add_arguments(self, parser):
        parser.add_argument("--slug", action="append", default=[], help="Article slug(s) to export (repeatable).")
        parser.add_argument("--publication", help="Export every published article in this publication slug.")
        parser.add_argument("--check", action="store_true", help="Report what would change; write nothing.")

    def handle(self, *args, **opts):
        qs = Article.objects.filter(status="published").select_related("publication").prefetch_related("tags")
        if opts["publication"]:
            qs = qs.filter(publication__slug=opts["publication"])
        if opts["slug"]:
            qs = qs.filter(slug__in=opts["slug"])
        if not opts["publication"] and not opts["slug"]:
            raise CommandError("Specify --slug <slug> (repeatable) and/or --publication <slug>.")

        articles = list(qs)
        if not articles:
            raise CommandError("No matching published articles found.")

        sites_dir = os.path.abspath(os.path.join(settings.BASE_DIR, "sites"))
        check = opts["check"]
        touched_pubs = {}

        for article in articles:
            pub = article.publication
            if not pub:
                self.stdout.write(self.style.WARNING(f"  skip {article.slug}: no publication"))
                continue
            site_path = os.path.join(sites_dir, pub.slug)
            if not os.path.isdir(site_path):
                self.stdout.write(self.style.WARNING(f"  skip {article.slug}: {site_path} missing"))
                continue

            html_path = os.path.join(site_path, f"{article.slug}.html")
            new_html = article_html(article, pub)
            changed = not (os.path.exists(html_path) and open(html_path, encoding="utf-8").read() == new_html)
            if check:
                self.stdout.write(f"  [check] {pub.slug}/{article.slug}.html {'WOULD CHANGE' if changed else 'ok'}")
            else:
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(new_html)
                self.stdout.write(self.style.SUCCESS(f"  wrote {pub.slug}/{article.slug}.html"))
            touched_pubs.setdefault(pub.slug, (site_path, []))[1].append(article)

        # Per-publication surfaces: articles.json, index.html, sitemap.xml
        for pub_slug, (site_path, arts) in touched_pubs.items():
            jpath = os.path.join(site_path, "articles.json")
            ipath = os.path.join(site_path, "index.html")
            spath = os.path.join(site_path, "sitemap.xml")
            jdata = None
            itext = open(ipath, encoding="utf-8").read() if os.path.exists(ipath) else None
            stext = open(spath, encoding="utf-8").read() if os.path.exists(spath) else None
            for article in arts:
                jdata = upsert_articles_json(jpath, article) if jdata is None else _merge_json(jdata, article)
                if itext is not None:
                    itext, _ = upsert_index_card(itext, article)
                if stext is not None:
                    stext, _ = upsert_sitemap(stext, article, pub)
            if check:
                self.stdout.write(f"  [check] {pub_slug}: articles.json/index.html/sitemap.xml would be updated")
                continue
            with open(jpath, "w", encoding="utf-8") as f:
                json.dump(jdata, f, indent=2, ensure_ascii=False)
                f.write("\n")
            if itext is not None:
                open(ipath, "w", encoding="utf-8").write(itext)
            if stext is not None:
                open(spath, "w", encoding="utf-8").write(stext)
            self.stdout.write(self.style.SUCCESS(f"  updated {pub_slug}: articles.json, index.html, sitemap.xml"))

        self.stdout.write(self.style.SUCCESS(f"\nExported {len(articles)} article(s) across {len(touched_pubs)} publication(s)."))


def _merge_json(data, article):
    """Apply a second/Nth article's upsert onto an in-memory json list."""
    entry = next((e for e in data if e.get("slug") == article.slug), None)
    fields = {
        "title": article.title, "slug": article.slug, "meta_description": article.meta_description,
        "date": article.published_at.strftime("%Y-%m-%dT%H:%M:%S.%f"), "word_count": article.word_count,
        "read_time": article.read_time, "category": article.publication.slug,
        "tags": [t.name for t in article.tags.all()], "author": article.publication.name,
        "image": article.cover_image, "status": article.status,
    }
    if entry is None:
        entry = {"seo_score": 95, "source": "db_export", "featured": False, "bucket": "main", "seo_score_original": 90}
        entry.update(fields)
        data.insert(0, entry)
    else:
        entry.update(fields)
    return data
