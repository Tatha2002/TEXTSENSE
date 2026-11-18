
from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification

        fields = [
            "id",
            "user",
            "title",
            "message",
            "type",
            "category",
            "priority",
            "reference_id",
            "read_status",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "title",
            "message",
            "type",
            "category",
            "priority",
            "reference_id",
            "created_at",
        ]
