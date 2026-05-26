"""Generate all site infrastructure files for The Trading Blueprint."""
import json, os

SITE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sites', 'the-trading-blueprint')
SITE_NAME = 'The Trading Blueprint'
SITE_DESC = 'Stock market strategies, technical analysis, and trading psychology for American traders'
BASE_URL = 'https://Tusharlimbasiya-200-silveroak.github.io/the-trading-blueprint'
SITE_SLUG = 'the-trading-blueprint'

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

THEME_SCRIPT = '''    <script>
    function toggleTheme(){
        var h=document.documentElement;
        var c=h.getAttribute('data-theme');
        var n=(c==='dark')?'light':'dark';
        if(!c){n=getComputedStyle(document.body).backgroundColor==='rgb(255, 255, 255)'?'dark':'light';}
        h.setAttribute('data-theme',n);
        localStorage.setItem('theme',n);
        updateThemeIcon(n);
    }
    function updateThemeIcon(t){
        var i=document.getElementById('themeIcon');
        if(i) i.textContent=(t==='dark')?'☀️':'🌙';
    }
    (function(){
        var t=localStorage.getItem('theme');
        if(!t&&window.matchMedia('(prefers-color-scheme:dark)').matches) t='dark';
        updateThemeIcon(t||'light');
    })();
    </script>'''

# Load articles
with open(os.path.join(SITE_DIR, 'articles.json'), 'r') as f:
    articles = json.load(f)

# ── 1. INDEX.HTML ──────────────────────────────────────────────────
print('Creating index.html...')

article_cards = ''
for i, art in enumerate(articles):
    loading = 'eager' if i < 3 else 'lazy'
    article_cards += f'''
                <article class="article-card">
                    <div class="card-image">
                        <img src="https://picsum.photos/seed/{art['slug']}/640/360"
                             alt="{art['title']}"
                             loading="{loading}" decoding="async"
                             width="640" height="360">
                    </div>
                    <div class="card-body">
                        <h3><a href="{art['slug']}.html">{art['title']}</a></h3>
                        <div class="article-meta">
                            <time datetime="{art['date'][:10]}">📅 {art['date'][:10]}</time>
                            <span class="read-time">⏱️ {art['read_time']} min</span>
                        </div>
                        <p class="article-excerpt">{art['meta_description'][:160]}</p>
                        <a href="{art['slug']}.html" class="read-more">Read More</a>
                    </div>
                </article>
'''

