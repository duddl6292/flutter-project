from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Notification

@receiver(
    post_save,
    sender=Notification,
    dispatch_uid="notifications_dispatch_web_push",
)
def dispatch_web_push_after_commit(
    sender,
    instance: Notification,
    created: bool,
    **kwargs,
) -> None:
    """새 인앱 알림이 확정된 뒤 웹 푸시 발송을 시작한다."""

    if not created:
        return

    notification_id = instance.pk

    def dispatch() -> None:
        from .services import dispatch_web_push

        dispatch_web_push(notification_id)

    transaction.on_commit(dispatch, robust=True)
