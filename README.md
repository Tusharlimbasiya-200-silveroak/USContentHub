# USContentHub

A Django-powered content platform hosting **7 niche websites** for US audiences, covering tech, health, finance, travel, recipes, news, and trading. Articles are served as static HTML on GitHub Pages, with a full Django backend on Vercel for the main blog platform.

## Publications

| Publication | Niche | Articles | URL |
|---|---|---|---|
| Tech Gadget Hub | Technology & Gadgets | ~34 | [Visit](https://tusharlimbasiya-200-silveroak.github.io/tech-gadget-hub/) |
| Health & Wellness Daily | Health & Wellness | ~53 | [Visit](https://tusharlimbasiya-200-silveroak.github.io/health-wellness-daily/) |
| Smart Money Guide | Personal Finance | ~31 | [Visit](https://tusharlimbasiya-200-silveroak.github.io/smart-money-guide/) |
| USA Travel Explorer | Travel | ~67 | [Visit](https://tusharlimbasiya-200-silveroak.github.io/usa-travel-explorer/) |
| Recipe Kitchen USA | Recipes & Food | ~67 | [Visit](https://tusharlimbasiya-200-silveroak.github.io/recipe-kitchen-usa/) |
| USA News Digest | News & Trends | ~62 | [Visit](https://tusharlimbasiya-200-silveroak.github.io/usa-news-digest/) |
| The Trading Blueprint | Trading & Investing | ~18 | [Visit](https://tusharlimbasiya-200-silveroak.github.io/the-trading-blueprint/) |

## Project Structure

```
USContentHub/
├── api/
│   └── index.py                  # Vercel WSGI entry point
├── blog/                         # Django app (models, views, templates, URLs)
│   ├── migrations/               # 4 database migrations
│   ├── templates/blog/           # 14 Django HTML templates
│   ├── management/commands/      # import_blogs CLI command
│   ├── models.py                 # Publication, Article, Comment, Rating, etc.
│   ├── views.py                  # All views (home, article, search, auth, etc.)
│   ├── urls.py                   # URL routing
│   ├── sitemaps.py               # XML sitemaps
│   └── tests.py                  # Full test suite (1100+ lines)
├── writeflow/                    # Django project settings
│   ├── settings.py               # DB, cache, email, security, auth config
│   ├── urls.py                   # Root URL conf + sitemap
│   └── wsgi.py / asgi.py
├── sites/                        # Static HTML content per publication
│   ├── tech-gadget-hub/
│   ├── health-wellness-daily/
│   ├── smart-money-guide/
│   ├── usa-travel-explorer/
│   ├── recipe-kitchen-usa/
│   ├── usa-news-digest/
│   ├── the-trading-blueprint/
│   └── _low_quality/             # Articles with SEO score < 80 (not deployed)
├── pinterest_bot/
│   ├── pinterest_auto_pin.py     # Pinterest v5 API bot (7 pins/day)
│   └── pinned_tracker.json       # Tracks which articles have been pinned
├── .github/workflows/
│   ├── pinterest-daily.yml       # Daily cron: pins 1 article per publication
│   ├── deploy-sites.yml          # Deploys HTML sites to GitHub Pages
│   └── build-dashboard.yml       # Rebuilds dashboard.html on content push
├── dashboard.html                # Content stats dashboard
├── update_articles_json.py       # Utility: regenerates articles.json per site
├── manage.py
├── requirements.txt
├── vercel.json                   # Vercel deployment config
└── .env.example                  # Environment variable template
```

## Local Development

### Requirements

- Python 3.11+
- pip

### Setup

```bash
# 1. Clone and enter the project
git clone https://github.com/Tusharlimbasiya-200-silveroak/USContentHub.git
cd USContentHub

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment file and configure
cp .env.example .env
# Edit .env — at minimum set DJANGO_SECRET_KEY

# 5. Run migrations
python manage.py migrate

# 6. Load initial data (optional)
python manage.py loaddata blog/fixtures/initial_data.json

# 7. Start the development server
python manage.py runserver
```

Open http://localhost:8000 in your browser.

### Running Tests

```bash
python manage.py test blog
```

## Deployment

### Vercel (Django backend)

The Django app is deployed to Vercel via `api/index.py`. Required environment variables (set in Vercel dashboard):

| Variable | Purpose |
|---|---|
| `DJANGO_SECRET_KEY` | Strong random key — required |
| `DJANGO_DEBUG` | Set to `False` in production |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string (optional) |
| `SITE_URL` | Your production URL |
| `EMAIL_HOST` | SMTP host for newsletter emails |
| `EMAIL_HOST_USER` | SMTP username |
| `EMAIL_HOST_PASSWORD` | SMTP password |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Google OAuth (optional) |

### GitHub Pages (Static sites)

Each `sites/<publication>/` folder is deployed to its own GitHub Pages repo via the `deploy-sites.yml` workflow. Triggered on any push to `sites/**`.

### Pinterest Bot

The `pinterest_bot/pinterest_auto_pin.py` script runs daily via GitHub Actions (`.github/workflows/pinterest-daily.yml`). It pins 1 article per publication per day.

Required GitHub Secrets:
- `PINTEREST_ACCESS_TOKEN`
- `PINTEREST_BOARD_TECH`, `PINTEREST_BOARD_HEALTH`, `PINTEREST_BOARD_FINANCE`
- `PINTEREST_BOARD_TRAVEL`, `PINTEREST_BOARD_RECIPES`, `PINTEREST_BOARD_NEWS`, `PINTEREST_BOARD_TRADING`
- `SITE_URL`, `DEPLOY_TOKEN`

## Tech Stack

- **Backend**: Django 6.x + WhiteNoise + django-allauth
- **Database**: PostgreSQL
- **Cache**: Redis (production) / LocMemCache (development)
- **Hosting**: Vercel (Django) + GitHub Pages (static sites)
- **Automation**: GitHub Actions (deploy, Pinterest bot, dashboard)
- **Auth**: Custom auth + Google & Microsoft OAuth via django-allauth
