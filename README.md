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
- PostgreSQL connection string (`DATABASE_URL`), for example Neon in production

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
# Edit .env — set DJANGO_SECRET_KEY and DATABASE_URL

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

## Publishing content (single source of truth)

The database is the source of truth; the static GitHub Pages sites are a
generated artifact. Publish a new article with **one command** so the Vercel
(Neon) site and the GitHub Pages site stay in lockstep:

```bash
# Write a draft JSON (see publish.py docstring for the schema; `content` is the
# CLEAN body HTML only — no breadcrumb/newsletter/share chrome).
DATABASE_URL='postgres://…neon…' python3 publish.py drafts/my-article.json --commit
git push        # deploy-sites.yml then ships the static side to gh-pages
```

`publish.py` upserts the article into the DB, then runs `export_static` to
(re)generate the article HTML + `articles.json` entry + homepage card +
sitemap URL for that publication. `export_static` is idempotent and
non-lossy — it only touches the given slug and preserves the extra
`articles.json` fields the DB does not model.

- `python manage.py export_static --slug <slug> [--check]` — render specific articles from the DB.
- `python manage.py import_blogs` — legacy static→DB bridge; also runs in CI (`sync-db.yml`) as a drift safety net. Additive (skips existing slugs).

> Never paste the production `DATABASE_URL` on the command line interactively —
> set it as a GitHub Actions secret (below) and let CI run the DB writes.

## Deployment

### Vercel (Django backend)

The Django app is deployed to Vercel via `api/index.py`. Required environment variables (set in Vercel dashboard):

| Variable | Purpose |
|---|---|
| `DJANGO_SECRET_KEY` | Strong random key — required |
| `DJANGO_DEBUG` | Set to `False` in production |
| `DATABASE_URL` | PostgreSQL/Neon connection string — required |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hosts; include custom domains |
| `DATABASE_TEST_NAME` | Optional explicit test DB name for `manage.py test` |
| `REDIS_URL` | Redis/Upstash connection string — recommended for production scale |
| `SITE_URL` | Your production URL |
| `EMAIL_HOST` | SMTP host for newsletter emails |
| `EMAIL_HOST_USER` | SMTP username |
| `EMAIL_HOST_PASSWORD` | SMTP password |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Google OAuth (optional) |

### GitHub Pages (Static sites)

Each active `sites/<publication>/` folder is deployed to its own GitHub Pages repo via the `deploy-sites.yml` workflow. Triggered on any push to `sites/**`.

### Database sync (`sync-db.yml`)

On every push to `sites/**`, this workflow mirrors any new articles into the
Neon database so the dynamic site never falls behind GitHub Pages. It reads
credentials from GitHub Secrets — **never** from the repo:

- `DATABASE_URL` — the Neon/PostgreSQL connection string (same value as Vercel)
- `DJANGO_SECRET_KEY` — any strong key (only needed for Django to boot)

Add them in **repo Settings → Secrets and variables → Actions**.

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
