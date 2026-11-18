
from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):

    feedback_count = serializers.SerializerMethodField()

    class Meta:
        model = Category

        fields = [
            "id",
            "name",
            "description",
            "active",
            "feedback_count",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "feedback_count",
            "created_at",
            "updated_at",
        ]

    def get_feedback_count(self, obj):
        return obj.feedbacks.count()
