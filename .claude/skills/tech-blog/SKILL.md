---
name: tech-blog
description: Research and write a technical blog article (Python releases, AI/ML updates, frameworks, dev tooling, tech news) for the Tech Pulse publication. Drafts locally, shows the full article to the user for review, and ONLY pushes it live after the user explicitly approves. Usage - /tech-blog <topic> or /tech-blog (auto-picks the biggest recent tech story).
---

# Tech Blog Writer Agent

Write one technical blog article end-to-end: research → draft → user review → (on approval) publish live.

## Hard rules

1. **NEVER commit or push without the user's explicit "yes"** for THIS specific article. Approval of a past article never carries over.
2. The article is inserted into the configured PostgreSQL database as a draft for review. Do not mark it published until the user approves.
3. If the user rejects or asks for changes, never leave the rejected version in the DB before any push.
4. All facts must come from research done NOW (WebSearch/WebFetch) — never write tech "news" from memory; your knowledge is stale by definition.

## Workflow

### 1. Pick topic & research
- If the user gave a topic (e.g. "python 3.14", "new AI models"), research that.
- If no topic: WebSearch for the biggest developer/tech stories of the past ~7 days (use today's real date). Candidates: Python/language releases, major AI model launches, framework releases, security advisories, big tech announcements. Pick the single most newsworthy one and tell the user what you picked.
- Do 3-6 searches; fetch 2-4 primary sources (official release notes, blogs, announcements). Collect concrete facts: version numbers, dates, benchmarks, quotes, breaking changes.

### 2. Write the draft
Write a 1200–2000 word article as a JSON file at `drafts/<slug>.json`:

```json
{
  "publication": "tech-pulse",
  "title": "≤300 chars, specific and SEO-friendly",
  "subtitle": "≤500 chars, one-sentence hook",
  "slug": "kebab-case-unique-slug",
  "cover_image": "https://images.unsplash.com/photo-...?w=1200",
  "tags": ["python", "ai", "5-8 lowercase tags"],
  "meta_description": "≤300 chars SEO summary",
  "content": "<p>HTML body…</p>"
}
```

Content format (match existing site articles):
- Raw HTML: `<p>`, `<h2>`, `<h3>`, `<ul>/<li>`, `<strong>`, `<em>`, `<blockquote>`. Code in `<pre><code>…</code></pre>` with HTML-escaped contents.
- Open with a strong 2-paragraph lead (what happened + why it matters), then 4-7 `<h2>` sections, end with a "What This Means for Developers" or takeaway section.
- Cite concrete numbers/dates from research. No fabricated quotes or benchmarks.
- Cover image: a topically relevant `images.unsplash.com` URL with `?w=1200`.
- Slug must not collide: check `DATABASE_URL= python3 manage.py shell -c "from blog.models import Article; print(Article.objects.filter(slug='<slug>').exists())"`.

### 3. Stage for review
```bash
python3 publish_draft.py drafts/<slug>.json
```
(Draft insert only — not visible on public article pages because the status is `draft`.) Then start a local server if one isn't running (pick a free port, NOT 8765 — it's occupied):
```bash
python3 manage.py runserver 8799   # run_in_background
```

### 4. User review — REQUIRED GATE
First, email the draft to the reviewer (tusharlimbasiya200@gmail.com, override via REVIEW_EMAIL in .env):
```bash
python3 send_review_email.py drafts/<slug>.json
```
(If SMTP isn't configured it prints a warning instead of sending — tell the user, but continue the in-chat review either way.)

Then show the user:
- Title, subtitle, word count, read time, tags
- The full article text (readable, converted from HTML) in chat
- Local preview status: draft stored in PostgreSQL; public article URL is available only after approval/publish
- Whether the review email was sent

Then ask explicitly (AskUserQuestion): **"Publish this article live?"** with options Yes / Edit something / No.
- **Edit** → apply requested changes to the JSON, re-run publish_draft.py, show the diff of what changed, ask again.
- **No** → `python3 publish_draft.py --delete <slug>`. Keep the JSON in drafts/ (gitignored) in case they change their mind.

### 5. On "yes" — push live
```bash
python3 publish_draft.py drafts/<slug>.json --publish
```
- Content-only posts are stored in PostgreSQL and do not require a git commit.
- Poll the article URL `https://us-content-hub.vercel.app/article/<slug>/` until it returns 200.
- Confirm to the user with the live URL.

## Notes
- The `tech-pulse` publication is auto-created by publish_draft.py on first use (Tech Pulse 🧠, purple #7c3aed).
- Always run manage.py/script commands with the intended PostgreSQL `DATABASE_URL` loaded from the environment.
- One article per invocation. For a batch, finish the review cycle for each before starting the next.
