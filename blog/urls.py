from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.about_page, name="about"),
    path("contact/", views.contact_page, name="contact"),
    path("contact/submit/", views.contact_submit, name="contact_submit"),
    path("privacy/", views.privacy_page, name="privacy"),
    # Pinterest domain verification
    path("pinterest-0fd9e.html", views.pinterest_verify, name="pinterest_verify"),
    path("article/<slug:slug>/", views.ArticleDetailView.as_view(), name="article"),
    path("article/<slug:slug>/comment/", views.add_comment, name="add_comment"),
    path("article/<slug:slug>/rate/", views.rate_article, name="rate_article"),
    path("article/<slug:slug>/feedback/", views.article_feedback, name="article_feedback"),
    path("article/<slug:slug>/bookmark/", views.toggle_bookmark, name="toggle_bookmark"),
    path("comment/<int:comment_id>/delete/", views.delete_comment, name="delete_comment"),
    path("pub/<slug:slug>/", views.PublicationView.as_view(), name="publication"),
    path("tag/", views.TagView.as_view(), name="tag_query"),
    path("tag/<path:tag_name>/", views.TagView.as_view(), name="tag"),
    path("search/", views.SearchView.as_view(), name="search"),
    path("explore/", views.ExploreView.as_view(), name="explore"),
    path("reading-list/", views.ReadingListView.as_view(), name="reading_list"),
    path("newsletter/subscribe/", views.newsletter_subscribe, name="newsletter_subscribe"),
    path("csrf/", views.csrf_token, name="csrf_token"),
    path("api/articles/", views.load_more_articles, name="load_more"),
    # ── Custom Auth (takes precedence over allauth for these paths) ──
    path("accounts/register/", views.register_view, name="register"),
    path("accounts/login/", views.login_view, name="login"),
    path("accounts/logout/", views.logout_view, name="logout"),
    path("accounts/bookmarks/", views.user_bookmarks, name="user_bookmarks"),
    path("accounts/profile/", views.profile_view, name="profile"),
    path("follow/tag/<path:tag_name>/", views.toggle_follow_tag, name="follow_tag"),
    path("follow/pub/<slug:slug>/", views.toggle_follow_publication, name="follow_publication"),
    # ── Pinterest OAuth (one-time setup — remove after tokens saved) ──
    path("otp/pinterest-connect/", views.pinterest_connect, name="pinterest_connect"),
    path("otp/pinterest-callback/", views.pinterest_callback, name="pinterest_callback"),
    # ── Global RSS / Atom feeds ──
    path("feed/rss/", views.ArticleRSSFeed(), name="rss_feed"),
    path("feed/atom/", views.ArticleAtomFeed(), name="atom_feed"),
    # ── Per-publication RSS / Atom feeds ──
    path("feed/pub/<slug:slug>/rss/", views.PublicationRSSFeed(), name="pub_rss_feed"),
    path("feed/pub/<slug:slug>/atom/", views.PublicationAtomFeed(), name="pub_atom_feed"),
]
