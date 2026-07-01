import logging
import os
import re
from html import escape

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.contrib.syndication.views import Feed
from django.core.cache import cache
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.middleware.csrf import get_token
from django.db import transaction
from django.db.models import Count, F, Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.feedgenerator import Atom1Feed
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import DetailView, ListView

from .helpers import (
    bump_rate_counter,
    cache_or_set,
    check_rate_limit,
    get_client_ip,
    send_contact_emails,
    send_newsletter_welcome,
)
from .models import (
    Article,
    ArticleFeedback,
    ArticleRating,
    Comment,
    NewsletterSubscriber,
    Publication,
    ReadingHistory,
    Tag,
    UserProfile,
)

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
            profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
            ctx["bookmark_count"] = profile.bookmarks.count()
            ctx["featured_articles"] = cache_or_set(
                "featured_articles_3", 300,
                lambda: list(
                    Article.objects.filter(status="published")
                    .select_related("publication")
                    .prefetch_related("tags")
                    .order_by("-views")[:3]
                ),
            )

            # Member feeds — wrapped so a not-yet-migrated DB degrades gracefully
            # (rather than 500) in the brief window before migrate CI completes.
            try:
                # Continue reading — most-recently-read articles for this user
                ctx["continue_reading"] = list(
                    Article.objects.filter(
                        status="published",
                        reading_history__user=self.request.user,
                    )
                    .select_related("publication")
                    .order_by("-reading_history__last_read")[:4]
                )

                # "For You" — personalized by followed topics/publications,
                # falling back to the tags of what the user bookmarked / read.
                followed_tag_ids = set(profile.followed_tags.values_list("id", flat=True))
                followed_pub_ids = set(profile.followed_publications.values_list("id", flat=True))
                seed_tag_ids = set(
                    Tag.objects.filter(
                        Q(articles__bookmarked_by=profile)
                        | Q(articles__reading_history__user=self.request.user)
                    ).values_list("id", flat=True)
                )
                interest_tags = followed_tag_ids | seed_tag_ids
                read_ids = list(
                    self.request.user.reading_history.values_list("article_id", flat=True)
                )
                if interest_tags or followed_pub_ids:
                    ctx["for_you"] = list(
                        Article.objects.filter(status="published")
                        .filter(Q(tags__in=interest_tags) | Q(publication_id__in=followed_pub_ids))
                        .exclude(id__in=read_ids)
                        .select_related("publication")
                        .prefetch_related("tags")
                        .annotate(rel=Count("tags", filter=Q(tags__in=interest_tags)))
                        .order_by("-rel", "-published_at")
                        .distinct()[:6]
                    )
                ctx["following_count"] = len(followed_tag_ids) + len(followed_pub_ids)
            except Exception:
                logger.warning("Member feed unavailable (schema not migrated yet?)")
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
        # GFG-style topic sidebar: top topics within this publication
        tkey = f"topic_sidebar_v1_{self.publication.pk}"
        topic = cache.get(tkey)
        if topic is None:
            topic = {
                "pub": self.publication,
                "tags": list(
                    Tag.objects.filter(
                        articles__publication=self.publication,
                        articles__status="published",
                    )
                    .annotate(n=Count("articles"))
                    .order_by("-n")[:20]
                ),
            }
            cache.set(tkey, topic, 600)
        ctx["topic_pub"] = topic["pub"]
        ctx["topic_tags"] = topic["tags"]
        ctx["follow_pub"] = self.publication.slug
        if self.request.user.is_authenticated:
            try:
                profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
                ctx["is_following"] = profile.followed_publications.filter(
                    pk=self.publication.pk
                ).exists()
            except Exception:
                pass
        return ctx


