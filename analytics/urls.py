from django.urls import path
from .api_views import (AdminAnalyticsAPIView, AdminUserAnalyticsAPIView, AdminFeedbackAnalyticsAPIView, AdminCategoryAnalyticsAPIView, AdminKeywordAnalyticsAPIView)


urlpatterns = [
    path("analytics/", AdminAnalyticsAPIView.as_view(), name="admin-analytics"),
    path("analytics/users/", AdminUserAnalyticsAPIView.as_view(), name="admin-user-analytics"),
    path("analytics/feedback/", AdminFeedbackAnalyticsAPIView.as_view(), name="admin-feedback-analytics"),
    path("analytics/categories/", AdminCategoryAnalyticsAPIView.as_view(), name="admin-category-analytics"),
    path("analytics/keywords/", AdminKeywordAnalyticsAPIView.as_view(), name="admin-keyword-analytics"),
]



# GET http://127.0.0.1:8000/textsense/admin/analytics/
# GET http://127.0.0.1:8000/textsense/admin/analytics/users/
# GET http://127.0.0.1:8000/textsense/admin/analytics/feedback/
# GET http://127.0.0.1:8000/textsense/admin/analytics/categories/
# GET http://127.0.0.1:8000/textsense/admin/analytics/keywords/


