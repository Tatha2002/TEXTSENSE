from rest_framework import serializers
from .models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):

    class Meta:
        model = Feedback
        fields = [
            "id",
            "user",
            "title",
            "text",
            "category",
            "source",
            "status",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "user",
            # "status",
            "created_at",
        ]