
from rest_framework import serializers
from .models import Article
from django.utils.text import slugify


class ArticleSerializer(serializers.ModelSerializer):

    created_by_name = serializers.CharField(
        source="created_by.name",
        read_only=True
    )

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "meta_title",
            "meta_description",
            "status",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
            "published_at",
        ]

        read_only_fields = [
            "id",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
            "published_at",
        ]

    def validate(self, attrs):
        slug = attrs.get("slug")

        if not slug:
            slug = slugify(attrs.get("title", ""))

        queryset = Article.objects.filter(slug=slug)

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError({
                "slug": "An article with this slug already exists."
            })

        return attrs
