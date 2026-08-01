import logging

from django.conf import settings

logger = logging.getLogger(__name__)


class MockNotificationSender:
    def send(self, notification, devices):
        logger.info("mock_notification_sent", extra={
            "notification_id": str(notification.id), "device_count": len(devices)
        })
        return len(devices)


class FirebaseNotificationSender:
    def __init__(self):
        import firebase_admin
        from firebase_admin import credentials
        if not firebase_admin._apps:
            firebase_admin.initialize_app(credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH))

    def send(self, notification, devices):
        from firebase_admin import messaging
        messages = [messaging.Message(
            token=device.fcm_token,
            notification=messaging.Notification(title=notification.title, body=notification.body),
            data={key: str(value) for key, value in notification.data.items()},
        ) for device in devices]
        return messaging.send_each(messages).success_count if messages else 0


def get_notification_sender():
    if settings.FCM_BACKEND == "firebase" and settings.FIREBASE_CREDENTIALS_PATH:
        return FirebaseNotificationSender()
    return MockNotificationSender()
