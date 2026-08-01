from .models import Notification


def visible_notifications(user):
    return Notification.objects.filter(recipient=user)
