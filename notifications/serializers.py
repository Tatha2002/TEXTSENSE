
from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = [
            "id",
            "user",
            "message",
            "type",
            "read_status",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "message",
            "type",
            "created_at",
        ]
