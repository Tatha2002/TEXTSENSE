from django.db import models
from django.conf import settings
from categories.models import Category


class Feedback(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("REVIEWED", "Reviewed"),
        ("NEEDS_ATTENTION", "Needs Attention"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="feedbacks")
    title = models.CharField(max_length=200)
    text = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="feedbacks")
    source = models.CharField(max_length=100, default="website")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title