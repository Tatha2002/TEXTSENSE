from django.urls import path
from .api_views import (ArticleListCreateAPIView, ArticleDetailAPIView,)

urlpatterns = [

    path("articles/", ArticleListCreateAPIView.as_view(), name="article-list-create"),
    path("articles/<slug:slug>/", ArticleDetailAPIView.as_view(), name="article-detail"),

]


# POST http://127.0.0.1:8000/textsense/content/articles/
# GET http://127.0.0.1:8000/textsense/content/articles/


# POST http://127.0.0.1:8000/textsense/content/articles/<slug>/
# GET http://127.0.0.1:8000/textsense/content/articles/<slug>/
# PUT http://127.0.0.1:8000/textsense/content/articles/<slug>/
# PATCH http://127.0.0.1:8000/textsense/content/articles/<slug>/
# DELETE http://127.0.0.1:8000/textsense/content/articles/<slug>/



