from django.urls import path
from .api_views import (CategoryListCreateAPIView,CategoryDetailAPIView,)


urlpatterns = [
    
    path("create/", CategoryListCreateAPIView.as_view(), name="category-list-create"),
    path("details/<int:pk>/",CategoryDetailAPIView.as_view(),name="category-detail"),
]


# POST http://127.0.0.1:8000/textsense/category/create/
# POST http://127.0.0.1:8000/textsense/category/details/1/