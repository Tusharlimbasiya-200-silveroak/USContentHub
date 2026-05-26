from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("article/<slug:slug>/", views.ArticleDetailView.as_view(), name="article"),
    path("pub/<slug:slug>/", views.PublicationView.as_view(), name="publication"),
    path("tag/<str:tag_name>/", views.TagView.as_view(), name="tag"),
    path("search/", views.SearchView.as_view(), name="search"),
    path("explore/", views.ExploreView.as_view(), name="explore"),
]
