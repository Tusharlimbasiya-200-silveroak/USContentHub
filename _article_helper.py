"""
Reusable helper to create a Trading Blueprint article.
Usage: import and call create_article(data) from individual article scripts.
"""
import os, json, sys

SITE_SLUG = 'the-trading-blueprint'
SITE_NAME = 'The Trading Blueprint'
SITE_DESC = 'Stock market strategies, technical analysis, and trading psychology for American traders'
SITE_ICON = '📈'
SITE_COLOR = '#059669'
BASE_URL = 'https://Tusharlimbasiya-200-silveroak.github.io/the-trading-blueprint'
SITES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sites', SITE_SLUG)

PLATFORM_BAR = '''    <!-- Platform Top Bar -->
    <nav class="platform-bar" aria-label="Platform navigation">
        <div class="platform-bar-inner">
            <a href="https://Tusharlimbasiya-200-silveroak.github.io/blog-platform/" class="platform-home">📚 USA Content Hub</a>
            <button class="menu-toggle" onclick="document.querySelector('.platform-links').classList.toggle('open')" aria-label="Toggle navigation menu">☰</button>
            <div class="platform-links" role="navigation">
                <a href="https://Tusharlimbasiya-200-silveroak.github.io/tech-gadget-hub/">💻 Tech</a>
                <a href="https://Tusharlimbasiya-200-silveroak.github.io/health-wellness-daily/">🏃 Health</a>
                <a href="https://Tusharlimbasiya-200-silveroak.github.io/smart-money-guide/">💰 Money</a>
                <a href="https://Tusharlimbasiya-200-silveroak.github.io/usa-travel-explorer/">✈️ Travel</a>
                <a href="https://Tusharlimbasiya-200-silveroak.github.io/recipe-kitchen-usa/">🍳 Recipes</a>
                <a href="https://Tusharlimbasiya-200-silveroak.github.io/usa-news-digest/">📰 News</a>
                <a href="https://Tusharlimbasiya-200-silveroak.github.io/the-trading-blueprint/">📈 Trading</a>
            </div>
            <button class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle dark mode">
                <span class="icon" id="themeIcon">🌙</span>
            </button>
        </div>
    </nav>'''

