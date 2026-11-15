
from .models import Notification


def create_notification(user, message, notification_type):

    if not user:
        return None

    return Notification.objects.create(
        user=user,
        message=message,
        type=notification_type
    )
