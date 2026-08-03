from django.utils import timezone

from .models import (
    Notification,
    NotificationPreference,
    NotificationSetting,
)


DEFAULT_NOTIFICATION_CHANNELS = {
    "push_enabled": True,
    "email_enabled": False,
}

ROLE_NOTIFICATION_TYPES = {
    "PATIENT": (
        Notification.Type.APPOINTMENT,
        Notification.Type.MEDICATION,
        Notification.Type.SYSTEM,
    ),
    "CLINICIAN": (
        Notification.Type.APPOINTMENT,
        Notification.Type.TEST_RESULT,
        Notification.Type.CONSULTATION,
        Notification.Type.SYSTEM,
    ),
    "ADMIN": (
        Notification.Type.SYSTEM,
    ),
}


def get_allowed_notification_types(user) -> tuple[str, ...]:
    """사용자 역할에 노출할 알림 유형을 반환한다."""

    return ROLE_NOTIFICATION_TYPES.get(
        getattr(user, "role", ""),
        (Notification.Type.SYSTEM,),
    )


def get_notification_preference(
    *,
    user,
    notification_type: str,
) -> NotificationPreference:
    """역할에 맞는 유형별 채널 설정을 생성하거나 반환한다."""

    if notification_type not in get_allowed_notification_types(user):
        raise ValueError("사용자 역할에서 지원하지 않는 알림 유형입니다.")

    preference, _created = (
        NotificationPreference.objects.get_or_create(
            user=user,
            notification_type=notification_type,
            defaults=DEFAULT_NOTIFICATION_CHANNELS,
        )
    )

    return preference


def get_notification_setting(*, user) -> NotificationSetting:
    """사용자의 공통 방해금지 설정을 생성하거나 반환한다."""

    setting, _created = NotificationSetting.objects.get_or_create(
        user=user,
    )
    return setting


def is_quiet_hours(
    *,
    setting: NotificationSetting,
    at=None,
) -> bool:
    """주어진 시각이 사용자의 방해금지 시간인지 판단한다."""

    if (
        not setting.quiet_hours_enabled
        or setting.quiet_hours_start is None
        or setting.quiet_hours_end is None
    ):
        return False

    target = timezone.localtime(at or timezone.now()).time()
    start = setting.quiet_hours_start
    end = setting.quiet_hours_end

    if start < end:
        return start <= target < end

    # 22:00~07:00처럼 날짜 경계를 넘는 범위
    return target >= start or target < end


def is_notification_channel_enabled(
    *,
    user,
    notification_type: str,
    channel: str,
) -> bool:
    """인앱은 항상 허용하고 외부 채널은 사용자 설정을 확인한다."""

    if channel == "in_app":
        return True

    channel_fields = {
        "push": "push_enabled",
        "email": "email_enabled",
    }

    try:
        field_name = channel_fields[channel]
    except KeyError as exc:
        raise ValueError("지원하지 않는 알림 채널입니다.") from exc

    if notification_type not in get_allowed_notification_types(user):
        return False

    preference = get_notification_preference(
        user=user,
        notification_type=notification_type,
    )

    return bool(getattr(preference, field_name))


def should_send_notification(
    *,
    user,
    notification_type: str,
    channel: str,
    at=None,
) -> bool:
    """유형별 채널 설정과 방해금지 시간을 함께 적용한다."""

    if channel == "in_app":
        return True

    if not is_notification_channel_enabled(
        user=user,
        notification_type=notification_type,
        channel=channel,
    ):
        return False

    setting = get_notification_setting(user=user)
    return not is_quiet_hours(setting=setting, at=at)
