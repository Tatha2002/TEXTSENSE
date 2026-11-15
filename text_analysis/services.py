from django.db import transaction
from django.db.models import Sum, Count

from feedback.preprocessing import analyze_feedback
from feedback.predict import predict_sentiment_details

from .models import TextAnalysis, Keyword, FeedbackKeyword
from notifications.services import create_notification


@transaction.atomic
def analyze_and_save_feedback(feedback):

    # 1. Perform NLTK analysis
    nlp_result = analyze_feedback(feedback.text)

    processed_text = nlp_result["processed_text"]

    # 2. Predict sentiment using saved TF-IDF + Logistic Regression
    prediction = predict_sentiment_details(
        feedback.text,
        processed_text=processed_text
    )

    # 3. Save sentiment analysis
    analysis, created = TextAnalysis.objects.update_or_create(
        feedback=feedback,
        defaults={
            "sentiment": prediction["sentiment"],
            "confidence": prediction["confidence"],
            "cleaned_text": nlp_result["cleaned_text"],
            "processed_text": processed_text,
            "total_tokens": nlp_result["total_tokens"],
            "unique_words": nlp_result["unique_words"],
        }
    )

    # 4. Save keyword associations
    frequencies = nlp_result["word_frequencies"]

    for term, count in frequencies.items():

        keyword, _ = Keyword.objects.get_or_create(
            term=term
        )

        FeedbackKeyword.objects.update_or_create(
            feedback=feedback,
            keyword=keyword,
            defaults={
                "score": float(count)
            }
        )

        # Recalculate aggregate keyword statistics
        aggregate = FeedbackKeyword.objects.filter(
            keyword=keyword
        ).aggregate(
            total=Sum("score"),
            feedback_count=Count("id")
        )

        total_frequency = aggregate["total"] or 0
        feedback_count = aggregate["feedback_count"] or 1

        keyword.frequency = int(total_frequency)
        keyword.relevance = round(
            total_frequency / feedback_count,
            4
        )
        keyword.save(update_fields=["frequency", "relevance"])

    # 5. Prepare compact API response
    top_keywords = [
        term
        for term, count in sorted(
            frequencies.items(),
            key=lambda item: item[1],
            reverse=True
        )[:5]
    ]

    create_notification(
        user=feedback.user,
        message="Your feedback analysis has been completed successfully.",
        notification_type="ANALYSIS_COMPLETED"
    )

    return {
        "sentiment": analysis.sentiment,
        "confidence": analysis.confidence,
        "important_keywords": top_keywords,
    }