class TagView(ListView):
    model = Article
    template_name = "blog/tag.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        tag_name = self.kwargs.get("tag_name") or self.request.GET.get("name", "")
        self.tag = get_object_or_404(Tag, name=tag_name)
        return (
            Article.objects.filter(status="published", tags=self.tag)
            .select_related("publication")
            .prefetch_related("tags")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tag"] = self.tag
        ctx["follow_tag"] = self.tag.name
        if self.request.user.is_authenticated:
            try:
                profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
                ctx["is_following"] = profile.followed_tags.filter(pk=self.tag.pk).exists()
            except Exception:
                pass
        return ctx


class SearchView(ListView):
    model = Article
    template_name = "blog/search.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        self.query = self.request.GET.get("q", "").strip()[:200]
        if self.query and len(self.query) >= 2:
            base = (
                Article.objects.filter(status="published")
                .select_related("publication")
                .prefetch_related("tags")
            )
            try:
                vector = (
                    SearchVector("title", weight="A")
                    + SearchVector("subtitle", weight="B")
                    + SearchVector("content", weight="C")
                )
                search_query = SearchQuery(self.query, search_type="websearch")
                results = (
                    base.annotate(search=vector, rank=SearchRank(vector, search_query))
                    .filter(search=search_query)
                    .order_by("-rank", "-published_at")
                )
                list(results[:1])
                return results
            except Exception as exc:
                logger.warning(
                    "Search full-text query failed; using icontains fallback: %s",
                    exc,
                    exc_info=True,
                )
                return base.filter(
                    Q(title__icontains=self.query)
                    | Q(subtitle__icontains=self.query)
                    | Q(content__icontains=self.query)
                ).order_by("-published_at")
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
            lambda: list(
                Tag.objects.annotate(
                    count=Count("articles", filter=Q(articles__status="published"))
                ).filter(count__gt=0).order_by("-count", "name")[:30]
            ),
        )
        ctx["all_tags"] = cache_or_set(
            "all_tags_counted", 300,
            lambda: list(
                Tag.objects.annotate(
                    count=Count("articles", filter=Q(articles__status="published"))
                ).filter(count__gt=0).order_by("name")
            ),
        )
        ctx["publications_with_counts"] = cache_or_set(
            "publications_with_counts", 300,
            lambda: list(
                Publication.objects.annotate(
                    article_count=Count("articles", filter=Q(articles__status="published"))
                ).order_by("name")
            ),
        )
        ctx["latest_articles"] = cache_or_set(
            "explore_latest_articles_6", 300,
            lambda: list(
                Article.objects.filter(status="published")
                .select_related("publication")
                .prefetch_related("tags")
                .order_by("-published_at")[:6]
            ),
        )
        ctx["total_articles"] = cache_or_set(
            "explore_total_articles", 300,
            lambda: Article.objects.filter(status="published").count(),
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
            # Track reading history for logged-in users (member feature).
            if request.user.is_authenticated:
                ReadingHistory.objects.update_or_create(
                    user=request.user, article=self.object
                )
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

        # GFG-style topic sidebar: top topics in this publication + more in section
        if article.publication:
            tkey = f"topic_sidebar_v1_{article.publication_id}"
            topic = cache.get(tkey)
            if topic is None:
                topic = {
                    "pub": article.publication,
                    "tags": list(
                        Tag.objects.filter(
                            articles__publication=article.publication,
                            articles__status="published",
                        )
                        .annotate(n=Count("articles"))
                        .order_by("-n")[:20]
                    ),
                }
                cache.set(tkey, topic, 600)
            ctx["topic_pub"] = topic["pub"]
            ctx["topic_tags"] = topic["tags"]
            ctx["topic_more"] = list(
                Article.objects.filter(
                    status="published", publication=article.publication
                ).exclude(id=article.id).order_by("-published_at")[:6]
            )

        # Evaluate comments once; reuse list for both display and count.
        # Defensive: if the schema is behind the code (e.g. Comment.user not yet
        # migrated in prod) degrade to no comments rather than 500 the page.
        try:
            comments = list(article.comments.filter(is_approved=True))
        except Exception:
            logger.warning("Comments unavailable (schema not migrated yet?)")
            comments = []
        ctx["comments"] = comments
        ctx["comment_count"] = len(comments)

        ctx["avg_rating"] = article.average_rating()
        ctx["rating_count"] = article.rating_count()
        ctx["user_rated"] = ArticleRating.objects.filter(
            article=article, ip_address=get_client_ip(self.request)
        ).exists()

        # "Was this helpful?" feedback state
        try:
            ctx["helpful_percent"] = article.helpful_percent()
            ctx["feedback_count"] = article.feedback_count()
            ctx["user_feedback"] = (
                ArticleFeedback.objects.filter(
                    article=article, ip_address=get_client_ip(self.request)
                ).values_list("helpful", flat=True).first()
            )
        except Exception:
            logger.warning("Feedback unavailable (schema not migrated yet?)")
            ctx["helpful_percent"] = 0
            ctx["feedback_count"] = 0
            ctx["user_feedback"] = None
        ctx["is_bookmarked"] = False
        if self.request.user.is_authenticated:
            try:
                profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
                ctx["is_bookmarked"] = profile.bookmarks.filter(pk=article.pk).exists()
            except Exception:
                logger.warning("Profile lookup unavailable (schema not migrated yet?)")

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
    content = escape(request.POST.get("content", "").strip()[:2000])

    # Logged-in members comment under their account name; anon must give a name.
    comment_user = None
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        name = escape(profile.shown_name[:100])
        comment_user = request.user
    else:
        name = escape(request.POST.get("name", "").strip()[:100])

    if not name or not content or len(name) < 2 or len(content) < 5:
        return JsonResponse(
            {"success": False, "error": "Name (2+ chars) and comment (5+ chars) are required."},
            status=400,
        )

    try:
        comment = Comment.objects.create(
            article=article, user=comment_user, name=name, content=content
        )
        bump_rate_counter(rate_key, 60)
        return JsonResponse({
            "success": True,
            "id": comment.id,
            "name": comment.name,
            "content": comment.content,
            "created_at": comment.created_at.strftime("%b %d, %Y %H:%M"),
            "owner": comment_user is not None,
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
    ip = get_client_ip(request)
    rate_key = f"newsletter_rate_{ip}"
    if check_rate_limit(rate_key, 20):
        return JsonResponse(
            {"success": False, "error": "Too many subscription attempts. Please try again later."},
            status=429,
        )
    bump_rate_counter(rate_key, 3600)

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


@require_GET
@ensure_csrf_cookie
def csrf_token(request):
    return JsonResponse({"success": True, "csrfToken": get_token(request)})


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

    try:
        sent = send_contact_emails(name, email, subject, message, ip)
    except Exception as exc:
        logger.error(
            "contact_submit: email delivery failed — %s: %s", type(exc).__name__, exc, exc_info=True
        )
        sent = False

    if not sent:
        return JsonResponse(
            {"success": False, "error": "Message delivery is temporarily unavailable. Please try again later."},
            status=503,
        )

    bump_rate_counter(rate_key, 3600)
    return JsonResponse({"success": True, "message": "Message sent! We'll reply within 1–2 business days."})


# ── Static pages ──────────────────────────────────────────────────────────────

def about_page(request):
    from .models import AUTHOR_PROFILES

    team = []
    for profile in AUTHOR_PROFILES.values():
        parts = profile["name"].split()
        team.append({**profile, "initials": "".join(p[0] for p in parts[:2]).upper()})
    return render(request, "blog/about.html", {"team": team})


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
    rate_key = f"rating_rate_{ip}"

    if check_rate_limit(rate_key, 60):
        return JsonResponse(
            {"success": False, "error": "Too many rating attempts. Please try again later."},
            status=429,
        )
    bump_rate_counter(rate_key, 3600)

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


# ── "Was this helpful?" feedback ──────────────────────────────────────────────

@require_POST
def article_feedback(request, slug):
    article = get_object_or_404(Article, slug=slug, status="published")
    ip = get_client_ip(request)
    rl_key = f"feedback_rate_{ip}"

    if check_rate_limit(rl_key, 30):
        return JsonResponse(
            {"success": False, "error": "Too many submissions. Please try again later."},
            status=429,
        )
    bump_rate_counter(rl_key, 3600)

    raw = (request.POST.get("helpful") or "").strip().lower()
    if raw not in ("1", "true", "yes", "0", "false", "no"):
        return JsonResponse({"success": False, "error": "Invalid feedback."}, status=400)
    helpful = raw in ("1", "true", "yes")

    comment = (request.POST.get("comment") or "").strip()[:280]

    try:
        with transaction.atomic():
            ArticleFeedback.objects.update_or_create(
                article=article, ip_address=ip,
                defaults={
                    "helpful": helpful,
                    "comment": comment,
                    "user": request.user if request.user.is_authenticated else None,
                },
            )
        return JsonResponse({
            "success": True,
            "helpful_percent": article.helpful_percent(),
            "feedback_count": article.feedback_count(),
        })
    except Exception:
        # Graceful fallback for read-only DB environments (mirrors rate_article)
        return JsonResponse({
            "success": True,
            "helpful_percent": 100 if helpful else 0,
            "feedback_count": 1,
        })


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
        ip = get_client_ip(request)
        rate_key = f"register_rate_{ip}"
        if check_rate_limit(rate_key, 10):
            return render(request, "blog/register.html", {
                "errors": ["Too many registration attempts. Please try again later."],
            }, status=429)
        bump_rate_counter(rate_key, 3600)

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
        ip = get_client_ip(request)
        rate_key = f"login_rate_{ip}"
        if check_rate_limit(rate_key, 20):
            return render(request, "blog/login.html", {
                "error": "Too many login attempts. Please try again later.",
            }, status=429)
        bump_rate_counter(rate_key, 900)

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get("next") or "/"
            if not url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                next_url = "/"
            return redirect(next_url)
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


# ── Member: follow topics / publications ─────────────────────────────────────

@login_required
@require_POST
def toggle_follow_tag(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    try:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if profile.followed_tags.filter(pk=tag.pk).exists():
            profile.followed_tags.remove(tag)
            following = False
        else:
            profile.followed_tags.add(tag)
            following = True
        return JsonResponse({"following": following, "tag": tag.name})
    except Exception:
        return JsonResponse({"error": "Following is temporarily unavailable."}, status=503)


@login_required
@require_POST
def toggle_follow_publication(request, slug):
    pub = get_object_or_404(Publication, slug=slug)
    try:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if profile.followed_publications.filter(pk=pub.pk).exists():
            profile.followed_publications.remove(pub)
            following = False
        else:
            profile.followed_publications.add(pub)
            following = True
        return JsonResponse({"following": following, "publication": pub.slug})
    except Exception:
        return JsonResponse({"error": "Following is temporarily unavailable."}, status=503)


# ── Member: profile ──────────────────────────────────────────────────────────

@login_required
def profile_view(request):
    try:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if request.method == "POST":
            profile.display_name = escape(request.POST.get("display_name", "").strip()[:80])
            profile.bio = escape(request.POST.get("bio", "").strip()[:300])
            profile.save()
            messages.success(request, "Profile updated.")
            return redirect("blog:profile")

        history = (
            Article.objects.filter(status="published", reading_history__user=request.user)
            .select_related("publication")
            .order_by("-reading_history__last_read")[:12]
        )
        followed_tags = list(profile.followed_tags.all())
        followed_publications = list(profile.followed_publications.all())
    except Exception:
        logger.warning("Profile unavailable (schema not migrated yet?)")
        messages.info(request, "Member profile is being set up — please check back soon.")
        return redirect("blog:home")
    return render(request, "blog/profile.html", {
        "profile": profile,
        "badges": profile.badges(),
        "bookmark_count": profile.bookmarks.count(),
        "history": history,
        "followed_tags": followed_tags,
        "followed_publications": followed_publications,
        "following_count": len(followed_tags) + len(followed_publications),
    })


# ── Member: delete own comment ───────────────────────────────────────────────

@login_required
@require_POST
def delete_comment(request, comment_id):
    try:
        comment = get_object_or_404(Comment, pk=comment_id)
        if comment.user_id != request.user.id and not request.user.is_staff:
            return JsonResponse({"success": False, "error": "Not allowed."}, status=403)
        comment.delete()
        return JsonResponse({"success": True})
    except Http404:
        return JsonResponse({"success": False, "error": "Not found."}, status=404)
    except Exception:
        return JsonResponse({"success": False, "error": "Temporarily unavailable."}, status=503)


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


# ── Error handlers ────────────────────────────────────────────────────────────

def custom_404(request, exception=None):
    """Branded 404 with recent articles. Registered as handler404 in writeflow/urls.py."""
    recent = (
        Article.objects.filter(status="published")
        .select_related("publication")
        .order_by("-published_at")[:4]
    )
    return render(request, "blog/404.html", {"recent_articles": recent}, status=404)
