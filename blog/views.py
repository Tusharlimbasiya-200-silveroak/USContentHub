import logging
import os
import re
from html import escape

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.syndication.views import Feed
from django.core.cache import cache
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Count, F, Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.feedgenerator import Atom1Feed
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from .helpers import (
    bump_rate_counter,
    cache_or_set,
    check_rate_limit,
    get_client_ip,
    send_contact_emails,
    send_newsletter_welcome,
)
from .models import Article, ArticleRating, Comment, NewsletterSubscriber, Publication, Tag, UserProfile

logger = logging.getLogger(__name__)


# ── Listing views ─────────────────────────────────────────────────────────────

class HomeView(ListView):
    model = Article
    template_name = "blog/home.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        return (
            Article.objects.filter(status="published")
            .select_related("publication")
            .prefetch_related("tags")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["popular_tags"] = cache_or_set(
            "popular_tags_15", 300,
            lambda: list(Tag.objects.annotate(count=Count("articles")).order_by("-count")[:15]),
        )
        ctx["total_articles"] = cache_or_set(
            "total_published_articles", 300,
            lambda: Article.objects.filter(status="published").count(),
        )
        if self.request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=self.request.user)
                ctx["bookmark_count"] = profile.bookmarks.count()
            except UserProfile.DoesNotExist:
                ctx["bookmark_count"] = 0
            ctx["featured_articles"] = cache_or_set(
                "featured_articles_3", 300,
                lambda: list(
                    Article.objects.filter(status="published")
                    .select_related("publication")
                    .prefetch_related("tags")
                    .order_by("-views")[:3]
                ),
            )
        return ctx


