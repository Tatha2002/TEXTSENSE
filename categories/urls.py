from django.urls import path
from .api_views import (
    CategoryListCreateAPIView,
    CategoryDetailAPIView,
)


urlpatterns = [
    path("", CategoryListCreateAPIView.as_view(), name="category-list"),
    path("create/", CategoryListCreateAPIView.as_view(), name="category-list-create"),
    path("details/<int:pk>/", CategoryDetailAPIView.as_view(), name="category-detail"),
]


# GET http://127.0.0.1:8000/textsense/category/
# POST http://127.0.0.1:8000/textsense/category/create/
# GET http://127.0.0.1:8000/textsense/category/details/1/
# PUT http://127.0.0.1:8000/textsense/category/details/1/
# PATCH http://127.0.0.1:8000/textsense/category/details/1/
# DELETE http://127.0.0.1:8000/textsense/category/details/1/