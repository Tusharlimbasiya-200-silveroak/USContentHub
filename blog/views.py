import re

from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView

from .models import Article, Publication, Tag


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
        return ctx


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
        return Article.objects.filter(status="published").select_related("publication").prefetch_related("tags")[:20]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["popular_tags"] = Tag.objects.annotate(count=Count("articles")).order_by("-count")[:30]
        return ctx