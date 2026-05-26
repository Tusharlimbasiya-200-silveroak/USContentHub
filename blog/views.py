import re
from html import escape

from django.contrib.syndication.views import Feed
from django.core.cache import cache
from django.db.models import Count, F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.feedgenerator import Atom1Feed
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from .models import Article, Comment, Publication, Tag


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
        Article.objects.filter(pk=self.object.pk).update(views=F("views") + 1)
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        article = self.object
        cache_key = f"related_articles_{article.pk}"
        related = cache.get(cache_key)
        if related is None:
            related = list(
                Article.objects.filter(status="published", publication=article.publication)
                .exclude(id=article.id)
                .order_by("-published_at")[:3]
                if article.publication
                else Article.objects.filter(status="published").exclude(id=article.id).order_by("-published_at")[:3]
            )
            cache.set(cache_key, related, 600)
        ctx["related"] = related
        ctx["tags"] = article.tags.all()
        ctx["comments"] = article.comments.filter(is_approved=True)
        ctx["comment_count"] = ctx["comments"].count()
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