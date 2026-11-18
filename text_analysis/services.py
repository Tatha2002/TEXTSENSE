
from django.db import transaction
from django.db.models import Sum, Count

from feedback.preprocessing import analyze_feedback
from feedback.predict import predict_sentiment_details

from .models import TextAnalysis, Keyword, FeedbackKeyword
from notifications.services import create_notification


def get_analysis_result(analysis):
    keywords = FeedbackKeyword.objects.filter(
        feedback=analysis.feedback
    ).select_related("keyword").order_by("-score")[:5]

    return {
        "feedback_id": analysis.feedback_id,
        "sentiment": analysis.sentiment,
        "confidence": analysis.confidence,
        "scores": analysis.scores,
        "keywords": [item.keyword.term for item in keywords],
    }


@transaction.atomic
def analyze_and_save_feedback(feedback):

    # 1. Check whether analysis already exists
    existing_analysis = TextAnalysis.objects.filter(feedback=feedback).first()

    if existing_analysis:
        return get_analysis_result(existing_analysis)

    # 2. Perform NLTK analysis
    nlp_result = analyze_feedback(feedback.text)
    processed_text = nlp_result["processed_text"]

    # 3. Predict sentiment
    prediction = predict_sentiment_details(feedback.text, processed_text=processed_text)

    # 4. Convert probability percentages into decimal scores
    scores = {
        label: round(probability / 100, 4)
        for label, probability in prediction["probabilities"].items()
    }

    confidence = round(prediction["confidence"] / 100, 4)

    # 5. Save analysis
    analysis = TextAnalysis.objects.create(
        feedback=feedback,
        sentiment=prediction["sentiment"],
        confidence=confidence,
        scores=scores,
        cleaned_text=nlp_result["cleaned_text"],
        processed_text=processed_text,
        total_tokens=nlp_result["total_tokens"],
        unique_words=nlp_result["unique_words"],
    )

    # 6. Save keyword associations
    frequencies = nlp_result["word_frequencies"]

    for term, count in frequencies.items():
        keyword, _ = Keyword.objects.get_or_create(term=term)

        FeedbackKeyword.objects.update_or_create(
            feedback=feedback,
            keyword=keyword,
            defaults={"score": float(count)}
        )

        aggregate = FeedbackKeyword.objects.filter(keyword=keyword).aggregate(
            total=Sum("score"),
            feedback_count=Count("id")
        )

        total_frequency = aggregate["total"] or 0
        feedback_count = aggregate["feedback_count"] or 1

        keyword.frequency = int(total_frequency)
        keyword.relevance = round(total_frequency / feedback_count, 4)
        keyword.save(update_fields=["frequency", "relevance"])

    # 7. Create notification
    create_notification(
        user=feedback.user,
        message="Your feedback analysis has been completed successfully.",
        notification_type="ANALYSIS_COMPLETED"
    )

    return get_analysis_result(analysis)