index_html = f'''<!DOCTYPE html>
<html lang="en-US" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>{SITE_NAME} - {SITE_DESC}</title>
    <meta name="description" content="{SITE_DESC}">
    <meta name="keywords" content="stock trading, technical analysis, trading strategies, forex, options, day trading, swing trading">
    <meta name="author" content="{SITE_NAME}">
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
    <meta name="theme-color" content="#2563eb" media="(prefers-color-scheme: light)">
    <meta name="theme-color" content="#0f172a" media="(prefers-color-scheme: dark)">
    <link rel="canonical" href="{BASE_URL}/">
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📈</text></svg>">
    <link rel="manifest" href="manifest.json">

    <link rel="preconnect" href="https://picsum.photos" crossorigin>
    <link rel="dns-prefetch" href="https://picsum.photos">
    <link rel="preconnect" href="https://fonts.googleapis.com" crossorigin>
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

    <meta property="og:title" content="{SITE_NAME}">
    <meta property="og:description" content="{SITE_DESC}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{BASE_URL}/">
    <meta property="og:site_name" content="{SITE_NAME}">
    <meta property="og:locale" content="en_US">
    <meta property="og:image" content="https://picsum.photos/seed/{SITE_SLUG}/1200/630">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">

    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{SITE_NAME}">
    <meta name="twitter:description" content="{SITE_DESC}">
    <meta name="twitter:image" content="https://picsum.photos/seed/{SITE_SLUG}/1200/630">

    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "{SITE_NAME}",
        "description": "{SITE_DESC}",
        "url": "{BASE_URL}/",
        "inLanguage": "en-US",
        "publisher": {{"@type": "Organization", "name": "{SITE_NAME}"}}
    }}
    </script>

    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "{SITE_NAME} - All Articles",
        "description": "{SITE_DESC}",
        "url": "{BASE_URL}/"
    }}
    </script>

    <link rel="preload" href="style.css?v=1" as="style">
    <link rel="stylesheet" href="style.css?v=1">

    <script>
    (function(){{var t=localStorage.getItem('theme');if(t)document.documentElement.setAttribute('data-theme',t);}})();
    </script>
</head>
<body>
    <a href="#main-content" class="skip-link">Skip to content</a>

{PLATFORM_BAR}

    <header class="site-header">
        <div class="container">
            <h1 class="logo">{SITE_NAME}</h1>
            <p class="tagline">{SITE_DESC}</p>
        </div>
    </header>

    <main class="container" id="main-content">
        <section class="articles-list" aria-label="Articles">
            <h2>Latest Articles</h2>
            <p class="articles-count">{len(articles)} articles published</p>
            
            <div class="articles-grid" id="articlesGrid">
                {article_cards}
            </div>
        </section>
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

{THEME_SCRIPT}

    <script>
    var ticking=false;
    window.addEventListener('scroll',function(){{
        if(!ticking){{
            requestAnimationFrame(function(){{
                var btn=document.getElementById('backToTop');
                if(btn){{if(window.scrollY>400)btn.classList.add('visible');else btn.classList.remove('visible');}}
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

with open(os.path.join(SITE_DIR, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(index_html)
print('  ✓ index.html')

# ── 2. ABOUT.HTML ──────────────────────────────────────────────────
print('Creating about.html...')
about_html = f'''<!DOCTYPE html>
<html lang="en-US" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>About {SITE_NAME} — USA Content Hub</title>
    <meta name="description" content="{SITE_DESC}">
    <meta name="robots" content="index, follow">
    <meta property="og:title" content="About {SITE_NAME}">
    <meta property="og:description" content="{SITE_DESC}">
    <meta property="og:type" content="website">
    <link rel="preconnect" href="https://picsum.photos" crossorigin>
    <link rel="dns-prefetch" href="https://picsum.photos">
    <link rel="preconnect" href="https://fonts.googleapis.com" crossorigin>
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="style.css">
    <script>(function(){{var t=localStorage.getItem('theme');if(t)document.documentElement.setAttribute('data-theme',t);}})();</script>
</head>
<body>
    <a href="#main-content" class="skip-link">Skip to content</a>

{PLATFORM_BAR}

    <main id="main-content" class="about-layout">
        <div class="about-container">
            <div class="about-header">
                <span class="about-icon">📈</span>
                <h1>{SITE_NAME}</h1>
                <p class="about-tagline">Your blueprint for smarter trading</p>
            </div>

            <section class="about-section">
                <h2>About this publication</h2>
                <p>{SITE_DESC}. We cover everything from stock market basics to advanced technical analysis, options strategies, forex trading, crypto markets, and the psychology that separates profitable traders from the rest.</p>
            </section>

            <section class="about-section">
                <h2>What we cover</h2>
                <p><strong>Niche:</strong> Trading & Market Analysis</p>
                <p><strong>Target Audience:</strong> US adults interested in active trading, from beginners to intermediate traders aged 20-50</p>
                <div class="about-tags">
                    <span class="tag-pill">trading</span>
                    <span class="tag-pill">stocks</span>
                    <span class="tag-pill">technical-analysis</span>
                    <span class="tag-pill">options</span>
                    <span class="tag-pill">forex</span>
                    <span class="tag-pill">crypto</span>
                    <span class="tag-pill">day-trading</span>
                    <span class="tag-pill">risk-management</span>
                </div>
            </section>

            <section class="about-section">
                <h2>Our approach</h2>
                <p>No hype. No "guaranteed returns." No trading guru nonsense. Just honest, research-backed trading education that focuses on risk management first, strategy second, and discipline always. Every article is written to help you make better decisions with your own money.</p>
            </section>

            <section class="about-section">
                <h2>Disclaimer</h2>
                <p>This publication is for educational purposes only. Nothing here constitutes financial advice. All trading involves risk. Past performance does not guarantee future results. Always do your own research and consider consulting a licensed financial advisor before making investment decisions.</p>
            </section>
        </div>
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

