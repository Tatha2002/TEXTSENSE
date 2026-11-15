from django.contrib import admin
from .models import TextAnalysis, Keyword, FeedbackKeyword


@admin.register(TextAnalysis)
class TextAnalysisAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "feedback",
        "sentiment",
        "confidence",
        "analyzed_at",
    )

    list_filter = ("sentiment", "analyzed_at")
    search_fields = ("feedback__title", "feedback__text")


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):

    list_display = ("id", "term", "frequency", "relevance")
    search_fields = ("term",)


@admin.register(FeedbackKeyword)
class FeedbackKeywordAdmin(admin.ModelAdmin):

    list_display = ("feedback", "keyword", "score")