
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Notification
from .serializers import NotificationSerializer


# 1. List notifications of logged-in user

class NotificationListAPIView(generics.ListAPIView):

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


# 2. View notification details

class NotificationDetailAPIView(generics.RetrieveAPIView):

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


# 3. Delete a particular notification

class NotificationDeleteAPIView(generics.DestroyAPIView):

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


# 4. Mark a particular notification as read

class MarkNotificationReadAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):

        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.read_status = True
        notification.save(update_fields=["read_status"])

        serializer = NotificationSerializer(notification)

        return Response(
            {
                "message": "Notification marked as read.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


# 5. Mark all notifications as read

class MarkAllNotificationsReadAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request):

        updated_count = Notification.objects.filter(user=request.user, read_status=False).update(read_status=True)

        return Response(
            {
                "message": "All notifications marked as read.",
                "updated_count": updated_count
            },
            status=status.HTTP_200_OK
        )
