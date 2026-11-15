from django.urls import path
from .api_views import (FeedbackListCreateAPIView,FeedbackDetailAPIView,)

urlpatterns = [
    path("create/", FeedbackListCreateAPIView.as_view(), name="feedback-list-create"),
    path("details/<int:pk>/", FeedbackDetailAPIView.as_view(), name="feedback-detail"),
]


# POST http://127.0.0.1:8000/textsense/feedback/create/
# POST http://127.0.0.1:8000/textsense/feedback/details/1/