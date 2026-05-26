from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Article, Comment, Publication, Tag


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
        self.assertContains(response, '"@type": "Article"')


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
        self.assertTemplateUsed(response, "blog/tag.html")

    def test_nonexistent_tag_404(self):
        response = self.client.get(reverse("blog:tag", args=["nonexistent-tag"]))
        self.assertEqual(response.status_code, 404)

    def test_tag_shows_correct_articles(self):
        response = self.client.get(reverse("blog:tag", args=["python"]))
        articles = response.context["articles"]
        self.assertEqual(len(articles), 2)

    def test_tag_shows_only_tagged_articles(self):
        response = self.client.get(reverse("blog:tag", args=["django"]))
        articles = response.context["articles"]
        self.assertEqual(len(articles), 1)


# ============================================================
# VIEW TESTS — Search
# ============================================================
class SearchViewTest(BaseTestCase):
    def test_search_page_loads(self):
        response = self.client.get(reverse("blog:search") + "?q=test")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/search.html")

    def test_search_finds_by_title(self):
        response = self.client.get(reverse("blog:search") + "?q=Test+Article")
        articles = response.context["articles"]
        self.assertGreater(len(articles), 0)

    def test_search_finds_by_content(self):
        response = self.client.get(reverse("blog:search") + "?q=paragraph")
        articles = response.context["articles"]
        self.assertGreater(len(articles), 0)

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
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(response.context["q"]), 200)


# ============================================================
# VIEW TESTS — Explore
# ============================================================
class ExploreViewTest(BaseTestCase):
    def test_explore_loads(self):
        response = self.client.get(reverse("blog:explore"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/explore.html")

    def test_explore_has_all_context(self):
        response = self.client.get(reverse("blog:explore"))
        self.assertIn("trending", response.context)
        self.assertIn("popular_tags", response.context)
        self.assertIn("all_tags", response.context)
        self.assertIn("publications_with_counts", response.context)


# ============================================================
# VIEW TESTS — Reading List
# ============================================================
class ReadingListViewTest(BaseTestCase):
    def test_empty_reading_list(self):
        response = self.client.get(reverse("blog:reading_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["articles"]), 0)

    def test_reading_list_with_slugs(self):
        response = self.client.get(reverse("blog:reading_list") + "?slugs=test-article-one,second-published")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["articles"]), 2)

    def test_reading_list_ignores_invalid_slugs(self):
        response = self.client.get(reverse("blog:reading_list") + "?slugs=nonexistent")
        self.assertEqual(len(response.context["articles"]), 0)

    def test_reading_list_max_100_slugs(self):
        slugs = ",".join([f"slug-{i}" for i in range(150)])
        response = self.client.get(reverse("blog:reading_list") + f"?slugs={slugs}")
        self.assertEqual(response.status_code, 200)


# ============================================================
# VIEW TESTS — RSS & Atom Feeds
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


# ============================================================
# PERFORMANCE / CACHING TESTS
# ============================================================
class CachingTest(BaseTestCase):
    def test_home_caches_popular_tags(self):
        self.client.get(reverse("blog:home"))
        cached = cache.get("popular_tags_15")
        self.assertIsNotNone(cached)

    def test_home_caches_total_count(self):
        self.client.get(reverse("blog:home"))
        cached = cache.get("total_published_articles")
        self.assertIsNotNone(cached)
        self.assertEqual(cached, 2)

    def test_explore_caches_trending(self):
        self.client.get(reverse("blog:explore"))
        cached = cache.get("explore_trending_20")
        self.assertIsNotNone(cached)

    def test_context_processor_caches_publications(self):
        self.client.get(reverse("blog:home"))
        cached = cache.get("all_publications")
        self.assertIsNotNone(cached)

    def test_article_detail_caches_related(self):
        self.client.get(reverse("blog:article", args=["test-article-one"]))
        cached = cache.get(f"related_articles_{self.article.pk}")
        self.assertIsNotNone(cached)


# ============================================================
# RESPONSE HEADER / MIDDLEWARE TESTS
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

    def test_base_has_google_translate(self):
        response = self.client.get(reverse("blog:home"))
        self.assertContains(response, "google_translate_element")

    def test_base_has_reading_progress(self):
        response = self.client.get(reverse("blog:home"))
        self.assertContains(response, "readingProgress")

    def test_base_has_rss_link(self):
        response = self.client.get(reverse("blog:home"))
        self.assertContains(response, "application/rss+xml")

    def test_base_has_reading_list_nav(self):
        response = self.client.get(reverse("blog:home"))
        self.assertContains(response, "reading-list")

    def test_base_has_theme_toggle(self):
        response = self.client.get(reverse("blog:home"))
        self.assertContains(response, "toggleTheme")


# ============================================================
# EDGE CASE / STRESS TESTS
# ============================================================
class EdgeCaseTest(BaseTestCase):
    def test_article_with_no_publication(self):
        a = Article.objects.create(
            title="No Pub Article", slug="no-pub", content="<p>test</p>",
            status="published", publication=None,
        )
        response = self.client.get(reverse("blog:article", args=["no-pub"]))
        self.assertEqual(response.status_code, 200)

    def test_article_with_no_tags(self):
        a = Article.objects.create(
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
