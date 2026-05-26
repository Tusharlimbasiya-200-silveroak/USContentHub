from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Publication(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True, default="")
    color = models.CharField(max_length=7, default="#2563eb")
    icon = models.CharField(max_length=10, default="📚")
    github_url = models.URLField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    STATUS_CHOICES = [("draft", "Draft"), ("published", "Published")]

    title = models.CharField(max_length=300)
    subtitle = models.CharField(max_length=500, blank=True, default="")
    slug = models.SlugField(max_length=300, unique=True)
    content = models.TextField()
    cover_image = models.URLField(max_length=500, blank=True, default="")
    publication = models.ForeignKey(
        Publication, on_delete=models.SET_NULL, null=True, blank=True, related_name="articles"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="articles")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="published", db_index=True)
    read_time = models.PositiveIntegerField(default=3)
    word_count = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0, db_index=True)
    meta_description = models.CharField(max_length=300, blank=True, default="")
    published_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at"]
        indexes = [
            models.Index(fields=["status", "-published_at"], name="idx_status_published"),
            models.Index(fields=["status", "-views"], name="idx_status_views"),
            models.Index(fields=["status", "publication", "-published_at"], name="idx_status_pub_date"),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:300]
        super().save(*args, **kwargs)


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=100)
    content = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_approved = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["article", "is_approved", "-created_at"], name="idx_comment_article"),
        ]

    def __str__(self):
        return f"{self.name} on {self.article.title[:30]}"
