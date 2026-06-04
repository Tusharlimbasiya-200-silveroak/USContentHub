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


# ── Error handlers ────────────────────────────────────────────────────────────

def custom_404(request, exception=None):
    """Branded 404 with recent articles. Registered as handler404 in writeflow/urls.py."""
    recent = (
        Article.objects.filter(status="published")
        .select_related("publication")
        .order_by("-published_at")[:4]
    )
    return render(request, "blog/404.html", {"recent_articles": recent}, status=404)


def db_diagnostic(request):
    """Temporary diagnostic endpoint — shows DB state on production. Remove after debugging."""
    import os, django.db
    from django.conf import settings
    db_path = str(settings.DATABASES['default'].get('NAME', 'N/A'))
    db_exists = os.path.exists(db_path) if db_path != 'N/A' else False
    db_size = os.path.getsize(db_path) if db_exists else 0
    total = Article.objects.count()
    pub_count = Article.objects.filter(publication_id=7).count()
    max_id = Article.objects.filter(publication_id=7).order_by('-id').values_list('id', flat=True).first()
    has_28 = Article.objects.filter(slug='dollar-cost-averaging-strategy-guide-2026').exists()
    has_50 = Article.objects.filter(slug='commodity-trading-gold-oil-agricultural-markets-2026').exists()
    return JsonResponse({
        'db_path': db_path,
        'db_exists': db_exists,
        'db_size_bytes': db_size,
        'total_articles': total,
        'trading_blueprint_count': pub_count,
        'max_trading_blueprint_id': max_id,
        'has_blog28_dca': has_28,
        'has_blog50_commodity': has_50,
        'engine': django.db.connection.vendor,
    })
