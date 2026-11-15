from django.db import models
from feedback.models import Feedback


class TextAnalysis(models.Model):

    SENTIMENT_CHOICES = [
        ("Positive", "Positive"),
        ("Negative", "Negative"),
        ("Neutral", "Neutral"),
    ]

    feedback = models.OneToOneField(Feedback, on_delete=models.CASCADE, related_name="analysis")
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES)
    confidence = models.FloatField()
    cleaned_text = models.TextField(blank=True)
    processed_text = models.TextField(blank=True)
    total_tokens = models.PositiveIntegerField(default=0)
    unique_words = models.PositiveIntegerField(default=0)
    analyzed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.feedback.title} - {self.sentiment}"


class Keyword(models.Model):
    term = models.CharField(max_length=100, unique=True)
    frequency = models.PositiveIntegerField(default=0)
    relevance = models.FloatField(default=0.0)

    def __str__(self):
        return self.term


class FeedbackKeyword(models.Model):
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name="feedback_keywords")
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE, related_name="feedback_keywords")
    score = models.FloatField(default=0.0)

    class Meta:
        unique_together = ("feedback", "keyword")

    def __str__(self):
        return f"{self.feedback_id} - {self.keyword.term}"


# Note
# - TextAnalysis: stores sentiment, confidence and preprocessing results.
# - Keyword: stores unique keywords across feedback records.
# - FeedbackKeyword: connects individual feedback records to their keywords.
# The score field stores the frequency of a keyword in that particular feedback. Later, we can use it for keyword analytics.