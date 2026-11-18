from django.db.models import Count, Sum, Q
from django.contrib.auth import get_user_model
from categories.models import Category
from feedback.models import Feedback
from text_analysis.models import TextAnalysis, Keyword, FeedbackKeyword

from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from calendar import monthrange


User = get_user_model()

def get_user_analytics():
    User = get_user_model()
    today = timezone.localdate()
    month_start = today.replace(day=1)
    week_start = today - timedelta(days=6)

    users = User.objects.filter(role=User.REACT_USER, is_superuser=False)

    weekly_stats = list(
        users.filter(date_joined__date__gte=week_start)
        .annotate(date=TruncDate("date_joined"))
        .values("date")
        .annotate(count=Count("id"))
        .order_by("date")
    )

    return {
        "total_users": users.count(),
        "active_users": users.count(),
        "new_users_this_month": users.filter(date_joined__date__gte=month_start).count(),
        "weekly_user_statistics": weekly_stats,
        "total_admins": User.objects.filter(role=User.REACT_ADMIN, is_superuser=False).count(),
        "total_superusers": User.objects.filter(is_superuser=True).count(),
    }


def get_feedback_analytics(date_from=None, date_to=None):
    feedback_qs = Feedback.objects.select_related("user", "category", "analysis").all()

    if date_from:
        feedback_qs = feedback_qs.filter(created_at__date__gte=date_from)

    if date_to:
        feedback_qs = feedback_qs.filter(created_at__date__lte=date_to)

    total_feedback = feedback_qs.count()
    reviewed_feedback = feedback_qs.filter(status__in=["REVIEWED", "RESOLVED"]).count()
    pending_feedback = feedback_qs.filter(status__in=["NEW", "PENDING"]).count()

    sentiment_distribution = list(
        feedback_qs.filter(analysis__isnull=False)
        .values("analysis__sentiment")
        .annotate(count=Count("id"))
        .order_by("analysis__sentiment")
    )

    feedback_details = []

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
        "total_feedback": total_feedback,
        "reviewed_feedback": reviewed_feedback,
        "pending_feedback": pending_feedback,
        "sentiment_distribution": sentiment_distribution,
        "feedback_details": feedback_details,
    }


def get_category_analytics():
    categories = Category.objects.annotate(feedback_count=Count("feedbacks")).order_by("name")

    category_details = []

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
        "uncategorized_feedback": Feedback.objects.filter(category__isnull=True).count(),
        "categories": category_details,
    }


