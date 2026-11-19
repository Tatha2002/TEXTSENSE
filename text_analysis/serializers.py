from rest_framework import serializers
from .models import TextAnalysis


class TextAnalysisSerializer(serializers.ModelSerializer):

    feedback_id = serializers.IntegerField(source="feedback.id", read_only=True)

    keywords = serializers.SerializerMethodField()

    class Meta:
        model = TextAnalysis

        fields = [
            "feedback_id",
            "sentiment",
            "confidence",
            "scores",
            "keywords",
        ]

        read_only_fields = fields

    def get_keywords(self, obj):
        from .models import FeedbackKeyword

        keywords = FeedbackKeyword.objects.filter(
            feedback=obj.feedback
        ).select_related("keyword").order_by("-score")[:5]

        return [item.keyword.term for item in keywords]
