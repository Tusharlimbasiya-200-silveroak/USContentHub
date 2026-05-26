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
    name = models.CharField(max_length=100, unique=True)

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
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="published")
    read_time = models.PositiveIntegerField(default=3)
    word_count = models.PositiveIntegerField(default=0)
    meta_description = models.CharField(max_length=300, blank=True, default="")
    published_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:300]
        super().save(*args, **kwargs)
