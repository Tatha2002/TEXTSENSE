from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPE_CHOICES = [
        ("FEEDBACK_SUBMITTED", "Feedback Submitted"),
        ("ANALYSIS_COMPLETED", "Analysis Completed"),
        ("ADMIN_UPDATE", "Administrative Update"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    read_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.type}"
