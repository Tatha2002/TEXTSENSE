from django.contrib import admin
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "user",
        "category",
        "status",
        "created_at",
    )

    list_filter = ("status", "category", "created_at")
    search_fields = ("title", "text", "user__email")