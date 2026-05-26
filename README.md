# USContentHub

A collection of 6 niche content websites hosted on GitHub Pages, covering technology, health, finance, travel, recipes, and news for US audiences.

## Sites

| Site | Niche | URL |
|------|-------|-----|
| tech-gadget-hub | Technology & Gadgets | [Visit](https://tusharlimbasiya-200-silveroak.github.io/tech-gadget-hub/) |
| health-wellness-daily | Health & Wellness | [Visit](https://tusharlimbasiya-200-silveroak.github.io/health-wellness-daily/) |
| smart-money-guide | Personal Finance | [Visit](https://tusharlimbasiya-200-silveroak.github.io/smart-money-guide/) |
| usa-travel-explorer | Travel | [Visit](https://tusharlimbasiya-200-silveroak.github.io/usa-travel-explorer/) |
| recipe-kitchen-usa | Recipes & Food | [Visit](https://tusharlimbasiya-200-silveroak.github.io/recipe-kitchen-usa/) |
| usa-news-digest | News & Trends | [Visit](https://tusharlimbasiya-200-silveroak.github.io/usa-news-digest/) |

## Structure

```
USContentHub/
├── sites/                    # All 6 niche website content
│   ├── tech-gadget-hub/
│   ├── health-wellness-daily/
│   ├── smart-money-guide/
│   ├── usa-travel-explorer/
│   ├── recipe-kitchen-usa/
│   └── usa-news-digest/
├── templates/                # Jinja2 HTML/CSS templates
├── blog-platform.html        # Blog platform page
├── dashboard.html            # Content dashboard
├── medium_platform/          # Flask-based blog platform
├── social_posts/             # Social media content
├── pinterest_pins/           # Pinterest pin content
├── quora_answers/            # Quora answer content
├── reddit_posts/             # Reddit post content
├── twitter_threads/          # Twitter thread content
├── youtube_shorts/           # YouTube shorts scripts
├── share_posts/              # Cross-platform sharing content
└── docs/                     # Guides & documentation
```

## Deployment

Content is auto-deployed via GitHub Actions. The workflow runs when new content is pushed and deploys each site to its own GitHub Pages repo.

## Related

- **[Workflow](https://github.com/Tusharlimbasiya-200-silveroak/Workflow)** — The automation engine that generates and deploys content to this hub.
