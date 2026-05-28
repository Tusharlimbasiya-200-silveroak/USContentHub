from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Article, ArticleRating, Comment, NewsletterSubscriber, Publication, Tag, UserProfile


class BaseTestCase(TestCase):
    """Shared setup for all test classes."""

    @classmethod
    def setUpTestData(cls):
        cls.pub = Publication.objects.create(
            name="Test Publication",
            slug="test-pub",
            description="A test publication",
            icon="🧪",
        )
        cls.tag1 = Tag.objects.create(name="python")
        cls.tag2 = Tag.objects.create(name="django")

        cls.article = Article.objects.create(
            title="Test Article One",
            slug="test-article-one",
            subtitle="A subtitle",
            content="<h2>Section 1</h2><p>Content paragraph one.</p>"
                    "<h2>Section 2</h2><p>Content paragraph two.</p>"
                    "<h2>Section 3</h2><p>Content paragraph three.</p>",
            publication=cls.pub,
            status="published",
            read_time=3,
            word_count=500,
            meta_description="Test meta description",
            cover_image="https://picsum.photos/1200/630",
        )
        cls.article.tags.add(cls.tag1, cls.tag2)

        cls.draft = Article.objects.create(
            title="Draft Article",
            slug="draft-article",
            content="<p>This is draft content.</p>",
            publication=cls.pub,
            status="draft",
            word_count=100,
        )

        cls.article2 = Article.objects.create(
            title="Second Published Article",
            slug="second-published",
            content="<p>Second article content for testing.</p>",
            publication=cls.pub,
            status="published",
            read_time=2,
            word_count=300,
            meta_description="Second article meta",
        )
        cls.article2.tags.add(cls.tag1)

    def setUp(self):
        cache.clear()


# ============================================================
# MODEL TESTS
# ============================================================
class PublicationModelTest(BaseTestCase):
    def test_str_representation(self):
        self.assertEqual(str(self.pub), "Test Publication")

    def test_slug_unique(self):
        with self.assertRaises(Exception):
            Publication.objects.create(name="Dupe", slug="test-pub")


class TagModelTest(BaseTestCase):
    def test_str_representation(self):
        self.assertEqual(str(self.tag1), "python")

    def test_unique_tag_name(self):
        with self.assertRaises(Exception):
            Tag.objects.create(name="python")


class ArticleModelTest(BaseTestCase):
    def test_str_representation(self):
        self.assertEqual(str(self.article), "Test Article One")

    def test_auto_slug_generation(self):
        a = Article.objects.create(title="Auto Slug Test", content="test", status="published")
        self.assertEqual(a.slug, "auto-slug-test")

    def test_ordering_by_published_at(self):
        articles = list(Article.objects.filter(status="published"))
        for i in range(len(articles) - 1):
            self.assertGreaterEqual(articles[i].published_at, articles[i + 1].published_at)

    def test_default_values(self):
        a = Article.objects.create(title="Defaults Test", slug="defaults-test", content="x")
        self.assertEqual(a.status, "published")
        self.assertEqual(a.read_time, 3)
        self.assertEqual(a.word_count, 0)
        self.assertEqual(a.views, 0)

    def test_slug_truncation(self):
        long_title = "A" * 400
        a = Article.objects.create(title=long_title, content="test")
        self.assertLessEqual(len(a.slug), 300)

    def test_average_rating_no_ratings(self):
        self.assertEqual(self.article.average_rating(), 0)

    def test_average_rating_with_ratings(self):
        ArticleRating.objects.create(article=self.article, ip_address="1.1.1.1", score=4)
        ArticleRating.objects.create(article=self.article, ip_address="2.2.2.2", score=5)
        self.assertEqual(self.article.average_rating(), 4.5)

    def test_rating_count(self):
        ArticleRating.objects.create(article=self.article, ip_address="1.1.1.1", score=3)
        self.assertEqual(self.article.rating_count(), 1)

    def test_embed_video_url_youtube(self):
        self.article.video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self.assertEqual(self.article.embed_video_url(), "https://www.youtube.com/embed/dQw4w9WgXcQ")

    def test_embed_video_url_youtu_be(self):
        self.article.video_url = "https://youtu.be/dQw4w9WgXcQ"
        self.assertEqual(self.article.embed_video_url(), "https://www.youtube.com/embed/dQw4w9WgXcQ")

    def test_embed_video_url_vimeo(self):
        self.article.video_url = "https://vimeo.com/123456"
        self.assertEqual(self.article.embed_video_url(), "https://player.vimeo.com/video/123456")

    def test_embed_video_url_empty(self):
        self.article.video_url = ""
        self.assertEqual(self.article.embed_video_url(), "")

    def test_video_url_field_default(self):
        a = Article.objects.create(title="No Video", slug="no-video", content="x")
        self.assertEqual(a.video_url, "")