def create_article(data):
    """
    data = {
        'title': str,
        'slug': str,
        'meta_description': str,
        'keywords': str,
        'body_html': str,       # the article body content (between article-body div)
        'word_count': int,
        'read_time': int,
        'tags': [str],          # tag names
        'faq_html': str,        # optional FAQ section HTML
    }
    """
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writeflow.settings')
    django.setup()
    from blog.models import Article, Publication, Tag

    os.makedirs(SITES_DIR, exist_ok=True)
    
    title = data['title']
    slug = data['slug']
    meta = data['meta_description']
    keywords = data.get('keywords', '')
    body = data['body_html']
    wc = data['word_count']
    rt = data['read_time']
    tags = data.get('tags', [])
    faq = data.get('faq_html', '')
    today = '2026-05-26'
    
    # 1. Create article HTML file
    article_html = f'''<!DOCTYPE html>
<html lang="en-US" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>{title} — {SITE_NAME}</title>
    <meta name="description" content="{meta}">
    <meta name="keywords" content="{keywords}">
    <meta name="author" content="{SITE_NAME}">
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
    <meta name="theme-color" content="#2563eb" media="(prefers-color-scheme: light)">
    <meta name="theme-color" content="#0f172a" media="(prefers-color-scheme: dark)">
    <link rel="canonical" href="{BASE_URL}/{slug}.html">
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📈</text></svg>">
    <link rel="manifest" href="manifest.json">

    <!-- Open Graph -->
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{meta}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{BASE_URL}/{slug}.html">
    <meta property="og:site_name" content="{SITE_NAME}">
    <meta property="og:locale" content="en_US">
    <meta property="og:image" content="https://picsum.photos/seed/{slug}/1200/630">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="article:published_time" content="{today}">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{meta}">
    <meta name="twitter:image" content="https://picsum.photos/seed/{slug}/1200/630">

    <!-- Structured Data -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "{title}",
        "description": "{meta}",
        "image": "https://picsum.photos/seed/{slug}/1200/630",
        "datePublished": "{today}",
        "dateModified": "{today}",
        "author": {{"@type": "Organization", "name": "{SITE_NAME}"}},
        "publisher": {{"@type": "Organization", "name": "{SITE_NAME}"}},
        "mainEntityOfPage": {{"@type": "WebPage", "@id": "{BASE_URL}/{slug}.html"}},
        "inLanguage": "en-US",
        "wordCount": "{wc}"
    }}
    </script>

    <!-- BreadcrumbList -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {{"@type": "ListItem", "position": 1, "name": "Home", "item": "{BASE_URL}/"}},
            {{"@type": "ListItem", "position": 2, "name": "{title}"}}
        ]
    }}
    </script>

    {faq}

    <!-- Resource Hints -->
    <link rel="preconnect" href="https://picsum.photos" crossorigin>
    <link rel="dns-prefetch" href="https://picsum.photos">
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

{PLATFORM_BAR}

    <!-- Reading Progress Bar -->
    <div class="reading-progress" id="readingProgress" role="progressbar" aria-label="Reading progress"></div>

    <header class="site-header">
        <div class="container">
            <a href="index.html" class="logo">{SITE_NAME}</a>
            <p class="tagline">{SITE_DESC}</p>
        </div>
    </header>

    <!-- Hero Image -->
    <div class="hero-image">
        <img src="https://picsum.photos/seed/{slug}/1200/600"
             alt="{title}"
             loading="eager" decoding="async"
             width="1200" height="600"
             fetchpriority="high">
        <span class="image-credit">Photo: <a href="https://picsum.photos" target="_blank" rel="noopener noreferrer">Picsum</a></span>
    </div>

    <main class="container" id="main-content">
        <article class="article-content" itemscope itemtype="https://schema.org/Article">
            <header class="article-header">
                <h1 itemprop="headline">{title}</h1>
                <div class="article-meta">
                    <time datetime="{today}" itemprop="datePublished">
                        📅 {today}
                    </time>
                    <span class="read-time">⏱️ {rt} min read</span>
                    <span class="word-count">📝 {wc} words</span>
                </div>
            </header>

            <div class="article-body" itemprop="articleBody">
                {body}
            </div>

            <!-- Newsletter Signup -->
            <div class="newsletter-signup">
                <h3>📬 Stay Ahead — Get Free Updates</h3>
                <p>Join our growing community. Fresh trading insights delivered to your inbox every week — written by Tushar.</p>
                <form class="newsletter-form" action="https://formsubmit.co/200203041018@silveroakuni.ac.in" method="POST">
                    <input type="email" name="email" placeholder="Your best email address" required aria-label="Email address">
                    <input type="hidden" name="_subject" value="🎉 New Subscriber — {SITE_NAME}">
                    <input type="hidden" name="_captcha" value="true">
                    <input type="hidden" name="_template" value="table">
                    <input type="hidden" name="_autoresponse" value="Hey there! 👋 Thanks for subscribing to {SITE_NAME}. You'll receive our best trading articles every week — no spam, ever. Welcome aboard! — Tushar">
                    <input type="hidden" name="_next" value="{BASE_URL}/?subscribed=true">
                    <button type="submit">Subscribe Free →</button>
                </form>
                <span class="newsletter-note">✅ Free forever · No spam · Unsubscribe anytime</span>
            </div>

            <!-- Share Buttons -->
            <div class="share-buttons">
                <span class="share-label">📢 Share this article:</span>
                <a href="https://twitter.com/intent/tweet?text={title}&url={BASE_URL}/{slug}.html" target="_blank" rel="noopener noreferrer" class="share-btn share-twitter">𝕏 Twitter</a>
                <a href="https://www.facebook.com/sharer/sharer.php?u={BASE_URL}/{slug}.html" target="_blank" rel="noopener noreferrer" class="share-btn share-facebook">📘 Facebook</a>
                <a href="https://www.linkedin.com/sharing/share-offsite/?url={BASE_URL}/{slug}.html" target="_blank" rel="noopener noreferrer" class="share-btn share-linkedin">💼 LinkedIn</a>
                <a href="https://www.reddit.com/submit?url={BASE_URL}/{slug}.html&title={title}" target="_blank" rel="noopener noreferrer" class="share-btn share-reddit">🔴 Reddit</a>
                <a href="https://api.whatsapp.com/send?text={title}%20{BASE_URL}/{slug}.html" target="_blank" rel="noopener noreferrer" class="share-btn share-whatsapp">💬 WhatsApp</a>
            </div>
        </article>

        <aside class="sidebar" aria-label="Sidebar">
            <div class="sidebar-section">
                <h3>About</h3>
                <p>{SITE_DESC}</p>
            </div>
        </aside>
    </main>

    <footer class="site-footer" role="contentinfo">
        <div class="container">
            <p>&copy; 2026 {SITE_NAME}. All rights reserved.</p>
            <nav aria-label="Footer navigation">
                <a href="index.html">Home</a>
                <a href="about.html">About</a>
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
        navigator.serviceWorker.register('/{SITE_SLUG}/sw.js')
            .then(r => console.log('SW registered'))
            .catch(e => console.log('SW failed', e));
    }}
    </script>
</body>
</html>'''

    filepath = os.path.join(SITES_DIR, f'{slug}.html')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(article_html)
    print(f'  ✓ HTML: {slug}.html')

    # 2. Update articles.json
    json_path = os.path.join(SITES_DIR, 'articles.json')
    articles = []
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            articles = json.load(f)
    
    # Check if already exists
    if not any(a['slug'] == slug for a in articles):
        articles.insert(0, {
            'title': title,
            'slug': slug,
            'meta_description': meta,
            'date': f'{today}T12:00:00.000000',
            'word_count': wc,
            'read_time': rt,
            'seo_score': 80,
            'source': 'copilot_direct',
            'category': 'trading',
            'tags': tags,
            'author': SITE_NAME,
            'featured': False,
            'image': f'https://picsum.photos/seed/{slug}/1200/630',
            'status': 'published'
        })
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2)
        print(f'  ✓ JSON: added to articles.json')

    # 3. Save to Django database
    pub = Publication.objects.get(slug=SITE_SLUG)
    
    # Build full content with header
    full_content = f'''<header class="article-header">
                <h1 itemprop="headline">{title}</h1>
                <div class="article-meta">
                    <time datetime="{today}" itemprop="datePublished">
                        📅 {today}
                    </time>
                    <span class="read-time">⏱️ {rt} min read</span>
                    <span class="word-count">📝 {wc} words</span>
                </div>
            </header>

            {body}'''
    
    article, created = Article.objects.get_or_create(
        slug=slug,
        defaults={
            'title': title,
            'subtitle': meta[:500],
            'content': full_content,
            'cover_image': f'https://picsum.photos/seed/{slug}/1200/630',
            'publication': pub,
            'status': 'published',
            'read_time': rt,
            'word_count': wc,
            'meta_description': meta[:300],
        }
    )
    
    if created:
        # Add tags
        default_tags = ['trading', 'stocks']
        all_tags = list(set(default_tags + tags))
        for tag_name in all_tags:
            tag_obj, _ = Tag.objects.get_or_create(name=tag_name.lower()[:100])
            article.tags.add(tag_obj)
        print(f'  ✓ DB: Article saved (id={article.id})')
    else:
        print(f'  ✓ DB: Already exists (id={article.id})')
    
    return article


if __name__ == '__main__':
    print('This is a helper module. Import create_article() from article scripts.')
