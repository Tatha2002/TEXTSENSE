from django.urls import path
from .api_views import (FeedbackListAPIView, FeedbackCreateAPIView, FeedbackDetailAPIView,)

urlpatterns = [
    path("", FeedbackListAPIView.as_view(), name="feedback-list"),
    path("create/", FeedbackCreateAPIView.as_view(), name="feedback-create"),
    path("details/<int:pk>/", FeedbackDetailAPIView.as_view(), name="feedback-detail"),
]



# GET http://127.0.0.1:8000/textsense/feedback/
# POST http://127.0.0.1:8000/textsense/feedback/create/
# GET http://127.0.0.1:8000/textsense/feedback/details/1/
# PATCH http://127.0.0.1:8000/textsense/feedback/details/1/
# DELETE http://127.0.0.1:8000/textsense/feedback/details/1/