class CommentModelTest(BaseTestCase):
    def test_str_representation(self):
        c = Comment.objects.create(article=self.article, name="John", content="Great article!")
        self.assertIn("John", str(c))
        self.assertIn("Test Article", str(c))

    def test_ordering_newest_first(self):
        c1 = Comment.objects.create(article=self.article, name="A", content="First comment")
        c2 = Comment.objects.create(article=self.article, name="B", content="Second comment")
        comments = list(Comment.objects.filter(article=self.article))
        self.assertEqual(comments[0].pk, c2.pk)

    def test_cascade_delete(self):
        Comment.objects.create(article=self.article, name="X", content="Test comment")
        self.assertEqual(Comment.objects.count(), 1)
        self.article.delete()
        self.assertEqual(Comment.objects.count(), 0)


class NewsletterModelTest(BaseTestCase):
    def test_str_representation(self):
        sub = NewsletterSubscriber.objects.create(email="test@example.com")
        self.assertEqual(str(sub), "test@example.com")

    def test_email_unique(self):
        NewsletterSubscriber.objects.create(email="unique@example.com")
        with self.assertRaises(Exception):
            NewsletterSubscriber.objects.create(email="unique@example.com")

    def test_default_active(self):
        sub = NewsletterSubscriber.objects.create(email="active@example.com")
        self.assertTrue(sub.is_active)


class ArticleRatingModelTest(BaseTestCase):
    def test_str_representation(self):
        r = ArticleRating.objects.create(article=self.article, ip_address="1.2.3.4", score=5)
        self.assertIn("5/5", str(r))

    def test_unique_per_ip_per_article(self):
        ArticleRating.objects.create(article=self.article, ip_address="1.1.1.1", score=3)
        with self.assertRaises(Exception):
            ArticleRating.objects.create(article=self.article, ip_address="1.1.1.1", score=4)

    def test_score_boundaries(self):
        r = ArticleRating.objects.create(article=self.article, ip_address="10.0.0.1", score=1)
        self.assertEqual(r.score, 1)
        r2 = ArticleRating.objects.create(article=self.article, ip_address="10.0.0.2", score=5)
        self.assertEqual(r2.score, 5)


class UserProfileModelTest(BaseTestCase):
    def test_profile_creation(self):
        user = User.objects.create_user("testuser", "test@test.com", "testpass123")
        profile = UserProfile.objects.create(user=user)
        self.assertEqual(str(profile), "testuser")

    def test_bookmarks(self):
        user = User.objects.create_user("bookmarker", "bm@test.com", "testpass123")
        profile = UserProfile.objects.create(user=user)
        profile.bookmarks.add(self.article)
        self.assertIn(self.article, profile.bookmarks.all())


# ============================================================
# VIEW TESTS — Home
# ============================================================
class HomeViewTest(BaseTestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse("blog:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/home.html")

    def test_home_shows_published_only(self):
        response = self.client.get(reverse("blog:home"))
        articles = response.context["articles"]
        for a in articles:
            self.assertEqual(a.status, "published")

    def test_home_excludes_drafts(self):
        response = self.client.get(reverse("blog:home"))
        slugs = [a.slug for a in response.context["articles"]]
        self.assertNotIn("draft-article", slugs)

    def test_home_has_total_count(self):
        response = self.client.get(reverse("blog:home"))
        self.assertIn("total_articles", response.context)
        self.assertEqual(response.context["total_articles"], 2)

    def test_home_has_popular_tags(self):
        response = self.client.get(reverse("blog:home"))
        self.assertIn("popular_tags", response.context)

    def test_home_pagination(self):
        for i in range(15):
            Article.objects.create(
                title=f"Pagination Article {i}", slug=f"pagination-{i}",
                content="test", status="published",
            )
        response = self.client.get(reverse("blog:home"))
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["articles"]), 12)

        response2 = self.client.get(reverse("blog:home") + "?page=2")
        self.assertEqual(response2.status_code, 200)


