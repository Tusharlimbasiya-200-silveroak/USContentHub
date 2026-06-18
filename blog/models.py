import re

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from django.utils import timezone
from django.utils.text import slugify


class Publication(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True, default="")
    color = models.CharField(max_length=7, default="#2563eb")
    icon = models.CharField(max_length=10, default="📚")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.name


# Per-publication editorial bylines. Gives each article a consistent human
# author + bio (an E-E-A-T signal Google looks for) without a DB migration —
# these are derived from the article's publication at render time.
AUTHOR_PROFILES = {
    "tech-gadget-hub": {
        "name": "Marcus Reed",
        "role": "Technology Editor",
        "bio": "Marcus covers consumer tech, gadgets, and software, focusing on what new releases actually mean for everyday users.",
    },
    "health-wellness-daily": {
        "name": "Elena Brooks",
        "role": "Health & Wellness Editor",
        "bio": "Elena writes practical, evidence-aware wellness and lifestyle guidance. Her articles are informational and not a substitute for professional medical advice.",
    },
    "smart-money-guide": {
        "name": "Daniel Okafor",
        "role": "Personal Finance Editor",
        "bio": "Daniel breaks down budgeting, saving, and money decisions in plain language. His articles are educational and not personalized financial advice.",
    },
    "usa-travel-explorer": {
        "name": "Sofia Martinez",
        "role": "Travel Editor",
        "bio": "Sofia covers US destinations, trip planning, and travel tips with a focus on practical, real-world itineraries.",
    },
    "recipe-kitchen-usa": {
        "name": "Grace Bennett",
        "role": "Food Editor",
        "bio": "Grace develops and tests approachable recipes and kitchen guides for home cooks of every skill level.",
    },
    "usa-news-digest": {
        "name": "James Carter",
        "role": "News Editor",
        "bio": "James summarizes US news and current events, focusing on clear context over noise.",
    },
    "the-trading-blueprint": {
        "name": "Ryan Holt",
        "role": "Markets & Trading Editor",
        "bio": "Ryan covers markets, trading setups, and macro events. His articles are educational market commentary, not financial or investment advice.",
    },
    "tech-pulse": {
        "name": "Priya Nair",
        "role": "Tech News Editor",
        "bio": "Priya tracks AI, developer tooling, and the fast-moving tech landscape, translating releases into what they mean for builders.",
    },
}

DEFAULT_AUTHOR = {
    "name": "USA Content Hub Editorial Team",
    "role": "Editorial Team",
    "bio": "Researched, written, and edited by the USA Content Hub editorial team.",
}

# Publications whose articles must carry a "not financial advice" disclaimer.
FINANCIAL_PUBLICATIONS = {"the-trading-blueprint", "smart-money-guide"}


class Article(models.Model):
    STATUS_CHOICES = [("draft", "Draft"), ("published", "Published")]

    title = models.CharField(max_length=500)
    subtitle = models.CharField(max_length=500, blank=True, default="")
    slug = models.SlugField(max_length=300, unique=True)
    content = models.TextField()
    cover_image = models.URLField(max_length=500, blank=True, default="")
    video_url = models.URLField(max_length=500, blank=True, default="")
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

    def average_rating(self):
        result = self.ratings.aggregate(avg=Avg("score"))
        avg = result.get("avg")
        return round(avg, 1) if avg is not None else 0

    def rating_count(self):
        return self.ratings.count()

    def embed_video_url(self):
        """Convert YouTube/Vimeo URLs to embeddable format."""
        url = self.video_url
        if not url:
            return ""
        yt = re.match(r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)', url)
        if yt:
            return f"https://www.youtube.com/embed/{yt.group(1)}"
        vm = re.match(r'(?:https?://)?(?:www\.)?vimeo\.com/(\d+)', url)
        if vm:
            return f"https://player.vimeo.com/video/{vm.group(1)}"
        return url

    @property
    def author_profile(self):
        """Editorial byline (name/role/bio) derived from the publication."""
        slug = self.publication.slug if self.publication else ""
        return AUTHOR_PROFILES.get(slug, DEFAULT_AUTHOR)

    @property
    def author_initials(self):
        parts = self.author_profile["name"].split()
        return "".join(p[0] for p in parts[:2]).upper()

    @property
    def is_financial(self):
        """True when the article needs a 'not financial advice' disclaimer."""
        slug = self.publication.slug if self.publication else ""
        return slug in FINANCIAL_PUBLICATIONS


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="comments"
    )
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


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-subscribed_at"]

    def __str__(self):
        return self.email


class ArticleRating(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="ratings")
    ip_address = models.GenericIPAddressField()
    score = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("article", "ip_address")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.score}/5 on {self.article.title[:30]}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bookmarks = models.ManyToManyField(Article, blank=True, related_name="bookmarked_by")
    display_name = models.CharField(max_length=80, blank=True, default="")
    bio = models.CharField(max_length=300, blank=True, default="")
    followed_tags = models.ManyToManyField(Tag, blank=True, related_name="followers")
    followed_publications = models.ManyToManyField(
        Publication, blank=True, related_name="followers"
    )

    def __str__(self):
        return self.user.username

    @property
    def shown_name(self):
        return self.display_name or self.user.username

    def reads_count(self):
        return self.user.reading_history.count()

    def badges(self):
        """Simple reading badges/streaks computed from reading history."""
        from datetime import timedelta

        qs = self.user.reading_history.all()
        n = qs.count()
        out = []
        for threshold, label, icon in (
            (1, "First Read", "🌱"),
            (10, "Curious Reader", "📖"),
            (25, "Bookworm", "🐛"),
            (50, "Scholar", "🎓"),
            (100, "Knowledge Seeker", "🧠"),
        ):
            if n >= threshold:
                out.append({"label": label, "icon": icon})
        # day streak: distinct consecutive days ending today
        days = sorted({r.last_read.date() for r in qs}, reverse=True)
        streak = 0
        if days:
            today = timezone.now().date()
            cursor = today
            for d in days:
                if d == cursor:
                    streak += 1
                    cursor = cursor - timedelta(days=1)
                elif d < cursor:
                    break
        return {"earned": out, "reads": n, "streak": streak}


class ReadingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reading_history")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="reading_history")
    last_read = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        unique_together = ("user", "article")
        ordering = ["-last_read"]
        indexes = [
            models.Index(fields=["user", "-last_read"], name="idx_history_user"),
        ]

    def __str__(self):
        return f"{self.user.username} read {self.article.title[:30]}"
