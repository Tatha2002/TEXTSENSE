from rest_framework import serializers
from .models import Feedback
from django.core.exceptions import ObjectDoesNotExist


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



class MyFeedbackSerializer(serializers.ModelSerializer):

    category_name = serializers.CharField(source="category.name",read_only=True)

    sentiment = serializers.SerializerMethodField()
    confidence = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = [
            "id",
            "title",
            "text",
            "category",
            "category_name",
            "source",
            "status",
            "sentiment",
            "confidence",
            "created_at",
        ]

    def get_sentiment(self, obj):
        try:
            return obj.analysis.sentiment
        except ObjectDoesNotExist:
            return None

    def get_confidence(self, obj):
        try:
            return obj.analysis.confidence
        except ObjectDoesNotExist:
            return None



class RecentFeedbackSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name",read_only=True)
    sentiment = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = [
            "id",
            "title",
            "category_name",
            "status",
            "sentiment",
            "created_at",
        ]

    def get_sentiment(self, obj):
        try:
            return obj.analysis.sentiment
        except ObjectDoesNotExist:
            return None

