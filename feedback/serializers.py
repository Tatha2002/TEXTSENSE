from rest_framework import serializers
from .models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):

    user_name = serializers.CharField(source="user.name", read_only=True)
    category_name = serializers.CharField(source="category.name",read_only=True)

    class Meta:
        model = Feedback

        fields = [
            "id",
            "user",
            "user_name",
            "title",
            "text",
            "category",
            "category_name",
            "source",
            "status",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "user_name",
            "category_name",
            "status",
            "created_at",
        ]
