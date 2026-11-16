from django.db.models import Count
from django.contrib.auth import get_user_model
from categories.models import Category
from feedback.models import Feedback
from text_analysis.models import TextAnalysis, Keyword

User = get_user_model()

def get_user_analytics():
    return {
        "total_users": User.objects.filter(role=User.REACT_USER,is_superuser=False).count(),
        "total_admins": User.objects.filter(role=User.REACT_ADMIN,is_superuser=False).count(),
        "total_superusers": User.objects.filter(is_superuser=True).count(),
    }


def get_feedback_analytics(date_from=None, date_to=None):
    feedback_qs = Feedback.objects.select_related("user", "category", "analysis").all()

    if date_from:
        feedback_qs = feedback_qs.filter(created_at__date__gte=date_from)

    if date_to:
        feedback_qs = feedback_qs.filter(created_at__date__lte=date_to)

    feedback_details: list = []

    for feedback in feedback_qs.order_by("-created_at"):
        analysis = getattr(feedback, "analysis", None)

        feedback_details.append({
            "id": feedback.id,
            "title": feedback.title,
            "text": feedback.text,
            "user": {
                "id": feedback.user.id,
                "name": feedback.user.name,
                "email": feedback.user.email,
                "role": feedback.user.role,
            },
            "category": {
                "id": feedback.category.id,
                "name": feedback.category.name,
            },
            "source": feedback.source,
            "status": feedback.status,
            "sentiment": analysis.sentiment if analysis else None,
            "confidence": analysis.confidence if analysis else None,
            "created_at": feedback.created_at,
        })

    return {
        "total_feedback": feedback_qs.count(),
        "feedback_details": feedback_details,
    }


def get_category_analytics():
    categories = Category.objects.annotate(feedback_count=Count("feedbacks")).order_by("name")

    category_details: list = []

    for category in categories:
        category_details.append({
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "active": category.active,
            "feedback_count": category.feedback_count,
            "created_at": category.created_at,
        })

    return {
        "total_categories": categories.count(),
        "active_categories": categories.filter(active=True).count(),
        "inactive_categories": categories.filter(active=False).count(),
        "categories": category_details,
    }


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

    sentiment_distribution = list(analysis_qs.values("sentiment").annotate(count=Count("id")).order_by("sentiment"))
    category_distribution = list(feedback_qs.values("category__name").annotate(count=Count("id")).order_by("-count"))
    status_distribution = list(feedback_qs.values("status").annotate(count=Count("id")).order_by("status"))

    keyword_qs = Keyword.objects.all()

    if date_from or date_to:keyword_qs = Keyword.objects.filter(feedback_keywords__feedback__in=feedback_qs).distinct()

    top_keywords = list(keyword_qs.values("term", "frequency", "relevance").order_by("-frequency")[:10])

    user_analytics = get_user_analytics()
    category_analytics = get_category_analytics()

    return {
        **user_analytics,
        "total_feedback": total_feedback,
        "total_categories": category_analytics["total_categories"],
        "total_analyzed": total_analyzed,
        "pending_analysis": total_feedback - total_analyzed,
        "sentiment_distribution": sentiment_distribution,
        "category_distribution": category_distribution,
        "status_distribution": status_distribution,
        "top_keywords": top_keywords,
    }



