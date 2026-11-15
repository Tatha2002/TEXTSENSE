
from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "type",
        "read_status",
        "created_at",
    )

    list_filter = ("type", "read_status", "created_at")

    search_fields = ("user__email", "message")
