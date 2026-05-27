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
from django.db.models import Avg, Count, F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.feedgenerator import Atom1Feed
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, TemplateView

from .models import Article, ArticleRating, Comment, NewsletterSubscriber, Publication, Tag, UserProfile


class HomeView(ListView):
    model = Article
    template_name = "blog/home.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        return Article.objects.filter(status="published").select_related("publication").prefetch_related("tags")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        popular_tags = cache.get("popular_tags_15")
        if popular_tags is None:
            popular_tags = list(Tag.objects.annotate(count=Count("articles")).order_by("-count")[:15])
            cache.set("popular_tags_15", popular_tags, 300)
        ctx["popular_tags"] = popular_tags

        total = cache.get("total_published_articles")
        if total is None:
            total = Article.objects.filter(status="published").count()
            cache.set("total_published_articles", total, 300)
        ctx["total_articles"] = total
        return ctx


class ArticleDetailView(DetailView):
    model = Article
    template_name = "blog/article.html"
    context_object_name = "article"
    slug_field = "slug"

    def get_queryset(self):
        return Article.objects.filter(status="published").select_related("publication").prefetch_related("tags")

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        try:
            Article.objects.filter(pk=self.object.pk).update(views=F("views") + 1)
        except Exception:
            pass  # Read-only filesystem (e.g. Vercel) — view count increment is best-effort
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        article = self.object
        cache_key = f"related_articles_v2_{article.pk}"
        related = cache.get(cache_key)
        if related is None:
            tag_ids = list(article.tags.values_list("id", flat=True))
            if tag_ids:
                # Find articles sharing the most tags
                related = list(
                    Article.objects.filter(status="published", tags__in=tag_ids)
                    .exclude(id=article.id)
                    .annotate(shared_tags=Count("tags"))
                    .order_by("-shared_tags", "-published_at")
                    .distinct()[:6]
                )
            elif article.publication:
                related = list(
                    Article.objects.filter(status="published", publication=article.publication)
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
        ctx["comments"] = article.comments.filter(is_approved=True)
        ctx["comment_count"] = ctx["comments"].count()
        ctx["avg_rating"] = article.average_rating()
        ctx["rating_count"] = article.rating_count()
        # Check if current user has rated
        ip = _get_client_ip(self.request)
        ctx["user_rated"] = ArticleRating.objects.filter(article=article, ip_address=ip).exists()
        # Breadcrumbs
        ctx["breadcrumbs"] = [("Home", "/")]
        if article.publication:
            ctx["breadcrumbs"].append((article.publication.name, f"/pub/{article.publication.slug}/"))
        ctx["breadcrumbs"].append((article.title[:60], None))
        return ctx


@require_POST
def add_comment(request, slug):
    # Rate limiting: max 5 comments per IP per minute
    ip = _get_client_ip(request)
    rate_key = f"comment_rate_{ip}"
    count = cache.get(rate_key, 0)
    if count >= 5:
        return JsonResponse(
            {"success": False, "error": "Too many comments. Please wait a minute."},
            status=429,
        )

    article = get_object_or_404(Article, slug=slug, status="published")
    name = escape(request.POST.get("name", "").strip()[:100])
    content = escape(request.POST.get("content", "").strip()[:2000])

    if not name or not content or len(name) < 2 or len(content) < 5:
        return JsonResponse({"success": False, "error": "Name (2+ chars) and comment (5+ chars) are required."}, status=400)

    comment = Comment.objects.create(article=article, name=name, content=content)

    # Increment rate counter
    cache.set(rate_key, count + 1, 60)

    return JsonResponse({
        "success": True,
        "name": comment.name,
        "content": comment.content,
        "created_at": comment.created_at.strftime("%b %d, %Y %H:%M"),
    })


def _get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


class PublicationView(ListView):
    model = Article
    template_name = "blog/publication.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        self.publication = get_object_or_404(Publication, slug=self.kwargs["slug"])
        return Article.objects.filter(status="published", publication=self.publication).prefetch_related("tags")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["publication"] = self.publication
        ctx["total_articles"] = self.get_queryset().count()
        return ctx


class TagView(ListView):
    model = Article
    template_name = "blog/tag.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, name=self.kwargs["tag_name"])
        return Article.objects.filter(status="published", tags=self.tag).select_related("publication")

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
            return Article.objects.filter(
                Q(title__icontains=self.query) | Q(content__icontains=self.query) | Q(subtitle__icontains=self.query),
                status="published",
            ).select_related("publication")
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
        cache_key = "explore_trending_20"
        qs = cache.get(cache_key)
        if qs is None:
            qs = list(
                Article.objects.filter(status="published")
                .select_related("publication")
                .prefetch_related("tags")
                .order_by("-views")[:20]
            )
            cache.set(cache_key, qs, 300)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        popular_tags = cache.get("popular_tags_30")
        if popular_tags is None:
            popular_tags = list(Tag.objects.annotate(count=Count("articles")).order_by("-count")[:30])
            cache.set("popular_tags_30", popular_tags, 300)
        ctx["popular_tags"] = popular_tags

        all_tags = cache.get("all_tags_counted")
        if all_tags is None:
            all_tags = list(Tag.objects.annotate(count=Count("articles")).order_by("name"))
            cache.set("all_tags_counted", all_tags, 300)
        ctx["all_tags"] = all_tags

        pubs = cache.get("publications_with_counts")
        if pubs is None:
            pubs = list(Publication.objects.annotate(article_count=Count("articles")).order_by("name"))
            cache.set("publications_with_counts", pubs, 300)
        ctx["publications_with_counts"] = pubs
        return ctx


class ReadingListView(ListView):
    model = Article
    template_name = "blog/reading_list.html"
    context_object_name = "articles"

    def get_queryset(self):
        slugs_param = self.request.GET.get("slugs", "")
        if slugs_param:
            slugs = [s.strip() for s in slugs_param.split(",") if s.strip()][:100]
            return Article.objects.filter(status="published", slug__in=slugs).select_related("publication")
        return Article.objects.none()


class ArticleRSSFeed(Feed):
    title = "USA Content Hub"
    link = "/"
    description = "Latest articles on Tech, Health, Finance, Travel, Recipes & News"

    def items(self):
        return Article.objects.filter(status="published").order_by("-published_at")[:20]

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


def about_page(request):
    return render(request, "blog/about.html")


def contact_page(request):
    return render(request, "blog/contact.html")


def privacy_page(request):
    return render(request, "blog/privacy.html")


# ── Newsletter Subscribe ──────────────────────────────────────
@require_POST
def newsletter_subscribe(request):
    email = request.POST.get("email", "").strip().lower()[:254]
    if not email:
        return JsonResponse({"success": False, "error": "Email is required."}, status=400)
    try:
        validate_email(email)
    except Exception:
        return JsonResponse({"success": False, "error": "Invalid email address."}, status=400)

    subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
    if not created and subscriber.is_active:
        return JsonResponse({"success": True, "message": "You're already subscribed!"})
    if not subscriber.is_active:
        subscriber.is_active = True
        subscriber.save()
    return JsonResponse({"success": True, "message": "Successfully subscribed!"})


# ── Article Rating ─────────────────────────────────────────────
@require_POST
def rate_article(request, slug):
    article = get_object_or_404(Article, slug=slug, status="published")
    ip = _get_client_ip(request)

    try:
        score = int(request.POST.get("score", 0))
    except (ValueError, TypeError):
        return JsonResponse({"success": False, "error": "Invalid score."}, status=400)

    if score < 1 or score > 5:
        return JsonResponse({"success": False, "error": "Score must be between 1 and 5."}, status=400)

    rating, created = ArticleRating.objects.update_or_create(
        article=article, ip_address=ip,
        defaults={"score": score},
    )

    avg = article.average_rating()
    count = article.rating_count()
    return JsonResponse({"success": True, "avg_rating": avg, "rating_count": count, "your_score": score})


# ── Load More Articles (AJAX) ─────────────────────────────────
def load_more_articles(request):
    page = request.GET.get("page", 1)
    per_page = 12
    articles = Article.objects.filter(status="published").select_related("publication").prefetch_related("tags")
    paginator = Paginator(articles, per_page)

    try:
        page_obj = paginator.page(page)
    except Exception:
        return JsonResponse({"articles": [], "has_next": False})

    data = []
    for a in page_obj:
        data.append({
            "title": a.title,
            "slug": a.slug,
            "cover_image": a.cover_image,
            "published_at": a.published_at.strftime("%Y-%m-%d"),
            "read_time": a.read_time,
            "meta_description": a.meta_description or a.subtitle[:160] if a.subtitle else "",
            "publication_name": a.publication.name if a.publication else "",
            "publication_icon": a.publication.icon if a.publication else "",
            "publication_slug": a.publication.slug if a.publication else "",
        })
    return JsonResponse({"articles": data, "has_next": page_obj.has_next()})


# ── Auth Views ─────────────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect("blog:home")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()[:150]
        email = request.POST.get("email", "").strip().lower()[:254]
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        errors = []
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters.")
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
            return render(request, "blog/register.html", {"errors": errors, "username": username, "email": email})

        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, "Account created successfully!")
        return redirect("blog:home")
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
            next_url = request.GET.get("next", "/")
            return redirect(next_url)
        return render(request, "blog/login.html", {"error": "Invalid username or password.", "username": username})
    return render(request, "blog/login.html")


def logout_view(request):
    logout(request)
    return redirect("blog:home")


@login_required
@require_POST
def toggle_bookmark(request, slug):
    article = get_object_or_404(Article, slug=slug, status="published")
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if profile.bookmarks.filter(pk=article.pk).exists():
        profile.bookmarks.remove(article)
        return JsonResponse({"bookmarked": False})
    profile.bookmarks.add(article)
    return JsonResponse({"bookmarked": True})


@login_required
def user_bookmarks(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    articles = profile.bookmarks.filter(status="published").select_related("publication")
    return render(request, "blog/user_bookmarks.html", {"articles": articles})