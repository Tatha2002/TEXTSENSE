
from .models import Notification


def create_notification(user, message, notification_type, title=None, category="SYSTEM", priority="MEDIUM", reference_id=None):

    if not user:
        return None

    if not title:
        title = message[:255]

    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        type=notification_type,
        category=category,
        priority=priority,
        reference_id=reference_id
    )
