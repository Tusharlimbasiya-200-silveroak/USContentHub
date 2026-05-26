from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.about_page, name="about"),
    path("contact/", views.contact_page, name="contact"),
    path("article/<slug:slug>/", views.ArticleDetailView.as_view(), name="article"),
    path("article/<slug:slug>/comment/", views.add_comment, name="add_comment"),
    path("pub/<slug:slug>/", views.PublicationView.as_view(), name="publication"),
    path("tag/<str:tag_name>/", views.TagView.as_view(), name="tag"),
    path("search/", views.SearchView.as_view(), name="search"),
    path("explore/", views.ExploreView.as_view(), name="explore"),
    path("reading-list/", views.ReadingListView.as_view(), name="reading_list"),
    path("feed/rss/", views.ArticleRSSFeed(), name="rss_feed"),
    path("feed/atom/", views.ArticleAtomFeed(), name="atom_feed"),
]
