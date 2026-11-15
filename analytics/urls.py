from django.urls import path
from .api_views import AdminAnalyticsAPIView

urlpatterns = [
    path("analytics/", AdminAnalyticsAPIView.as_view(), name="admin-analytics"),
]


# POST http://127.0.0.1:8000/textsense/admin/analytics/