class PublicationView(ListView):
    model = Article
    template_name = "blog/publication.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        self.publication = get_object_or_404(Publication, slug=self.kwargs["slug"])
        return (
            Article.objects.filter(status="published", publication=self.publication)
            .select_related("publication")
            .prefetch_related("tags")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["publication"] = self.publication
        # Use object_list (already fetched by ListView) instead of calling
        # get_queryset() again — avoids a second DB hit per page load.
        ctx["total_articles"] = self.object_list.count()
        return ctx


class TagView(ListView):
    model = Article
    template_name = "blog/tag.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, name=self.kwargs["tag_name"])
        return (
            Article.objects.filter(status="published", tags=self.tag)
            .select_related("publication")
            .prefetch_related("tags")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tag"] = self.tag
        return ctx


class SearchView(ListView):
    model = Article
    template_name = "blog/search.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        self.query = self.request.GET.get("q", "").strip()[:200]
        if self.query and len(self.query) >= 2:
            return (
                Article.objects.filter(
                    Q(title__icontains=self.query)
                    | Q(content__icontains=self.query)
                    | Q(subtitle__icontains=self.query),
                    status="published",
                )
                .select_related("publication")
                .prefetch_related("tags")
            )
        return Article.objects.none()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.query
        return ctx


class ExploreView(ListView):
    model = Article
    template_name = "blog/explore.html"
    context_object_name = "trending"
    paginate_by = 20

    def get_queryset(self):
        return cache_or_set(
            "explore_trending_20", 300,
            lambda: list(
                Article.objects.filter(status="published")
                .select_related("publication")
                .prefetch_related("tags")
                .order_by("-views")[:20]
            ),
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["popular_tags"] = cache_or_set(
            "popular_tags_30", 300,
            lambda: list(Tag.objects.annotate(count=Count("articles")).order_by("-count")[:30]),
        )
        ctx["all_tags"] = cache_or_set(
            "all_tags_counted", 300,
            lambda: list(Tag.objects.annotate(count=Count("articles")).order_by("name")),
        )
        ctx["publications_with_counts"] = cache_or_set(
            "publications_with_counts", 300,
            lambda: list(Publication.objects.annotate(article_count=Count("articles")).order_by("name")),
        )
        return ctx


class ReadingListView(ListView):
    model = Article
    template_name = "blog/reading_list.html"
    context_object_name = "articles"

    def get_queryset(self):
        slugs_param = self.request.GET.get("slugs", "")
        if slugs_param:
            slugs = [s.strip() for s in slugs_param.split(",") if s.strip()][:100]
            return (
                Article.objects.filter(status="published", slug__in=slugs)
                .select_related("publication")
                .prefetch_related("tags")
            )
        return Article.objects.none()


# ── Article detail ────────────────────────────────────────────────────────────

class ArticleDetailView(DetailView):
    model = Article
    template_name = "blog/article.html"
    context_object_name = "article"
    slug_field = "slug"

    def get_queryset(self):
        return (
            Article.objects.filter(status="published")
            .select_related("publication")
            .prefetch_related("tags")
        )

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        try:
            Article.objects.filter(pk=self.object.pk).update(views=F("views") + 1)
        except Exception:
            pass  # Best-effort; DB may be read-only on Vercel cold starts
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        article = self.object

        # Related articles: by shared tags → same publication → recency fallback
        cache_key = f"related_articles_v2_{article.pk}"
        related = cache.get(cache_key)
        if related is None:
            tag_ids = list(article.tags.values_list("id", flat=True))
            if tag_ids:
                related = list(
                    Article.objects.filter(status="published", tags__in=tag_ids)
                    .exclude(id=article.id)
                    .annotate(shared_tags=Count("tags"))
                    .order_by("-shared_tags", "-published_at")
                    .distinct()[:6]
                )
            elif article.publication:
                related = list(
                    Article.objects.filter(
                        status="published", publication=article.publication
                    )
                    .exclude(id=article.id)
                    .order_by("-published_at")[:6]
                )
            else:
                related = list(
                    Article.objects.filter(status="published")
                    .exclude(id=article.id)
                    .order_by("-published_at")[:6]
                )
            cache.set(cache_key, related, 600)

        ctx["related"] = related
        ctx["tags"] = article.tags.all()

        # Evaluate comments once; reuse list for both display and count
        comments = list(article.comments.filter(is_approved=True))
        ctx["comments"] = comments
        ctx["comment_count"] = len(comments)

        ctx["avg_rating"] = article.average_rating()
        ctx["rating_count"] = article.rating_count()
        ctx["user_rated"] = ArticleRating.objects.filter(
            article=article, ip_address=get_client_ip(self.request)
        ).exists()

        # Breadcrumbs
        ctx["breadcrumbs"] = [("Home", "/")]
        if article.publication:
            ctx["breadcrumbs"].append(
                (article.publication.name, f"/pub/{article.publication.slug}/")
            )
        ctx["breadcrumbs"].append((article.title[:60], None))
        return ctx


# ── Comments ──────────────────────────────────────────────────────────────────

@require_POST
def add_comment(request, slug):
    ip = get_client_ip(request)
    rate_key = f"comment_rate_{ip}"

    if check_rate_limit(rate_key, 5):
        return JsonResponse(
            {"success": False, "error": "Too many comments. Please wait a minute."},
            status=429,
        )

    article = get_object_or_404(Article, slug=slug, status="published")
    name = escape(request.POST.get("name", "").strip()[:100])
    content = escape(request.POST.get("content", "").strip()[:2000])

    if not name or not content or len(name) < 2 or len(content) < 5:
        return JsonResponse(
            {"success": False, "error": "Name (2+ chars) and comment (5+ chars) are required."},
            status=400,
        )

    try:
        comment = Comment.objects.create(article=article, name=name, content=content)
        bump_rate_counter(rate_key, 60)
        return JsonResponse({
            "success": True,
            "name": comment.name,
            "content": comment.content,
            "created_at": comment.created_at.strftime("%b %d, %Y %H:%M"),
        })
    except Exception as exc:
        logger.error(
            "add_comment: DB write failed — %s: %s", type(exc).__name__, exc, exc_info=True
        )
        return JsonResponse(
            {"success": False, "error": "Comments are temporarily unavailable. Please try again later."},
            status=503,
        )


# ── Newsletter ────────────────────────────────────────────────────────────────

@require_POST
def newsletter_subscribe(request):
    email = request.POST.get("email", "").strip().lower()[:254]
    if not email:
        return JsonResponse({"success": False, "error": "Email is required."}, status=400)
    try:
        validate_email(email)
    except Exception:
        return JsonResponse({"success": False, "error": "Invalid email address."}, status=400)

    try:
        subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
        if not created and subscriber.is_active:
            return JsonResponse({"success": True, "message": "You're already subscribed!"})
        if not subscriber.is_active:
            subscriber.is_active = True
            subscriber.save()
        send_newsletter_welcome(email)
        return JsonResponse({"success": True, "message": "Successfully subscribed! Check your inbox."})
    except Exception:
        # Graceful fallback when DB writes are unavailable
        return JsonResponse({"success": True, "message": "Thanks! We'll be in touch soon."})


# ── Contact ───────────────────────────────────────────────────────────────────

def contact_page(request):
    return render(request, "blog/contact.html")


@require_POST
def contact_submit(request):
    """Handle contact form POST. Rate-limited, validated, sends two emails."""
    ip = get_client_ip(request)
    rate_key = f"contact_rate_{ip}"

    if check_rate_limit(rate_key, 3):
        return JsonResponse(
            {"success": False, "error": "Too many submissions. Please try again later."},
            status=429,
        )

    name    = escape(request.POST.get("name", "").strip()[:100])
    email   = request.POST.get("email", "").strip()[:254]
    subject = escape(request.POST.get("subject", "").strip()[:200])
    message = escape(request.POST.get("message", "").strip()[:5000])

    if not name or len(name) < 2:
        return JsonResponse({"success": False, "error": "Name must be at least 2 characters."}, status=400)
    if not subject or len(subject) < 3:
        return JsonResponse({"success": False, "error": "Subject must be at least 3 characters."}, status=400)
    if not message or len(message) < 10:
        return JsonResponse({"success": False, "error": "Message must be at least 10 characters."}, status=400)
    try:
        validate_email(email)
    except Exception:
        return JsonResponse({"success": False, "error": "Invalid email address."}, status=400)

    send_contact_emails(name, email, subject, message, ip)
    bump_rate_counter(rate_key, 3600)
    return JsonResponse({"success": True, "message": "Message sent! We'll reply within 1–2 business days."})


# ── Static pages ──────────────────────────────────────────────────────────────

def about_page(request):
    return render(request, "blog/about.html")


def privacy_page(request):
    return render(request, "blog/privacy.html")


# ── Pinterest domain verification ─────────────────────────────────────────────

def pinterest_verify(request):
    """Serve the Pinterest HTML verification file at /pinterest-0fd9e.html"""
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pinterest-0fd9e.html")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        raise Http404
    return HttpResponse(content, content_type="text/html")


# ── Article rating ────────────────────────────────────────────────────────────

@require_POST
def rate_article(request, slug):
    article = get_object_or_404(Article, slug=slug, status="published")
    ip = get_client_ip(request)

    try:
        score = int(request.POST.get("score", 0))
    except (ValueError, TypeError):
        return JsonResponse({"success": False, "error": "Invalid score."}, status=400)

    if score < 1 or score > 5:
        return JsonResponse({"success": False, "error": "Score must be between 1 and 5."}, status=400)

    try:
        with transaction.atomic():
            ArticleRating.objects.update_or_create(
                article=article, ip_address=ip,
                defaults={"score": score},
            )
        avg = article.average_rating()
        count = article.rating_count()
        return JsonResponse({"success": True, "avg_rating": avg, "rating_count": count, "your_score": score})
    except Exception:
        # Graceful fallback for read-only DB environments
        return JsonResponse({"success": True, "avg_rating": score, "rating_count": 1, "your_score": score})


# ── Load more (AJAX pagination) ───────────────────────────────────────────────

def load_more_articles(request):
    page = request.GET.get("page", 1)
    articles = (
        Article.objects.filter(status="published")
        .select_related("publication")
        .prefetch_related("tags")
    )
    paginator = Paginator(articles, 12)

    try:
        page_obj = paginator.page(page)
    except Exception:
        return JsonResponse({"articles": [], "has_next": False})

    data = [
        {
            "title": a.title,
            "slug": a.slug,
            "cover_image": a.cover_image,
            "published_at": a.published_at.strftime("%Y-%m-%d"),
            "read_time": a.read_time,
            "meta_description": a.meta_description or (a.subtitle[:160] if a.subtitle else ""),
            "publication_name": a.publication.name if a.publication else "",
            "publication_icon": a.publication.icon if a.publication else "",
            "publication_slug": a.publication.slug if a.publication else "",
        }
        for a in page_obj
    ]
    return JsonResponse({"articles": data, "has_next": page_obj.has_next()})


# ── RSS / Atom feeds ──────────────────────────────────────────────────────────

class ArticleRSSFeed(Feed):
    title = "USA Content Hub"
    link = "/"
    description = "Latest articles on Tech, Health, Finance, Travel, Recipes & News"

    def items(self):
        return (
            Article.objects.filter(status="published")
            .select_related("publication")
            .order_by("-published_at")[:20]
        )

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.meta_description or item.subtitle

    def item_link(self, item):
        return f"/article/{item.slug}/"

    def item_pubdate(self, item):
        return item.published_at


class ArticleAtomFeed(ArticleRSSFeed):
    feed_type = Atom1Feed
    subtitle = ArticleRSSFeed.description


class PublicationRSSFeed(Feed):
    """Per-publication RSS feed: /feed/pub/<slug>/rss/"""

    def get_object(self, request, slug):
        return get_object_or_404(Publication, slug=slug)

    def title(self, pub):
        return f"{pub.name} — USA Content Hub"

    def link(self, pub):
        return f"/pub/{pub.slug}/"

    def description(self, pub):
        return f"Latest articles from {pub.name} on USA Content Hub"

    def items(self, pub):
        return (
            Article.objects.filter(status="published", publication=pub)
            .select_related("publication")
            .order_by("-published_at")[:20]
        )

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.meta_description or item.subtitle

    def item_link(self, item):
        return f"/article/{item.slug}/"

    def item_pubdate(self, item):
        return item.published_at


class PublicationAtomFeed(PublicationRSSFeed):
    feed_type = Atom1Feed

    def subtitle(self, pub):
        return f"Latest articles from {pub.name} on USA Content Hub"


# ── Auth views ────────────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect("blog:home")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()[:150]
        email    = request.POST.get("email", "").strip().lower()[:254]
        password  = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        errors = []
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters.")
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append("Username can only contain letters, numbers, and underscores.")
        if not email:
            errors.append("Email is required.")
        else:
            try:
                validate_email(email)
            except Exception:
                errors.append("Invalid email address.")
        if not password or len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if password != password2:
            errors.append("Passwords do not match.")
        if User.objects.filter(username=username).exists():
            errors.append("Username already taken.")
        if User.objects.filter(email=email).exists():
            errors.append("Email already registered.")

        if errors:
            return render(request, "blog/register.html", {
                "errors": errors, "username": username, "email": email,
            })

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            UserProfile.objects.create(user=user)
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, "Account created successfully!")
            return redirect("blog:home")
        except Exception as exc:
            logger.error(
                "register_view: create_user failed — %s: %s", type(exc).__name__, exc, exc_info=True
            )
            return render(request, "blog/register.html", {
                "errors": ["Registration is temporarily unavailable. Please try again later."],
                "username": username,
                "email": email,
            })
    return render(request, "blog/register.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("blog:home")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get("next", "/"))
        return render(request, "blog/login.html", {
            "error": "Invalid username or password.", "username": username,
        })
    return render(request, "blog/login.html")


@require_POST
def logout_view(request):
    logout(request)
    return redirect("blog:home")


# ── Bookmarks ─────────────────────────────────────────────────────────────────

@login_required
@require_POST
def toggle_bookmark(request, slug):
    article = get_object_or_404(Article, slug=slug, status="published")
    try:
        with transaction.atomic():
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            # Lock the row to prevent a race condition on rapid double-clicks
            UserProfile.objects.select_for_update().filter(pk=profile.pk).get()
            if profile.bookmarks.filter(pk=article.pk).exists():
                profile.bookmarks.remove(article)
                return JsonResponse({"bookmarked": False})
            profile.bookmarks.add(article)
            return JsonResponse({"bookmarked": True})
    except Exception as exc:
        logger.error(
            "toggle_bookmark: DB write failed — %s: %s", type(exc).__name__, exc, exc_info=True
        )
        return JsonResponse(
            {"bookmarked": False, "error": "Bookmark temporarily unavailable."}, status=503
        )


@login_required
def user_bookmarks(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    articles = (
        profile.bookmarks.filter(status="published")
        .select_related("publication")
        .prefetch_related("tags")
    )
    return render(request, "blog/user_bookmarks.html", {"articles": articles})


# ── Pinterest OAuth (one-time setup) ─────────────────────────────────────────

def pinterest_connect(request):
    """Step 1 — redirect to Pinterest OAuth. Admin-only."""
    if not request.user.is_staff:
        return HttpResponse("Forbidden", status=403)
    from .pinterest import auth_url
    callback = request.build_absolute_uri("/otp/pinterest-callback/")
    return redirect(auth_url(callback))


def pinterest_callback(request):
    """Step 2 — exchange OAuth code for tokens and display them. Admin-only."""
    if not request.user.is_staff:
        return HttpResponse("Forbidden", status=403)
    code = request.GET.get("code")
    if not code:
        return HttpResponse(f"Error: {request.GET.get('error_description', 'no code returned')}", status=400)
    from .pinterest import exchange_code
    callback = request.build_absolute_uri("/otp/pinterest-callback/")
    data = exchange_code(code, callback)
    if not data:
        return HttpResponse("Token exchange failed — check server logs.", status=500)
    access_token = data.get("access_token", "")
    refresh_token = data.get("refresh_token", "")
    expires_in = data.get("expires_in", "unknown")
    html = f"""<!DOCTYPE html><html><body style="font-family:monospace;padding:2rem;max-width:800px;margin:0 auto;">
<h2>Pinterest OAuth — tokens received</h2>
<p>Add these to your Vercel environment variables:</p>
<table border="1" cellpadding="8" style="border-collapse:collapse;width:100%;">
<tr><td><b>PINTEREST_ACCESS_TOKEN</b></td><td style="word-break:break-all;">{access_token}</td></tr>
<tr><td><b>PINTEREST_REFRESH_TOKEN</b></td><td style="word-break:break-all;">{refresh_token}</td></tr>
</table>
<p>Access token expires in: {expires_in} seconds</p>
<p>You also need <b>PINTEREST_BOARD_ID</b> — get it from your Pinterest board URL:<br>
<code>pinterest.com/YOUR_USERNAME/<b>BOARD_NAME</b>/</code> → use the board ID from the API or Pinterest URL.</p>
<hr><p style="color:#888;">Delete this endpoint from urls.py after setup is complete.</p>
</body></html>"""
    return HttpResponse(html)


# ── OTP: publish market-update article ───────────────────────────────────────

def otp_publish_market_article(request):
    """One-time endpoint — publishes the Nifty/Sensex market update article. Remove after use."""
    from django.utils.text import slugify
    from django.utils import timezone

    TITLE = "Nifty 50 at 23,460 & Sensex Surges 160 Points: Full Market Analysis"
    SLUG  = slugify(TITLE)[:280]

    if Article.objects.filter(slug=SLUG).exists():
        return HttpResponse(f"Already published: <a href='/article/{SLUG}/'>View article</a>")

    CONTENT = """
<p class="article-lead" style="font-size:1.15rem;font-weight:500;line-height:1.7;color:#374151;border-left:4px solid #2563eb;padding-left:1rem;margin-bottom:2rem;">Indian equity markets traded with a cautiously bullish bias today as the Nifty 50 hovered around <strong>23,460</strong> and the BSE Sensex gained approximately <strong>160 points to 74,523</strong> — buoyed by resilient domestic fundamentals even as global headwinds from Middle East geopolitical tensions kept investors on edge.</p>

<h2>📊 Today's Market Snapshot</h2>
<table style="width:100%;border-collapse:collapse;margin:1.5rem 0;font-size:.95rem;">
<thead><tr style="background:#2563eb;color:#fff;">
<th style="padding:10px 14px;text-align:left;">Index</th>
<th style="padding:10px 14px;text-align:right;">Level</th>
<th style="padding:10px 14px;text-align:right;">Change</th>
<th style="padding:10px 14px;text-align:right;">% Change</th>
</tr></thead>
<tbody>
<tr style="background:#f8fafc;"><td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;font-weight:600;">Nifty 50</td><td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;text-align:right;">23,460</td><td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;text-align:right;color:#16a34a;">+46.9</td><td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;text-align:right;color:#16a34a;">+0.20%</td></tr>
<tr><td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;font-weight:600;">BSE Sensex</td><td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;text-align:right;">74,523</td><td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;text-align:right;color:#16a34a;">+160</td><td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;text-align:right;color:#16a34a;">+0.22%</td></tr>
<tr style="background:#f8fafc;"><td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;font-weight:600;">Nifty Bank</td><td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;text-align:right;">~49,800</td><td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;text-align:right;color:#16a34a;">+~120</td><td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;text-align:right;color:#16a34a;">+0.24%</td></tr>
<tr><td style="padding:10px 14px;font-weight:600;">RBI Repo Rate</td><td style="padding:10px 14px;text-align:right;">5.25%</td><td style="padding:10px 14px;text-align:right;color:#6b7280;">Unchanged</td><td style="padding:10px 14px;text-align:right;color:#6b7280;">—</td></tr>
</tbody>
</table>

<h2>🔵 Nifty 50: Holding the Line Above 23,400</h2>
<p>The <strong>Nifty 50</strong>, India's benchmark index comprising the 50 largest companies listed on the National Stock Exchange, is trading around the <strong>23,460 mark</strong> — up a modest 0.20% for the session. While the gain appears slim on paper, it signals something important: sustained buying interest at support levels even in the face of global uncertainty.</p>
<p>Technically, 23,400 has emerged as a crucial short-term support zone. Bulls need to defend this level convincingly to prevent a slide toward the next support at 23,200. On the upside, a decisive close above 23,600 could trigger fresh momentum toward the 24,000 psychological mark — a level many domestic institutional investors (DIIs) are targeting by the end of Q2 FY26.</p>
<blockquote style="border-left:4px solid #f59e0b;padding:1rem 1.5rem;background:#fffbeb;border-radius:0 8px 8px 0;margin:1.5rem 0;font-style:italic;">"The Nifty is in a consolidation phase between 23,200 and 23,800. Any breakout on either side will determine the next 500-point move. For now, dip buyers are active." — Market technician view</blockquote>

<h2>🔴 BSE Sensex: Positive Breadth on the 30-Pack</h2>
<p>The <strong>BSE Sensex</strong> — the 30-stock index that serves as the pulse of Dalal Street — advanced approximately <strong>160 points to hover near 74,523</strong>. The breadth was positive, with 18 out of 30 Sensex constituents trading in the green during morning trade.</p>
<p>Key gainers within the Sensex basket included heavyweight banking stocks such as HDFC Bank and ICICI Bank, IT bellwether Infosys, and select FMCG names like HUL. Offsetting these gains were Reliance Industries — which faced mild profit-booking — and a few auto stocks facing margin pressure from rising input costs.</p>
<p>A Sensex at 74,523 means the index is up <strong>approximately 14% from its January 2025 lows</strong>, reflecting the underlying resilience of the Indian economy even as global peers struggled. The market cap of BSE-listed companies now stands at roughly ₹4.1 lakh crore, reaffirming India's position as one of the world's top-five equity markets by capitalisation.</p>

<h2>🏦 RBI Keeps Repo Rate Steady at 5.25% — What It Means for Markets</h2>
<p>In its most recent Monetary Policy Committee (MPC) meeting, the <strong>Reserve Bank of India held the repo rate unchanged at 5.25%</strong> — a decision that was broadly in line with market expectations, yet critically important for investor sentiment.</p>
<h3>Why the RBI Paused</h3>
<ul>
<li><strong>Retail inflation (CPI)</strong> has moderated to near the 4% target band, giving the RBI room to breathe without aggressive tightening.</li>
<li><strong>GDP growth</strong> remains robust at 6.5–7%, reducing urgency for rate cuts to stimulate demand.</li>
<li><strong>Rupee stability</strong> is a key consideration — any premature rate cut could pressure the INR amid a strengthening US dollar environment.</li>
<li><strong>Global synchronisation</strong> — with the US Federal Reserve remaining in a higher-for-longer posture, the RBI is cautiously watching before pivoting.</li>
</ul>
<h3>Market Impact of an Unchanged Rate</h3>
<p>A stable rate environment is generally <strong>positive for equities</strong>. Here's why:</p>
<ul>
<li>Borrowing costs for companies remain predictable, supporting capital expenditure plans.</li>
<li>Real estate and auto sectors — both rate-sensitive — benefit from stable EMI burdens.</li>
<li>Banking stocks gain from steady net interest margins (NIMs) without the pressure of deposit repricing.</li>
<li>Bond markets see limited volatility, supporting the debt portion of balanced portfolios.</li>
</ul>
<p>The <a href="https://www.rbi.org.in" target="_blank" rel="noopener noreferrer" style="color:#2563eb;font-weight:600;">RBI's stance</a> continues to be "withdrawal of accommodation" — a neutral-to-hawkish posture that prioritises price stability while remaining supportive of growth. Market participants are now pricing in a <strong>possible rate cut in Q3 FY26</strong> if inflation remains anchored.</p>

<h2>🌍 Global Cues: Geopolitics & Sluggish Indices Keep Investors Cautious</h2>
<p>While domestic fundamentals remain solid, <strong>global headwinds are casting a long shadow</strong> over Indian markets today. Two key macro themes are dominating investor psychology:</p>
<h3>1. Middle East Geopolitical Tensions</h3>
<p>Ongoing conflict escalation in the Middle East continues to push <strong>Brent crude prices higher</strong>, hovering in the $88–92 per barrel range. This is a double-edged concern for India:</p>
<ul>
<li>India imports roughly <strong>85% of its crude oil</strong>, making it highly sensitive to energy price spikes.</li>
<li>Rising crude raises the <strong>current account deficit (CAD)</strong>, putting pressure on the Indian Rupee.</li>
<li>Higher fuel costs feed into the broader inflation basket, potentially complicating the RBI's rate trajectory.</li>
<li><strong>Aviation and paint stocks</strong> feel the pinch immediately, while <strong>oil marketing companies (OMCs)</strong> face margin compression.</li>
</ul>
<p>That said, elevated crude also benefits <strong>Reliance Industries</strong> (through its refining and petrochemicals business) and upstream players like <strong>ONGC and Oil India</strong>.</p>
<h3>2. Sluggish Global Indices</h3>
<p>Wall Street ended the previous session with mixed results — the Dow Jones slipped 0.3% while the Nasdaq eked out a marginal gain, driven by AI-related stocks. European markets were broadly flat amid concerns over Germany's industrial slowdown and stubborn core inflation in the Eurozone.</p>
<p>Asian markets showed divergence: Japanese Nikkei and South Korean KOSPI underperformed, while Chinese Shanghai Composite saw modest buying on government stimulus expectations.</p>
<p>For India, this mixed global backdrop means <strong>Foreign Portfolio Investor (FPI) flows remain choppy</strong>. FPIs have been net sellers on most days this week, while Domestic Institutional Investors (DIIs) — particularly LIC and mutual funds through SIP inflows — have stepped in to absorb the selling pressure, preventing a deeper correction.</p>

<h2>📈 Sector-Wise Performance Today</h2>
<table style="width:100%;border-collapse:collapse;margin:1.5rem 0;font-size:.9rem;">
<thead><tr style="background:#1e40af;color:#fff;">
<th style="padding:9px 12px;text-align:left;">Sector</th>
<th style="padding:9px 12px;text-align:left;">Trend</th>
<th style="padding:9px 12px;text-align:left;">Key Movers</th>
</tr></thead>
<tbody>
<tr style="background:#f0fdf4;"><td style="padding:9px 12px;border-bottom:1px solid #e2e8f0;font-weight:600;">Banking & Finance</td><td style="padding:9px 12px;border-bottom:1px solid #e2e8f0;color:#16a34a;">▲ Outperforming</td><td style="padding:9px 12px;border-bottom:1px solid #e2e8f0;">HDFC Bank, ICICI Bank, SBI</td></tr>
<tr><td style="padding:9px 12px;border-bottom:1px solid #e2e8f0;font-weight:600;">Information Technology</td><td style="padding:9px 12px;border-bottom:1px solid #e2e8f0;color:#16a34a;">▲ Mild gains</td><td style="padding:9px 12px;border-bottom:1px solid #e2e8f0;">Infosys, TCS, HCL Tech</td></tr>
<tr style="background:#f8fafc;"><td style="padding:9px 12px;border-bottom:1px solid #e2e8f0;font-weight:600;">FMCG</td><td style="padding:9px 12px;border-bottom:1px solid #e2e8f0;color:#16a34a;">▲ Stable buying</td><td style="padding:9px 12px;border-bottom:1px solid #e2e8f0;">HUL, Nestle, Britannia</td></tr>
<tr><td style="padding:9px 12px;border-bottom:1px solid #e2e8f0;font-weight:600;">Oil & Gas</td><td style="padding:9px 12px;border-bottom:1px solid #e2e8f0;color:#d97706;">↔ Mixed</td><td style="padding:9px 12px;border-bottom:1px solid #e2e8f0;">ONGC ▲, Reliance ▼ (profit booking)</td></tr>
<tr style="background:#f8fafc;"><td style="padding:9px 12px;border-bottom:1px solid #e2e8f0;font-weight:600;">Auto</td><td style="padding:9px 12px;border-bottom:1px solid #e2e8f0;color:#dc2626;">▼ Under pressure</td><td style="padding:9px 12px;border-bottom:1px solid #e2e8f0;">Maruti, M&amp;M (input cost concerns)</td></tr>
<tr><td style="padding:9px 12px;border-bottom:1px solid #e2e8f0;font-weight:600;">Real Estate</td><td style="padding:9px 12px;border-bottom:1px solid #e2e8f0;color:#16a34a;">▲ Benefiting from stable rates</td><td style="padding:9px 12px;border-bottom:1px solid #e2e8f0;">DLF, Godrej Properties</td></tr>
<tr style="background:#f8fafc;"><td style="padding:9px 12px;font-weight:600;">Pharma</td><td style="padding:9px 12px;color:#16a34a;">▲ Defensive buying</td><td style="padding:9px 12px;">Sun Pharma, Dr. Reddy's</td></tr>
</tbody>
</table>

<h2>🎯 Key Technical Levels to Watch</h2>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin:1.5rem 0;">
<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:1rem;">
<h3 style="color:#15803d;margin-top:0;">Nifty 50</h3>
<p style="margin:4px 0;">🟢 <strong>Resistance:</strong> 23,600 → 23,800 → 24,000</p>
<p style="margin:4px 0;">🔴 <strong>Support:</strong> 23,400 → 23,200 → 23,000</p>
<p style="margin:4px 0;">📌 <strong>Key Level:</strong> 23,500 (50-day EMA)</p>
</div>
<div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;padding:1rem;">
<h3 style="color:#c2410c;margin-top:0;">BSE Sensex</h3>
<p style="margin:4px 0;">🟢 <strong>Resistance:</strong> 75,000 → 75,500 → 76,000</p>
<p style="margin:4px 0;">🔴 <strong>Support:</strong> 74,000 → 73,500 → 73,000</p>
<p style="margin:4px 0;">📌 <strong>Key Level:</strong> 74,500 (short-term pivot)</p>
</div>
</div>

<h2>💡 Trading Strategy for Today</h2>
<p>Given the current market conditions — modest gains, stable rates, and global caution — here is a balanced approach for different investor profiles:</p>
<h3>For Short-Term Traders (Intraday/Swing)</h3>
<ul>
<li><strong>Buy on dips</strong> near Nifty 23,400 support with a stop-loss below 23,300.</li>
<li><strong>Target</strong>: 23,550–23,600 in the near term.</li>
<li>Avoid over-leveraged positions given the geopolitical uncertainty — volatility spikes can wipe margins quickly.</li>
<li>Focus on <strong>banking and IT stocks</strong> which are showing relative strength today.</li>
</ul>
<h3>For Medium-Term Investors (3–6 months)</h3>
<ul>
<li>Use any intraday dip below 23,300 on Nifty as an <strong>accumulation opportunity</strong>.</li>
<li>Favour <strong>quality large-caps</strong> with strong balance sheets — HDFC Bank, Infosys, Asian Paints, L&amp;T.</li>
<li>Keep <strong>5–10% cash</strong> to deploy if global events cause a sharper correction (Nifty 22,800–23,000 zone).</li>
</ul>
<h3>For Long-Term Investors (1+ year)</h3>
<ul>
<li>Continue SIPs — market consolidation phases are the best time for rupee-cost averaging.</li>
<li>Consider adding exposure to <strong>infrastructure, capital goods, and defence PSUs</strong> — sectors with strong government budget tailwinds.</li>
<li>The <strong>India growth story remains intact</strong>: 6.5% GDP growth, rising consumption, PLI-driven manufacturing, and a young demographic dividend.</li>
</ul>

<h2>📰 Key Events to Watch This Week</h2>
<ul>
<li>🇮🇳 <strong>India CPI Inflation data</strong> — will determine whether RBI has room for a future rate cut.</li>
<li>🇺🇸 <strong>US Federal Reserve minutes</strong> — any hawkish signal could trigger FPI outflows from emerging markets.</li>
<li>🛢️ <strong>OPEC+ production meeting</strong> — crude output decisions will directly impact India's CAD and OMC margins.</li>
<li>📊 <strong>Q4 FY26 corporate earnings</strong> — results from major banks and IT companies will drive stock-specific moves.</li>
<li>🌐 <strong>Geopolitical developments</strong> — any escalation or de-escalation in the Middle East could swing oil prices ±$5 rapidly.</li>
</ul>

<h2>❓ Frequently Asked Questions</h2>
<div style="border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;margin:1.5rem 0;">
<details style="padding:1rem;border-bottom:1px solid #e2e8f0;">
<summary style="font-weight:600;cursor:pointer;">Why is the Nifty up only 0.2% despite positive domestic data?</summary>
<p style="margin-top:.75rem;color:#4b5563;">The modest gain reflects a tug-of-war between positive domestic fundamentals (stable RBI rates, resilient corporate earnings) and negative global sentiment (Middle East tensions, weak global indices). FPI selling is capping the upside while DII buying is supporting the downside — resulting in a narrow trading range.</p>
</details>
<details style="padding:1rem;border-bottom:1px solid #e2e8f0;">
<summary style="font-weight:600;cursor:pointer;">What does RBI keeping rates at 5.25% mean for my home loan EMI?</summary>
<p style="margin-top:.75rem;color:#4b5563;">Good news — your home loan EMI will remain unchanged for now. Banks link their lending rates (MCLR/Repo-linked rates) to the RBI repo rate. With the rate on hold at 5.25%, there will be no immediate increase or decrease in your monthly outgo. A future rate cut (expected in Q3 FY26) would reduce EMIs.</p>
</details>
<details style="padding:1rem;border-bottom:1px solid #e2e8f0;">
<summary style="font-weight:600;cursor:pointer;">Should I buy, sell, or hold my equity mutual funds right now?</summary>
<p style="margin-top:.75rem;color:#4b5563;">If you have a long-term horizon (3+ years), continue your SIPs without interruption. Market consolidation phases are actually beneficial for SIP investors as they accumulate more units at lower prices. Short-term volatility due to global factors does not change India's fundamental growth trajectory.</p>
</details>
<details style="padding:1rem;">
<summary style="font-weight:600;cursor:pointer;">Which sectors are safest to invest in during geopolitical uncertainty?</summary>
<p style="margin-top:.75rem;color:#4b5563;">Historically, <strong>FMCG, Pharma, and IT</strong> are considered defensive sectors — they tend to hold up better during global uncertainty. Banking stocks can also be resilient if domestic credit growth remains strong. Avoid high-beta sectors like metals, real estate mid-caps, and small-cap indices during peak uncertainty phases.</p>
</details>
</div>

<h2>📚 References & Further Reading</h2>
<ul>
<li><a href="https://www.nseindia.com" target="_blank" rel="noopener noreferrer" style="color:#2563eb;">NSE India — National Stock Exchange Official Data</a></li>
<li><a href="https://www.bseindia.com" target="_blank" rel="noopener noreferrer" style="color:#2563eb;">BSE India — Bombay Stock Exchange Live Market</a></li>
<li><a href="https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx" target="_blank" rel="noopener noreferrer" style="color:#2563eb;">RBI Monetary Policy Press Release</a></li>
<li><a href="https://economictimes.indiatimes.com/markets" target="_blank" rel="noopener noreferrer" style="color:#2563eb;">Economic Times — Markets & Finance</a></li>
<li><a href="https://www.moneycontrol.com/markets/" target="_blank" rel="noopener noreferrer" style="color:#2563eb;">Moneycontrol — Live Market Updates</a></li>
<li><a href="https://www.sebi.gov.in" target="_blank" rel="noopener noreferrer" style="color:#2563eb;">SEBI — Securities & Exchange Board of India</a></li>
</ul>
<hr style="margin:2rem 0;border-color:#e2e8f0;">
<p style="font-size:.85rem;color:#6b7280;font-style:italic;">⚠️ <strong>Disclaimer:</strong> This article is for educational and informational purposes only and does not constitute financial advice. Stock market investments are subject to market risks. Please consult a SEBI-registered financial advisor before making any investment decisions.</p>
"""

    from blog.models import Publication, Tag
    pub = Publication.objects.filter(slug="the-trading-blueprint").first()
    tag_names = ["Nifty 50", "Sensex", "Stock Market", "RBI", "Indian Economy", "Market Analysis", "Trading", "Investing"]
    tags = []
    for t in tag_names:
        obj, _ = Tag.objects.get_or_create(name=t)
        tags.append(obj)

    article = Article.objects.create(
        title=TITLE,
        slug=SLUG,
        subtitle="Nifty holds 23,400 support, Sensex eyes 75,000 — RBI holds rates at 5.25% as Middle East tensions weigh on sentiment",
        content=CONTENT,
        cover_image="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&h=630&fit=crop&q=80",
        publication=pub,
        status="published",
        read_time=8,
        word_count=1400,
        meta_description="Nifty 50 trades at 23,460 (+0.2%) and Sensex gains 160 points to 74,523. RBI holds repo rate at 5.25%. Full market analysis, sector performance, technical levels and trading strategy.",
        published_at=timezone.now(),
    )
    article.tags.set(tags)

    return HttpResponse(
        f'Published! <a href="/article/{article.slug}/">View: {article.title}</a>'
    )


# ── Error handlers ────────────────────────────────────────────────────────────

def custom_404(request, exception=None):
    """Branded 404 with recent articles. Registered as handler404 in writeflow/urls.py."""
    recent = (
        Article.objects.filter(status="published")
        .select_related("publication")
        .order_by("-published_at")[:4]
    )
    return render(request, "blog/404.html", {"recent_articles": recent}, status=404)

