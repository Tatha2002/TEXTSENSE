from django.utils import timezone

from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Article
from .serializers import ArticleSerializer
from categories.permissions import IsTextSenseAdmin


class ArticleListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and (
            user.is_superuser or
            user.role in ["SUPER_USER", "REACT_ADMIN"]
        ):
            return Article.objects.all().order_by("-created_at")

        return Article.objects.filter(status="PUBLISHED").order_by("-published_at")

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        return [IsTextSenseAdmin()]

    def perform_create(self, serializer):
        article = serializer.save(created_by=self.request.user)

        if article.status == "PUBLISHED":
            article.published_at = timezone.now()
            article.save(update_fields=["published_at"])


class ArticleDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ArticleSerializer
    lookup_field = "slug"

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and (
            user.is_superuser or
            user.role in ["SUPER_USER", "REACT_ADMIN"]
        ):
            return Article.objects.all()

        return Article.objects.filter(status="PUBLISHED")

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        return [IsTextSenseAdmin()]

    def perform_update(self, serializer):
        old_status = self.get_object().status
        article = serializer.save()

        if article.status == "PUBLISHED" and old_status != "PUBLISHED":
            article.published_at = timezone.now()
            article.save(update_fields=["published_at"])