{THEME_SCRIPT}
</body>
</html>'''

with open(os.path.join(SITE_DIR, 'about.html'), 'w', encoding='utf-8') as f:
    f.write(about_html)
print('  ✓ about.html')

# ── 3. 404.HTML ────────────────────────────────────────────────────
print('Creating 404.html...')
error_html = f'''<!DOCTYPE html>
<html lang="en-US">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Page Not Found - {SITE_NAME}</title>
<link rel="stylesheet" href="style.css">
<style>
.error-page{{text-align:center;padding:80px 20px;max-width:600px;margin:0 auto}}
.error-code{{font-size:6rem;font-weight:800;color:var(--primary);line-height:1;margin-bottom:16px}}
.error-message{{font-size:1.25rem;color:var(--text-light);margin-bottom:32px}}
.error-link{{display:inline-block;padding:12px 32px;background:var(--primary);color:#fff;border-radius:var(--radius);text-decoration:none;font-weight:600}}
.error-link:hover{{background:var(--primary-dark)}}
</style>
    <script>(function(){{var t=localStorage.getItem("theme");if(t)document.documentElement.setAttribute("data-theme",t);}})();</script>
</head>
<body>
    <a href="#main-content" class="skip-link">Skip to content</a>
{PLATFORM_BAR}

<div class="error-page" id="main-content">
<div class="error-code">404</div>
<h1>Page Not Found</h1>
<p class="error-message">The page you are looking for does not exist or has been moved.</p>
<a href="/{SITE_SLUG}/" class="error-link">Back to Homepage</a>
</div>

{THEME_SCRIPT}
</body>
</html>'''

with open(os.path.join(SITE_DIR, '404.html'), 'w', encoding='utf-8') as f:
    f.write(error_html)
print('  ✓ 404.html')

# ── 4. ROBOTS.TXT ──────────────────────────────────────────────────
print('Creating robots.txt...')
robots = f'''User-agent: *
Allow: /

Sitemap: https://{SITE_SLUG}.github.io/sitemap.xml
'''
with open(os.path.join(SITE_DIR, 'robots.txt'), 'w') as f:
    f.write(robots)
print('  ✓ robots.txt')

# ── 5. SITEMAP.XML ─────────────────────────────────────────────────
print('Creating sitemap.xml...')
sitemap_entries = f'''  <url>
    <loc>{BASE_URL}/</loc>
    <lastmod>2026-05-26</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>{BASE_URL}/about.html</loc>
    <lastmod>2026-05-26</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>'''

for art in articles:
    sitemap_entries += f'''
  <url>
    <loc>{BASE_URL}/{art['slug']}.html</loc>
    <lastmod>{art['date'][:10]}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>'''

sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{sitemap_entries}
</urlset>'''

with open(os.path.join(SITE_DIR, 'sitemap.xml'), 'w', encoding='utf-8') as f:
    f.write(sitemap)
print('  ✓ sitemap.xml')

# ── 6. MANIFEST.JSON ──────────────────────────────────────────────
print('Creating manifest.json...')
manifest = {
    "name": SITE_NAME,
    "short_name": SITE_NAME,
    "start_url": "/",
    "display": "standalone",
    "background_color": "#ffffff",
    "theme_color": "#059669",
    "icons": [
        {
            "src": "https://picsum.photos/seed/" + SITE_SLUG + "/192/192",
            "sizes": "192x192",
            "type": "image/jpeg"
        },
        {
            "src": "https://picsum.photos/seed/" + SITE_SLUG + "/512/512",
            "sizes": "512x512",
            "type": "image/jpeg"
        }
    ]
}

with open(os.path.join(SITE_DIR, 'manifest.json'), 'w') as f:
    json.dump(manifest, f, indent=2)
print('  ✓ manifest.json')

# ── 7. SW.JS ──────────────────────────────────────────────────────
print('Creating sw.js...')
sw = f"""// Service Worker - Cache-first for static, network-first for HTML
const CACHE_NAME = '{SITE_SLUG}-v2026052612';
const STATIC_ASSETS = ['/', '/style.css', '/articles.json'];

self.addEventListener('install', e => {{
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
}});

self.addEventListener('activate', e => {{
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
}});

self.addEventListener('fetch', e => {{
  if (e.request.method !== 'GET') return;
  if (e.request.headers.get('accept') && e.request.headers.get('accept').includes('text/html')) {{
    e.respondWith(
      fetch(e.request).then(resp => {{
        const clone = resp.clone();
        caches.open(CACHE_NAME).then(c => c.put(e.request, clone));
        return resp;
      }}).catch(() => caches.match(e.request).then(r => r || caches.match('/')))
    );
    return;
  }}
  e.respondWith(
    caches.match(e.request).then(cached => {{
      if (cached) return cached;
      return fetch(e.request).then(resp => {{
        if (resp.ok) {{
          const clone = resp.clone();
          caches.open(CACHE_NAME).then(c => c.put(e.request, clone));
        }}
        return resp;
      }});
    }})
  );
}});
"""

with open(os.path.join(SITE_DIR, 'sw.js'), 'w') as f:
    f.write(sw)
print('  ✓ sw.js')

# ── 8. CONTACT.HTML ──────────────────────────────────────────────────
print('Creating contact.html...')
contact_html = f'''<!DOCTYPE html>
<html lang="en-US" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>Contact — {SITE_NAME}</title>
    <meta name="description" content="Get in touch with {SITE_NAME}">
    <meta name="robots" content="index, follow">
    <link rel="preconnect" href="https://fonts.googleapis.com" crossorigin>
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="style.css">
    <script>(function(){{var t=localStorage.getItem('theme');if(t)document.documentElement.setAttribute('data-theme',t);}})();</script>
</head>
<body>
    <a href="#main-content" class="skip-link">Skip to content</a>
{PLATFORM_BAR}

    <main id="main-content" class="about-layout">
        <div class="about-container">
            <div class="about-header">
                <span class="about-icon">📬</span>
                <h1>Contact Us</h1>
                <p class="about-tagline">We'd love to hear from you</p>
            </div>

            <section class="about-section">
                <h2>Get in touch</h2>
                <p>Have a question about trading, a topic suggestion, or feedback? Reach out and we'll get back to you.</p>
                <form class="newsletter-form" action="https://formsubmit.co/200203041018@silveroakuni.ac.in" method="POST" style="max-width: 600px;">
                    <input type="text" name="name" placeholder="Your name" required aria-label="Name" style="margin-bottom: 12px;">
                    <input type="email" name="email" placeholder="Your email" required aria-label="Email">
                    <textarea name="message" placeholder="Your message" required aria-label="Message" rows="5" style="width:100%;padding:12px;border:1px solid var(--border);border-radius:var(--radius);font-family:inherit;font-size:1rem;background:var(--bg);color:var(--text);margin-bottom:12px;resize:vertical;"></textarea>
                    <input type="hidden" name="_subject" value="📬 Contact — {SITE_NAME}">
                    <input type="hidden" name="_captcha" value="true">
                    <input type="hidden" name="_template" value="table">
                    <input type="hidden" name="_next" value="{BASE_URL}/contact.html?sent=true">
                    <button type="submit">Send Message →</button>
                </form>
            </section>
        </div>
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

{THEME_SCRIPT}
</body>
</html>'''

with open(os.path.join(SITE_DIR, 'contact.html'), 'w', encoding='utf-8') as f:
    f.write(contact_html)
print('  ✓ contact.html')

print(f'\\n✅ All site infrastructure files created in sites/{SITE_SLUG}/')