def get_dashboard_analytics(date_from=None, date_to=None):
    feedback_qs = Feedback.objects.all()
    analysis_qs = TextAnalysis.objects.all()
    User = get_user_model()

    if date_from:
        feedback_qs = feedback_qs.filter(created_at__date__gte=date_from)
        analysis_qs = analysis_qs.filter(feedback__created_at__date__gte=date_from)

    if date_to:
        feedback_qs = feedback_qs.filter(created_at__date__lte=date_to)
        analysis_qs = analysis_qs.filter(feedback__created_at__date__lte=date_to)

    total_feedback = feedback_qs.count()
    total_analyzed = analysis_qs.count()

    sentiment_counts = {
        "Positive": analysis_qs.filter(sentiment="Positive").count(),
        "Negative": analysis_qs.filter(sentiment="Negative").count(),
        "Neutral": analysis_qs.filter(sentiment="Neutral").count(),
    }

    sentiment_percentages = {
        key.lower(): round((value / total_analyzed) * 100, 2) if total_analyzed else 0
        for key, value in sentiment_counts.items()
    }

    sentiment_distribution = list(
        analysis_qs.values("sentiment").annotate(count=Count("id")).order_by("sentiment")
    )

    category_distribution = list(
        feedback_qs.values("category__name").annotate(count=Count("id")).order_by("-count")
    )

    status_distribution = list(
        feedback_qs.values("status").annotate(count=Count("id")).order_by("status")
    )

    feedback_trends = list(
        feedback_qs.annotate(date=TruncDate("created_at"))
        .values("date").annotate(count=Count("id")).order_by("date")
    )

    user_qs = User.objects.filter(role=User.REACT_USER, is_superuser=False)

    if date_from:
        user_qs = user_qs.filter(date_joined__date__gte=date_from)

    if date_to:
        user_qs = user_qs.filter(date_joined__date__lte=date_to)

    user_registration_trends = list(
        user_qs.annotate(date=TruncDate("date_joined"))
        .values("date").annotate(count=Count("id")).order_by("date")
    )

    keyword_qs = Keyword.objects.filter(
        feedback_keywords__feedback__in=feedback_qs
    ).distinct()

    top_keywords = list(
        keyword_qs.values("term", "frequency", "relevance")
        .order_by("-frequency")[:10]
    )

    category_analytics = get_category_analytics()

    percentage_changes = {
        "feedback": None,
        "users": None,
    }

    if date_from and date_to:
        from django.utils.dateparse import parse_date

        start_date = parse_date(str(date_from))
        end_date = parse_date(str(date_to))

        if start_date and end_date and end_date >= start_date:
            duration = (end_date - start_date).days + 1
            previous_to = start_date - timedelta(days=1)
            previous_from = previous_to - timedelta(days=duration - 1)

            previous_feedback = Feedback.objects.filter(
                created_at__date__gte=previous_from,
                created_at__date__lte=previous_to
            ).count()

            previous_users = User.objects.filter(
                role=User.REACT_USER,
                is_superuser=False,
                date_joined__date__gte=previous_from,
                date_joined__date__lte=previous_to
            ).count()

            percentage_changes = {
                "feedback": round(((total_feedback - previous_feedback) / previous_feedback) * 100, 2) if previous_feedback else None,
                "users": round(((user_qs.count() - previous_users) / previous_users) * 100, 2) if previous_users else None,
            }

    user_analytics = get_user_analytics()

    return {
        **user_analytics,
        "total_feedback": total_feedback,
        "total_categories": category_analytics["total_categories"],
        "total_analyzed": total_analyzed,
        "pending_analysis": total_feedback - total_analyzed,
        "sentiment_distribution": sentiment_distribution,
        "sentiment_percentages": sentiment_percentages,
        "category_distribution": category_distribution,
        "status_distribution": status_distribution,
        "feedback_trends": feedback_trends,
        "user_registration_trends": user_registration_trends,
        "top_keywords": top_keywords,
        "top_categories": category_distribution[:5],
        "percentage_changes": percentage_changes,
    }


def get_keyword_analytics():
    keywords = Keyword.objects.annotate(
        feedback_count=Count("feedback_keywords")
    ).filter(feedback_count__gt=0).order_by("-frequency")

    keyword_details = []

    for keyword in keywords:
        feedback_ids = FeedbackKeyword.objects.filter(
            keyword=keyword
        ).values_list("feedback_id", flat=True)

        sentiment_counts = TextAnalysis.objects.filter(
            feedback_id__in=feedback_ids
        ).values("sentiment").annotate(count=Count("id"))

        sentiment = {
            "positive": 0,
            "negative": 0,
            "neutral": 0,
        }

        total = 0

        for item in sentiment_counts:
            key = item["sentiment"].lower()
            sentiment[key] = item["count"]
            total += item["count"]

        sentiment_percentages = {
            key: round((value / total) * 100, 2) if total else 0
            for key, value in sentiment.items()
        }

        keyword_details.append({
            "id": keyword.id,
            "term": keyword.term,
            "frequency": keyword.frequency,
            "relevance": keyword.relevance,
            "feedback_count": len(feedback_ids),
            "sentiment_percentages": sentiment_percentages,
        })

    trending_topics = keyword_details[:10]

    emerging_issues = [
        item for item in keyword_details
        if item["sentiment_percentages"]["negative"] > 50
    ][:10]

    return {
        "total_keywords": len(keyword_details),
        "top_keywords": keyword_details[:10],
        "trending_topics": trending_topics,
        "emerging_issues": emerging_issues,
    }
