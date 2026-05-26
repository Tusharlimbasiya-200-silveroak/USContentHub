import re

from django.contrib.syndication.views import Feed
from django.db.models import Count, F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.feedgenerator import Atom1Feed
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
        ctx["popular_tags"] = Tag.objects.annotate(count=Count("articles")).order_by("-count")[:15]
        ctx["total_articles"] = Article.objects.filter(status="published").count()
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
        ctx["related"] = (
            Article.objects.filter(status="published", publication=article.publication)
            .exclude(id=article.id)
            .order_by("-published_at")[:3]
            if article.publication
            else Article.objects.filter(status="published").exclude(id=article.id).order_by("-published_at")[:3]
        )
        ctx["tags"] = article.tags.all()
        ctx["comments"] = article.comments.filter(is_approved=True)
        ctx["comment_count"] = ctx["comments"].count()
        return ctx


def add_comment(request, slug):
    if request.method == "POST":
        article = get_object_or_404(Article, slug=slug, status="published")
        name = request.POST.get("name", "").strip()[:100]
        content = request.POST.get("content", "").strip()[:2000]
        if name and content and len(name) >= 2 and len(content) >= 5:
            comment = Comment.objects.create(
                article=article,
                name=name,
                content=content,
            )
            return JsonResponse({
                "success": True,
                "name": comment.name,
                "content": comment.content,
                "created_at": comment.created_at.strftime("%b %d, %Y %H:%M"),
            })
        return JsonResponse({"success": False, "error": "Name and comment are required."}, status=400)
    return JsonResponse({"success": False, "error": "POST required."}, status=405)


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
        self.query = self.request.GET.get("q", "").strip()
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
        return Article.objects.filter(status="published").select_related("publication").prefetch_related("tags").order_by("-views")[:20]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["popular_tags"] = Tag.objects.annotate(count=Count("articles")).order_by("-count")[:30]
        ctx["all_tags"] = Tag.objects.annotate(count=Count("articles")).order_by("name")
        ctx["publications_with_counts"] = Publication.objects.annotate(article_count=Count("articles")).order_by("name")
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