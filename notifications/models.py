
from django.db import models
from django.conf import settings


class Notification(models.Model):

    TYPE_CHOICES = [
        ("FEEDBACK_SUBMITTED", "Feedback Submitted"),
        ("ANALYSIS_COMPLETED", "Analysis Completed"),
        ("ADMIN_UPDATE", "Administrative Update"),
    ]

    CATEGORY_CHOICES = [
        ("FEEDBACK", "Feedback"),
        ("ANALYSIS", "Analysis"),
        ("USER", "User"),
        ("SYSTEM", "System"),
    ]

    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255, default="Notification")
    message = models.TextField()
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="SYSTEM")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="MEDIUM")
    reference_id = models.CharField(max_length=100, null=True, blank=True)
    read_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.title}"
