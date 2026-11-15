from django.urls import path
from .api_views import (NotificationListAPIView, NotificationDetailAPIView, MarkNotificationReadAPIView, MarkAllNotificationsReadAPIView,)

urlpatterns = [

    path("", NotificationListAPIView.as_view(), name="notification-list"),
    path("read-all/", MarkAllNotificationsReadAPIView.as_view(), name="notification-read-all"),
    path("<int:pk>/", NotificationDetailAPIView.as_view(),name="notification-detail"),
    path("<int:pk>/read/", MarkNotificationReadAPIView.as_view(), name="notification-read"),

]


# GET http://127.0.0.1:8000/textsense/notifications/
# PATCH http://127.0.0.1:8000/textsense/notifications/read-all/
# GET http://127.0.0.1:8000/textsense/notifications/5
# DELETE http://127.0.0.1:8000/textsense/notifications/5
# GET http://127.0.0.1:8000/textsense/notifications/5/read/