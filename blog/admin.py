from django.contrib import admin

from .models import Article, Comment, Publication, Tag


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
    list_display = ("title", "publication", "status", "views", "read_time", "published_at")
    list_filter = ("status", "publication", "tags")
    search_fields = ("title", "content", "subtitle")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    date_hierarchy = "published_at"
    list_per_page = 25
    readonly_fields = ("views",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("name", "article", "is_approved", "created_at")
    list_filter = ("is_approved", "created_at")
    search_fields = ("name", "content")
    actions = ["approve_comments", "reject_comments"]

    @admin.action(description="Approve selected comments")
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description="Reject selected comments")
    def reject_comments(self, request, queryset):
        queryset.update(is_approved=False)