from django.contrib import admin

from .models import Article, Publication, Tag


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon", "created_at")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "publication", "status", "read_time", "published_at")
    list_filter = ("status", "publication", "tags")
    search_fields = ("title", "content", "subtitle")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    date_hierarchy = "published_at"
    list_per_page = 25