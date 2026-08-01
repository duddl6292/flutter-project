import logging

from django.db import transaction

from .models import Notification
from .senders import get_notification_sender

logger = logging.getLogger(__name__)


def _send(notification_id):
    try:
        notification = Notification.objects.get(pk=notification_id)
        devices = list(notification.recipient.devices.filter(is_active=True))
        get_notification_sender().send(notification, devices)
    except Exception:
        logger.exception("notification_delivery_failed", extra={"notification_id": str(notification_id)})


def create_notification(**data):
    key = data.get("deduplication_key")
    if key:
        notification, created = Notification.objects.get_or_create(
            deduplication_key=key, defaults=data
        )
    else:
        notification, created = Notification.objects.create(**data), True
    if created:
        transaction.on_commit(lambda: _send(notification.id))
    return notification, created
