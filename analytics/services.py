from django.db.models import Count
from feedback.models import Feedback
from text_analysis.models import TextAnalysis, Keyword


def get_dashboard_analytics(date_from=None, date_to=None):
    feedback_qs = Feedback.objects.all()
    analysis_qs = TextAnalysis.objects.all()

    if date_from:
        feedback_qs = feedback_qs.filter(created_at__date__gte=date_from)
        analysis_qs = analysis_qs.filter(feedback__created_at__date__gte=date_from)

    if date_to:
        feedback_qs = feedback_qs.filter(created_at__date__lte=date_to)
        analysis_qs = analysis_qs.filter(feedback__created_at__date__lte=date_to)

    total_feedback = feedback_qs.count()
    total_analyzed = analysis_qs.count()

    # Sentiment distribution
    sentiment_distribution = list(analysis_qs.values("sentiment").annotate(count=Count("id")).order_by("sentiment"))

    # Category-wise feedback
    category_distribution = list(feedback_qs.values("category__name").annotate(count=Count("id")).order_by("-count"))

    # Feedback status distribution
    status_distribution = list(feedback_qs.values("status").annotate(count=Count("id")).order_by("status"))

    # Top keywords
    keyword_qs = Keyword.objects.all()

    if date_from or date_to:
        keyword_qs = Keyword.objects.filter(feedbackkeyword__feedback__in=feedback_qs).distinct()

    top_keywords = list(keyword_qs.values("term", "frequency", "relevance").order_by("-frequency")[:10])

    return {
        "total_feedback": total_feedback,
        "total_analyzed": total_analyzed,
        "pending_analysis": total_feedback - total_analyzed,
        "sentiment_distribution": sentiment_distribution,
        "category_distribution": category_distribution,
        "status_distribution": status_distribution,
        "top_keywords": top_keywords,
    }
