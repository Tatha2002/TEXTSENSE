from rest_framework import serializers
from .models import TextAnalysis


class TextAnalysisSerializer(serializers.ModelSerializer):

    class Meta:
        model = TextAnalysis

        fields = [
            "id",
            "feedback",
            "sentiment",
            "confidence",
            "cleaned_text",
            "processed_text",
            "total_tokens",
            "unique_words",
            "analyzed_at",
        ]

        read_only_fields = fields