# ============================================================
# VIEW TESTS — Article Detail
# ============================================================
class ArticleDetailViewTest(BaseTestCase):
    def test_article_loads(self):
        response = self.client.get(reverse("blog:article", args=["test-article-one"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/article.html")

    def test_draft_returns_404(self):
        response = self.client.get(reverse("blog:article", args=["draft-article"]))
        self.assertEqual(response.status_code, 404)

    def test_nonexistent_article_404(self):
        response = self.client.get(reverse("blog:article", args=["does-not-exist"]))
        self.assertEqual(response.status_code, 404)

    def test_view_counter_increments(self):
        initial = Article.objects.get(pk=self.article.pk).views
        self.client.get(reverse("blog:article", args=["test-article-one"]))
        self.assertEqual(Article.objects.get(pk=self.article.pk).views, initial + 1)

    def test_view_counter_increments_multiple(self):
        initial = Article.objects.get(pk=self.article.pk).views
        for _ in range(5):
            self.client.get(reverse("blog:article", args=["test-article-one"]))
        self.assertEqual(Article.objects.get(pk=self.article.pk).views, initial + 5)

    def test_related_articles_in_context(self):
        response = self.client.get(reverse("blog:article", args=["test-article-one"]))
        self.assertIn("related", response.context)

    def test_related_excludes_self(self):
        response = self.client.get(reverse("blog:article", args=["test-article-one"]))
        related_ids = [a.id for a in response.context["related"]]
        self.assertNotIn(self.article.id, related_ids)

    def test_tags_in_context(self):
        response = self.client.get(reverse("blog:article", args=["test-article-one"]))
        self.assertIn("tags", response.context)

    def test_comments_in_context(self):
        response = self.client.get(reverse("blog:article", args=["test-article-one"]))
        self.assertIn("comments", response.context)
        self.assertIn("comment_count", response.context)

    def test_schema_json_in_response(self):
        response = self.client.get(reverse("blog:article", args=["test-article-one"]))
        self.assertContains(response, "application/ld+json")
        self.assertContains(response, '"@type": "NewsArticle"')

    def test_breadcrumbs_in_context(self):
        response = self.client.get(reverse("blog:article", args=["test-article-one"]))
        self.assertIn("breadcrumbs", response.context)
        breadcrumbs = response.context["breadcrumbs"]
        self.assertEqual(breadcrumbs[0][0], "Home")
        self.assertEqual(breadcrumbs[1][0], "Test Publication")

    def test_rating_data_in_context(self):
        response = self.client.get(reverse("blog:article", args=["test-article-one"]))
        self.assertIn("avg_rating", response.context)
        self.assertIn("rating_count", response.context)
        self.assertIn("user_rated", response.context)

    def test_print_button_in_template(self):
        response = self.client.get(reverse("blog:article", args=["test-article-one"]))
        self.assertContains(response, "window.print()")


# ============================================================
# VIEW TESTS — Comments
# ============================================================
class CommentViewTest(BaseTestCase):
    def test_post_valid_comment(self):
        response = self.client.post(
            reverse("blog:add_comment", args=["test-article-one"]),
            {"name": "Alice", "content": "This is a great article!"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["name"], "Alice")

    def test_comment_xss_escaped(self):
        response = self.client.post(
            reverse("blog:add_comment", args=["test-article-one"]),
            {"name": "<script>alert(1)</script>", "content": "Normal comment here"},
        )
        data = response.json()
        self.assertNotIn("<script>", data["name"])
        self.assertIn("&lt;script&gt;", data["name"])

    def test_comment_short_name_rejected(self):
        response = self.client.post(
            reverse("blog:add_comment", args=["test-article-one"]),
            {"name": "A", "content": "Valid content"},
        )
        self.assertEqual(response.status_code, 400)

    def test_comment_short_content_rejected(self):
        response = self.client.post(
            reverse("blog:add_comment", args=["test-article-one"]),
            {"name": "Alice", "content": "Hi"},
        )
        self.assertEqual(response.status_code, 400)

    def test_comment_empty_fields_rejected(self):
        response = self.client.post(
            reverse("blog:add_comment", args=["test-article-one"]),
            {"name": "", "content": ""},
        )
        self.assertEqual(response.status_code, 400)

    def test_get_method_rejected(self):
        response = self.client.get(reverse("blog:add_comment", args=["test-article-one"]))
        self.assertEqual(response.status_code, 405)

    def test_comment_on_nonexistent_article(self):
        response = self.client.post(
            reverse("blog:add_comment", args=["does-not-exist"]),
            {"name": "Alice", "content": "Valid comment here"},
        )
        self.assertEqual(response.status_code, 404)

    def test_comment_on_draft_rejected(self):
        response = self.client.post(
            reverse("blog:add_comment", args=["draft-article"]),
            {"name": "Alice", "content": "Valid comment here"},
        )
        self.assertEqual(response.status_code, 404)

    def test_comment_rate_limiting(self):
        url = reverse("blog:add_comment", args=["test-article-one"])
        for i in range(5):
            self.client.post(url, {"name": f"User{i}", "content": f"Comment number {i} here"})
        response = self.client.post(url, {"name": "Spammer", "content": "One more comment"})
        self.assertEqual(response.status_code, 429)

    def test_approved_comments_visible(self):
        Comment.objects.create(article=self.article, name="Visible", content="I am approved", is_approved=True)
        Comment.objects.create(article=self.article, name="Hidden", content="I am hidden", is_approved=False)
        response = self.client.get(reverse("blog:article", args=["test-article-one"]))
        comments = response.context["comments"]
        names = [c.name for c in comments]
        self.assertIn("Visible", names)
        self.assertNotIn("Hidden", names)

    def test_content_truncated_at_2000(self):
        long_content = "x" * 3000
        response = self.client.post(
            reverse("blog:add_comment", args=["test-article-one"]),
            {"name": "Truncator", "content": long_content},
        )
        self.assertEqual(response.status_code, 200)
        c = Comment.objects.filter(name="Truncator").first()
        self.assertLessEqual(len(c.content), 2000)


# ============================================================
# VIEW TESTS — Newsletter
# ============================================================
class NewsletterViewTest(BaseTestCase):
    def test_subscribe_valid_email(self):
        response = self.client.post(
            reverse("blog:newsletter_subscribe"),
            {"email": "hello@example.com"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertTrue(NewsletterSubscriber.objects.filter(email="hello@example.com").exists())

    def test_subscribe_invalid_email(self):
        response = self.client.post(
            reverse("blog:newsletter_subscribe"),
            {"email": "notanemail"},
        )
        self.assertEqual(response.status_code, 400)

    def test_subscribe_empty_email(self):
        response = self.client.post(
            reverse("blog:newsletter_subscribe"),
            {"email": ""},
        )
        self.assertEqual(response.status_code, 400)

    def test_subscribe_duplicate(self):
        self.client.post(reverse("blog:newsletter_subscribe"), {"email": "dup@example.com"})
        response = self.client.post(reverse("blog:newsletter_subscribe"), {"email": "dup@example.com"})
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("already", data["message"])

    def test_subscribe_reactivate(self):
        sub = NewsletterSubscriber.objects.create(email="inactive@example.com", is_active=False)
        response = self.client.post(reverse("blog:newsletter_subscribe"), {"email": "inactive@example.com"})
        sub.refresh_from_db()
        self.assertTrue(sub.is_active)

    def test_get_method_rejected(self):
        response = self.client.get(reverse("blog:newsletter_subscribe"))
        self.assertEqual(response.status_code, 405)

    def test_csrf_required(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(reverse("blog:newsletter_subscribe"), {"email": "x@y.com"})
        self.assertEqual(response.status_code, 403)


# ============================================================
# VIEW TESTS — Rating
# ============================================================
class RatingViewTest(BaseTestCase):
    def test_rate_valid(self):
        response = self.client.post(
            reverse("blog:rate_article", args=["test-article-one"]),
            {"score": 4},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["your_score"], 4)
        self.assertEqual(data["rating_count"], 1)

    def test_rate_invalid_score_zero(self):
        response = self.client.post(
            reverse("blog:rate_article", args=["test-article-one"]),
            {"score": 0},
        )
        self.assertEqual(response.status_code, 400)

    def test_rate_invalid_score_six(self):
        response = self.client.post(
            reverse("blog:rate_article", args=["test-article-one"]),
            {"score": 6},
        )
        self.assertEqual(response.status_code, 400)

    def test_rate_invalid_score_text(self):
        response = self.client.post(
            reverse("blog:rate_article", args=["test-article-one"]),
            {"score": "abc"},
        )
        self.assertEqual(response.status_code, 400)

    def test_rate_updates_on_second_attempt(self):
        url = reverse("blog:rate_article", args=["test-article-one"])
        self.client.post(url, {"score": 3})
        self.client.post(url, {"score": 5})
        rating = ArticleRating.objects.get(article=self.article, ip_address="127.0.0.1")
        self.assertEqual(rating.score, 5)

    def test_rate_nonexistent_article(self):
        response = self.client.post(
            reverse("blog:rate_article", args=["nonexistent"]),
            {"score": 3},
        )
        self.assertEqual(response.status_code, 404)

    def test_rate_draft_rejected(self):
        response = self.client.post(
            reverse("blog:rate_article", args=["draft-article"]),
            {"score": 3},
        )
        self.assertEqual(response.status_code, 404)

    def test_get_method_rejected(self):
        response = self.client.get(reverse("blog:rate_article", args=["test-article-one"]))
        self.assertEqual(response.status_code, 405)


# ============================================================
# VIEW TESTS — Load More (API)
# ============================================================
class LoadMoreViewTest(BaseTestCase):
    def test_load_more_page_1(self):
        response = self.client.get(reverse("blog:load_more") + "?page=1")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("articles", data)
        self.assertIn("has_next", data)

    def test_load_more_returns_articles(self):
        response = self.client.get(reverse("blog:load_more") + "?page=1")
        data = response.json()
        self.assertGreater(len(data["articles"]), 0)
        article = data["articles"][0]
        self.assertIn("title", article)
        self.assertIn("slug", article)
        self.assertIn("cover_image", article)

    def test_load_more_invalid_page(self):
        response = self.client.get(reverse("blog:load_more") + "?page=9999")
        data = response.json()
        self.assertEqual(data["articles"], [])
        self.assertFalse(data["has_next"])


# ============================================================
# VIEW TESTS — Static Pages
# ============================================================
class StaticPagesTest(BaseTestCase):
    def test_about_page(self):
        response = self.client.get(reverse("blog:about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "About")

    def test_contact_page(self):
        response = self.client.get(reverse("blog:contact"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Contact")

    def test_privacy_page(self):
        response = self.client.get(reverse("blog:privacy"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Privacy")


# ============================================================
# VIEW TESTS — Auth
# ============================================================
class AuthViewTest(BaseTestCase):
    def test_register_page_loads(self):
        response = self.client.get(reverse("blog:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/register.html")

    def test_register_valid(self):
        response = self.client.post(reverse("blog:register"), {
            "username": "newuser", "email": "new@example.com",
            "password": "strongpass123", "password2": "strongpass123",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertTrue(UserProfile.objects.filter(user__username="newuser").exists())

    def test_register_password_mismatch(self):
        response = self.client.post(reverse("blog:register"), {
            "username": "newuser2", "email": "new2@example.com",
            "password": "strongpass123", "password2": "wrongpass123",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser2").exists())

    def test_register_short_password(self):
        response = self.client.post(reverse("blog:register"), {
            "username": "shortpw", "email": "sp@example.com",
            "password": "short", "password2": "short",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="shortpw").exists())

    def test_register_duplicate_username(self):
        User.objects.create_user("taken", "taken@example.com", "testpass123")
        response = self.client.post(reverse("blog:register"), {
            "username": "taken", "email": "new3@example.com",
            "password": "strongpass123", "password2": "strongpass123",
        })
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        response = self.client.get(reverse("blog:login"))
        self.assertEqual(response.status_code, 200)

    def test_login_valid(self):
        User.objects.create_user("loginuser", "l@example.com", "testpass123")
        response = self.client.post(reverse("blog:login"), {
            "username": "loginuser", "password": "testpass123",
        })
        self.assertEqual(response.status_code, 302)

    def test_login_invalid(self):
        response = self.client.post(reverse("blog:login"), {
            "username": "noone", "password": "wrong",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid")

    def test_logout(self):
        User.objects.create_user("logoutuser", "lo@test.com", "testpass123")
        self.client.login(username="logoutuser", password="testpass123")
        response = self.client.get(reverse("blog:logout"))
        self.assertEqual(response.status_code, 302)

    def test_register_redirect_if_logged_in(self):
        User.objects.create_user("existing", "ex@test.com", "testpass123")
        self.client.login(username="existing", password="testpass123")
        response = self.client.get(reverse("blog:register"))
        self.assertEqual(response.status_code, 302)

    def test_login_redirect_if_logged_in(self):
        User.objects.create_user("existing2", "ex2@test.com", "testpass123")
        self.client.login(username="existing2", password="testpass123")
        response = self.client.get(reverse("blog:login"))
        self.assertEqual(response.status_code, 302)


# ============================================================
# VIEW TESTS — Bookmarks (auth required)
# ============================================================
class BookmarkViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user("bmuser", "bm@test.com", "testpass123")
        UserProfile.objects.create(user=self.user)

    def test_bookmark_requires_login(self):
        response = self.client.post(reverse("blog:toggle_bookmark", args=["test-article-one"]))
        self.assertEqual(response.status_code, 302)  # redirect to login

    def test_bookmark_add(self):
        self.client.login(username="bmuser", password="testpass123")
        response = self.client.post(reverse("blog:toggle_bookmark", args=["test-article-one"]))
        data = response.json()
        self.assertTrue(data["bookmarked"])

    def test_bookmark_remove(self):
        self.client.login(username="bmuser", password="testpass123")
        self.client.post(reverse("blog:toggle_bookmark", args=["test-article-one"]))
        response = self.client.post(reverse("blog:toggle_bookmark", args=["test-article-one"]))
        data = response.json()
        self.assertFalse(data["bookmarked"])

    def test_bookmarks_page_loads(self):
        self.client.login(username="bmuser", password="testpass123")
        response = self.client.get(reverse("blog:user_bookmarks"))
        self.assertEqual(response.status_code, 200)

    def test_bookmarks_page_requires_login(self):
        response = self.client.get(reverse("blog:user_bookmarks"))
        self.assertEqual(response.status_code, 302)


# ============================================================
# VIEW TESTS — Publication
# ============================================================
class PublicationViewTest(BaseTestCase):
    def test_publication_page_loads(self):
        response = self.client.get(reverse("blog:publication", args=["test-pub"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/publication.html")

    def test_nonexistent_publication_404(self):
        response = self.client.get(reverse("blog:publication", args=["no-pub"]))
        self.assertEqual(response.status_code, 404)

    def test_shows_only_published(self):
        response = self.client.get(reverse("blog:publication", args=["test-pub"]))
        for a in response.context["articles"]:
            self.assertEqual(a.status, "published")


# ============================================================
# VIEW TESTS — Tag
# ============================================================
class TagViewTest(BaseTestCase):
    def test_tag_page_loads(self):
        response = self.client.get(reverse("blog:tag", args=["python"]))
        self.assertEqual(response.status_code, 200)

    def test_nonexistent_tag_404(self):
        response = self.client.get(reverse("blog:tag", args=["nonexistent-tag"]))
        self.assertEqual(response.status_code, 404)

    def test_tag_shows_correct_articles(self):
        response = self.client.get(reverse("blog:tag", args=["python"]))
        self.assertEqual(len(response.context["articles"]), 2)

    def test_tag_shows_only_tagged_articles(self):
        response = self.client.get(reverse("blog:tag", args=["django"]))
        self.assertEqual(len(response.context["articles"]), 1)


# ============================================================
# VIEW TESTS — Search
# ============================================================
class SearchViewTest(BaseTestCase):
    def test_search_page_loads(self):
        response = self.client.get(reverse("blog:search") + "?q=test")
        self.assertEqual(response.status_code, 200)

    def test_search_finds_by_title(self):
        response = self.client.get(reverse("blog:search") + "?q=Test+Article")
        self.assertGreater(len(response.context["articles"]), 0)

    def test_search_finds_by_content(self):
        response = self.client.get(reverse("blog:search") + "?q=paragraph")
        self.assertGreater(len(response.context["articles"]), 0)

    def test_search_ignores_short_query(self):
        response = self.client.get(reverse("blog:search") + "?q=x")
        self.assertEqual(len(response.context["articles"]), 0)

    def test_search_empty_query(self):
        response = self.client.get(reverse("blog:search") + "?q=")
        self.assertEqual(len(response.context["articles"]), 0)

    def test_search_excludes_drafts(self):
        response = self.client.get(reverse("blog:search") + "?q=Draft")
        slugs = [a.slug for a in response.context["articles"]]
        self.assertNotIn("draft-article", slugs)

    def test_search_query_truncated(self):
        long_q = "a" * 500
        response = self.client.get(reverse("blog:search") + f"?q={long_q}")
        self.assertLessEqual(len(response.context["q"]), 200)


# ============================================================
# VIEW TESTS — Explore / Reading List
# ============================================================
class ExploreViewTest(BaseTestCase):
    def test_explore_loads(self):
        response = self.client.get(reverse("blog:explore"))
        self.assertEqual(response.status_code, 200)

    def test_explore_has_all_context(self):
        response = self.client.get(reverse("blog:explore"))
        self.assertIn("trending", response.context)
        self.assertIn("popular_tags", response.context)
        self.assertIn("all_tags", response.context)
        self.assertIn("publications_with_counts", response.context)


class ReadingListViewTest(BaseTestCase):
    def test_empty_reading_list(self):
        response = self.client.get(reverse("blog:reading_list"))
        self.assertEqual(len(response.context["articles"]), 0)

    def test_reading_list_with_slugs(self):
        response = self.client.get(reverse("blog:reading_list") + "?slugs=test-article-one,second-published")
        self.assertEqual(len(response.context["articles"]), 2)

    def test_reading_list_ignores_invalid_slugs(self):
        response = self.client.get(reverse("blog:reading_list") + "?slugs=nonexistent")
        self.assertEqual(len(response.context["articles"]), 0)

    def test_reading_list_max_100_slugs(self):
        slugs = ",".join([f"slug-{i}" for i in range(150)])
        response = self.client.get(reverse("blog:reading_list") + f"?slugs={slugs}")
        self.assertEqual(response.status_code, 200)


# ============================================================
# VIEW TESTS — Feeds
# ============================================================
class FeedTest(BaseTestCase):
    def test_rss_feed_loads(self):
        response = self.client.get(reverse("blog:rss_feed"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/rss+xml", response["Content-Type"])

    def test_rss_contains_articles(self):
        response = self.client.get(reverse("blog:rss_feed"))
        self.assertContains(response, "Test Article One")

    def test_atom_feed_loads(self):
        response = self.client.get(reverse("blog:atom_feed"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/atom+xml", response["Content-Type"])

    def test_atom_contains_articles(self):
        response = self.client.get(reverse("blog:atom_feed"))
        self.assertContains(response, "Test Article One")


# ============================================================
# SITEMAP TESTS
# ============================================================
class SitemapTest(BaseTestCase):
    def test_sitemap_loads(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertIn("xml", response["Content-Type"])

    def test_sitemap_contains_articles(self):
        response = self.client.get("/sitemap.xml")
        self.assertContains(response, "/article/test-article-one/")

    def test_sitemap_contains_static_pages(self):
        response = self.client.get("/sitemap.xml")
        self.assertContains(response, "/about/")
        self.assertContains(response, "/privacy/")

    def test_sitemap_excludes_drafts(self):
        response = self.client.get("/sitemap.xml")
        self.assertNotContains(response, "/article/draft-article/")


# ============================================================
# SECURITY TESTS
# ============================================================
class SecurityTest(BaseTestCase):
    def test_csrf_on_comment(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(
            reverse("blog:add_comment", args=["test-article-one"]),
            {"name": "Hacker", "content": "CSRF attack attempt"},
        )
        self.assertEqual(response.status_code, 403)

    def test_xss_in_search_query(self):
        response = self.client.get(reverse("blog:search") + "?q=<script>alert(1)</script>")
        self.assertNotContains(response, "<script>alert(1)</script>")

    def test_sql_injection_in_search(self):
        response = self.client.get(reverse("blog:search") + "?q=' OR 1=1 --")
        self.assertEqual(response.status_code, 200)

    def test_path_traversal_slug(self):
        response = self.client.get("/article/../../../etc/passwd/")
        self.assertIn(response.status_code, [400, 404])

    def test_comment_html_injection(self):
        self.client.post(
            reverse("blog:add_comment", args=["test-article-one"]),
            {"name": "Test", "content": '<img src=x onerror="alert(1)">'},
        )
        c = Comment.objects.filter(name="Test").first()
        self.assertNotIn("<img", c.content)

    def test_newsletter_xss(self):
        response = self.client.post(
            reverse("blog:newsletter_subscribe"),
            {"email": '<script>alert(1)</script>@evil.com'},
        )
        self.assertEqual(response.status_code, 400)


# ============================================================
# CACHING TESTS
# ============================================================
class CachingTest(BaseTestCase):
    def test_home_caches_popular_tags(self):
        self.client.get(reverse("blog:home"))
        self.assertIsNotNone(cache.get("popular_tags_15"))

    def test_home_caches_total_count(self):
        self.client.get(reverse("blog:home"))
        self.assertEqual(cache.get("total_published_articles"), 2)

    def test_explore_caches_trending(self):
        self.client.get(reverse("blog:explore"))
        self.assertIsNotNone(cache.get("explore_trending_20"))

    def test_context_processor_caches_publications(self):
        self.client.get(reverse("blog:home"))
        self.assertIsNotNone(cache.get("all_publications"))

    def test_article_detail_caches_related(self):
        self.client.get(reverse("blog:article", args=["test-article-one"]))
        self.assertIsNotNone(cache.get(f"related_articles_v2_{self.article.pk}"))


# ============================================================
# MIDDLEWARE TESTS
# ============================================================
class MiddlewareTest(BaseTestCase):
    def test_x_frame_options_header(self):
        response = self.client.get(reverse("blog:home"))
        self.assertIn(response.get("X-Frame-Options", ""), ["DENY", "SAMEORIGIN"])

    def test_content_type_is_html(self):
        response = self.client.get(reverse("blog:home"))
        self.assertIn("text/html", response["Content-Type"])


# ============================================================
# URL ROUTING TESTS
# ============================================================
class URLTest(BaseTestCase):
    def test_home_url(self):
        self.assertEqual(reverse("blog:home"), "/")

    def test_article_url(self):
        self.assertEqual(reverse("blog:article", args=["test-slug"]), "/article/test-slug/")

    def test_publication_url(self):
        self.assertEqual(reverse("blog:publication", args=["test-pub"]), "/pub/test-pub/")

    def test_tag_url(self):
        self.assertEqual(reverse("blog:tag", args=["python"]), "/tag/python/")

    def test_search_url(self):
        self.assertEqual(reverse("blog:search"), "/search/")

    def test_explore_url(self):
        self.assertEqual(reverse("blog:explore"), "/explore/")

    def test_reading_list_url(self):
        self.assertEqual(reverse("blog:reading_list"), "/reading-list/")

    def test_rss_url(self):
        self.assertEqual(reverse("blog:rss_feed"), "/feed/rss/")

    def test_atom_url(self):
        self.assertEqual(reverse("blog:atom_feed"), "/feed/atom/")

    def test_comment_url(self):
        self.assertEqual(reverse("blog:add_comment", args=["my-slug"]), "/article/my-slug/comment/")

    def test_newsletter_url(self):
        self.assertEqual(reverse("blog:newsletter_subscribe"), "/newsletter/subscribe/")

    def test_rate_url(self):
        self.assertEqual(reverse("blog:rate_article", args=["my-slug"]), "/article/my-slug/rate/")

    def test_privacy_url(self):
        self.assertEqual(reverse("blog:privacy"), "/privacy/")

    def test_register_url(self):
        self.assertEqual(reverse("blog:register"), "/accounts/register/")

    def test_login_url(self):
        self.assertEqual(reverse("blog:login"), "/accounts/login/")

    def test_logout_url(self):
        self.assertEqual(reverse("blog:logout"), "/accounts/logout/")

    def test_load_more_url(self):
        self.assertEqual(reverse("blog:load_more"), "/api/articles/")

    def test_bookmark_url(self):
        self.assertEqual(reverse("blog:toggle_bookmark", args=["slug"]), "/article/slug/bookmark/")

    def test_bookmarks_url(self):
        self.assertEqual(reverse("blog:user_bookmarks"), "/accounts/bookmarks/")


# ============================================================
# TEMPLATE CONTENT TESTS
# ============================================================
class TemplateTest(BaseTestCase):
    def test_home_has_nav(self):
        response = self.client.get(reverse("blog:home"))
        self.assertContains(response, "USA Content Hub")
        self.assertContains(response, "platform-bar")

    def test_article_has_share_buttons(self):
        response = self.client.get(reverse("blog:article", args=["test-article-one"]))
        self.assertContains(response, "Share this article")
        self.assertContains(response, "twitter.com")
        self.assertContains(response, "facebook.com")
        self.assertContains(response, "linkedin.com")

    def test_article_has_bookmark_button(self):
        response = self.client.get(reverse("blog:article", args=["test-article-one"]))
        self.assertContains(response, "bookmarkBtn")

    def test_article_has_comment_form(self):
        response = self.client.get(reverse("blog:article", args=["test-article-one"]))
        self.assertContains(response, "commentForm")

    def test_article_has_view_count(self):
        response = self.client.get(reverse("blog:article", args=["test-article-one"]))
        self.assertContains(response, "views")

    def test_article_has_toc_container(self):
        response = self.client.get(reverse("blog:article", args=["test-article-one"]))
        self.assertContains(response, "tocContainer")

    def test_article_has_rating_section(self):
        response = self.client.get(reverse("blog:article", args=["test-article-one"]))
        self.assertContains(response, "ratingStars")
        self.assertContains(response, "Rate This Article")

    def test_article_has_breadcrumbs(self):
        response = self.client.get(reverse("blog:article", args=["test-article-one"]))
        self.assertContains(response, "breadcrumbs")
        self.assertContains(response, "Home")

    def test_article_has_print_button(self):
        response = self.client.get(reverse("blog:article", args=["test-article-one"]))
        self.assertContains(response, "Print")

    def test_base_has_reading_progress(self):
        response = self.client.get(reverse("blog:home"))
        self.assertContains(response, "readingProgress")

    def test_base_has_rss_link(self):
        response = self.client.get(reverse("blog:home"))
        self.assertContains(response, "application/rss+xml")

    def test_base_has_theme_toggle(self):
        response = self.client.get(reverse("blog:home"))
        self.assertContains(response, "toggleTheme")

    def test_base_has_social_links(self):
        response = self.client.get(reverse("blog:home"))
        self.assertContains(response, "footer-social")
        self.assertContains(response, "twitter.com")
        self.assertContains(response, "facebook.com")

    def test_base_has_newsletter_form(self):
        response = self.client.get(reverse("blog:home"))
        self.assertContains(response, "footerNewsletter")
        self.assertContains(response, "subscribeNewsletter")

    def test_base_has_privacy_link(self):
        response = self.client.get(reverse("blog:home"))
        self.assertContains(response, "Privacy")

    def test_base_has_auth_links(self):
        response = self.client.get(reverse("blog:home"))
        self.assertContains(response, "Login")
        self.assertContains(response, "Register")

    def test_base_has_auth_links_logged_in(self):
        User.objects.create_user("tmpluser", "t@t.com", "testpass123")
        self.client.login(username="tmpluser", password="testpass123")
        response = self.client.get(reverse("blog:home"))
        self.assertContains(response, "Logout")

    def test_print_css_exists(self):
        response = self.client.get(reverse("blog:home"))
        self.assertContains(response, "@media print")

    def test_home_has_load_more(self):
        for i in range(15):
            Article.objects.create(title=f"LM {i}", slug=f"lm-{i}", content="t", status="published")
        response = self.client.get(reverse("blog:home"))
        self.assertContains(response, "loadMoreBtn")


# ============================================================
# EDGE CASE TESTS
# ============================================================
class EdgeCaseTest(BaseTestCase):
    def test_article_with_no_publication(self):
        Article.objects.create(
            title="No Pub Article", slug="no-pub", content="<p>test</p>",
            status="published", publication=None,
        )
        response = self.client.get(reverse("blog:article", args=["no-pub"]))
        self.assertEqual(response.status_code, 200)

    def test_article_with_no_tags(self):
        Article.objects.create(
            title="No Tag Article", slug="no-tag", content="<p>test</p>",
            status="published",
        )
        response = self.client.get(reverse("blog:article", args=["no-tag"]))
        self.assertEqual(response.status_code, 200)

    def test_search_with_special_characters(self):
        response = self.client.get(reverse("blog:search") + "?q=%25%26%3D")
        self.assertEqual(response.status_code, 200)

    def test_reading_list_with_empty_slugs(self):
        response = self.client.get(reverse("blog:reading_list") + "?slugs=,,,")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["articles"]), 0)

    def test_high_page_number_returns_404(self):
        response = self.client.get(reverse("blog:home") + "?page=9999")
        self.assertEqual(response.status_code, 404)

    def test_invalid_page_number(self):
        response = self.client.get(reverse("blog:home") + "?page=abc")
        self.assertEqual(response.status_code, 404)

    def test_concurrent_view_increments(self):
        """Verify F() expression handles concurrent updates safely."""
        initial = Article.objects.get(pk=self.article.pk).views
        for _ in range(20):
            self.client.get(reverse("blog:article", args=["test-article-one"]))
        final = Article.objects.get(pk=self.article.pk).views
        self.assertEqual(final, initial + 20)

    def test_article_with_video(self):
        a = Article.objects.create(
            title="Video Article", slug="video-test", content="<p>test</p>",
            status="published", video_url="https://www.youtube.com/watch?v=abc123",
        )
        response = self.client.get(reverse("blog:article", args=["video-test"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "youtube.com/embed/abc123")
