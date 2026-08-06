import logging
from pathlib import Path

from django.conf import settings
from django.utils import timezone

from .models import (
    Device,
    Notification,
    NotificationDelivery,
    NotificationPreference,
    NotificationSetting,
)


logger = logging.getLogger(__name__)


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


PUSH_TITLES = {
    Notification.Type.APPOINTMENT: "진료 일정 알림",
    Notification.Type.MEDICATION: "복약 알림",
    Notification.Type.TEST_RESULT: "검사 결과 알림",
    Notification.Type.CONSULTATION: "협진 알림",
    Notification.Type.EMERGENCY: "긴급 알림",
    Notification.Type.SYSTEM: "시스템 알림",
    Notification.Type.OTHER: "새 알림",
}

APPOINTMENT_PUSH_BODIES = {
    "CREATED": "새 진료 예약이 등록되었습니다.",
    "UPDATED": "진료 예약 정보가 변경되었습니다.",
    "STATUS_SCHEDULED": "진료 예약이 등록되었습니다.",
    "STATUS_CONFIRMED": "진료 예약이 확정되었습니다.",
    "STATUS_CHECKED_IN": "예약 환자가 접수되었습니다.",
    "STATUS_COMPLETED": "진료가 완료 처리되었습니다.",
    "STATUS_CANCELLED": "진료 예약이 취소되었습니다.",
    "STATUS_NO_SHOW": "진료 예약이 미방문 처리되었습니다.",
}

TEST_RESULT_PUSH_BODIES = {
    "REGISTERED": "새 검사 결과가 등록되었습니다.",
    "FINALIZED": "검사 결과가 최종 확정되었습니다.",
    "CORRECTED": "검사 결과가 정정되었습니다.",
    "RELEASED": "검사 결과가 환자에게 공개되었습니다.",
    "CT_ANALYSIS_COMPLETED": "CT AI 분석이 완료되었습니다.",
    "CT_ANALYSIS_FAILED": "CT AI 분석을 완료하지 못했습니다.",
}

INVALID_DEVICE_ERROR_NAMES = {
    "SenderIdMismatchError",
    "UnregisteredError",
}


def _is_invalid_device_error(exc: Exception) -> bool:
    error_name = type(exc).__name__
    if error_name in INVALID_DEVICE_ERROR_NAMES:
        return True

    return (
        error_name == "InvalidArgumentError"
        and "registration token" in str(exc).lower()
    )


def _firebase_app():
    import firebase_admin
    from firebase_admin import credentials

    try:
        return firebase_admin.get_app()
    except ValueError:
        pass

    options = {
        "httpTimeout": settings.FCM_HTTP_TIMEOUT_SECONDS,
    }
    if settings.FIREBASE_PROJECT_ID:
        options["projectId"] = settings.FIREBASE_PROJECT_ID

    credentials_path = settings.FIREBASE_CREDENTIALS_PATH
    if credentials_path:
        path = Path(credentials_path)
        if not path.is_absolute():
            path = settings.BASE_DIR.parent / path
        credential = credentials.Certificate(str(path))
        return firebase_admin.initialize_app(
            credential,
            options=options,
        )

    return firebase_admin.initialize_app(options=options)


def send_web_push(
    *,
    token: str,
    data: dict[str, str],
    urgency: str,
) -> str:
    """Firebase Admin SDK로 웹 데이터 메시지를 한 건 전송한다."""

    from firebase_admin import messaging

    message = messaging.Message(
        data=data,
        token=token,
        webpush=messaging.WebpushConfig(
            headers={
                "TTL": "3600",
                "Urgency": urgency,
            },
        ),
    )
    return messaging.send(
        message,
        app=_firebase_app(),
    )


def _safe_push_copy(
    notification: Notification,
) -> tuple[str, str]:
    event = str(
        notification.data.get("event", "")
    ).strip().upper()

    if notification.type == Notification.Type.CONSULTATION:
        actor_name = str(
            notification.data.get("actor_name", "")
        ).strip()
        actor = (
            f"{actor_name} 의료진"
            if actor_name
            else "담당 의료진"
        )
        bodies = {
            "REQUESTED": f"{actor}이 새 협진을 요청했습니다.",
            "ACCEPTED": f"{actor}이 협진 요청을 수락했습니다.",
            "MESSAGE": f"{actor}이 메시지를 보냈습니다.",
            "COMPLETED": "협진 최종 답변이 등록되었습니다.",
            "CANCELLED": "협진 요청이 취소되었습니다.",
        }
        return "협진 알림", bodies.get(
            event,
            "새로운 협진 알림이 도착했습니다.",
        )

    if notification.type == Notification.Type.APPOINTMENT:
        return "예약 알림", APPOINTMENT_PUSH_BODIES.get(
            event,
            "진료 예약에 변경 사항이 있습니다.",
        )

    if notification.type == Notification.Type.TEST_RESULT:
        is_ct_analysis = event.startswith("CT_ANALYSIS_")
        return (
            "CT 분석 알림" if is_ct_analysis else "검사 결과 알림",
            TEST_RESULT_PUSH_BODIES.get(
                event,
                "검사 결과에 변경 사항이 있습니다.",
            ),
        )

    if notification.type == Notification.Type.EMERGENCY:
        return (
            "긴급 알림",
            "새 응급 안내가 도착했습니다. 앱에서 확인해주세요.",
        )

    if notification.type == Notification.Type.MEDICATION:
        return (
            "복약 알림",
            notification.title or "복약 일정을 확인해주세요.",
        )

    return (
        PUSH_TITLES.get(notification.type, "새 알림"),
        notification.title or "새로운 알림이 도착했습니다.",
    )


def _push_data(
    notification: Notification,
) -> dict[str, str]:
    path = (
        notification.data.get("path")
        or notification.data.get("route")
        or "/dashboard"
    )
    if not isinstance(path, str) or not path.startswith("/"):
        path = "/dashboard"

    title, body = _safe_push_copy(notification)

    return {
        "notification_id": str(notification.pk),
        "type": notification.type,
        "title": title,
        "body": body,
        "path": path,
    }


def _masked_destination(token: str) -> str:
    return f"fcm:***{token[-12:]}"


def dispatch_web_push(notification_id) -> int:
    """알림 수신자의 활성 웹 브라우저에 푸시를 전송한다."""

    if not settings.FCM_ENABLED:
        return 0

    try:
        notification = (
            Notification.objects
            .select_related("recipient")
            .get(pk=notification_id)
        )
    except Notification.DoesNotExist:
        return 0

    devices = list(
        Device.objects.filter(
            user=notification.recipient,
            platform=Device.Platform.WEB,
            client_type=Device.ClientType.CLINICIAN_WEB,
            is_active=True,
        )
    )
    if not devices:
        return 0

    allowed = should_send_notification(
        user=notification.recipient,
        notification_type=notification.type,
        channel="push",
    )
    push_data = _push_data(notification)
    urgency = (
        "high"
        if notification.type == Notification.Type.EMERGENCY
        else "normal"
    )
    sent_count = 0

    for device in devices:
        delivery = NotificationDelivery.objects.create(
            notification=notification,
            device=device,
            channel=NotificationDelivery.Channel.PUSH,
            destination=_masked_destination(device.fcm_token),
            status=(
                NotificationDelivery.Status.PENDING
                if allowed
                else NotificationDelivery.Status.SUPPRESSED
            ),
        )

        if not allowed:
            continue

        delivery.status = NotificationDelivery.Status.SENDING
        delivery.attempt_count = 1
        delivery.save(
            update_fields=[
                "status",
                "attempt_count",
                "updated_at",
            ],
        )

        try:
            provider_message_id = send_web_push(
                token=device.fcm_token,
                data=push_data,
                urgency=urgency,
            )
        except Exception as exc:  # Firebase 오류는 업무 요청을 실패시키지 않는다.
            failed_at = timezone.now()
            error_code = type(exc).__name__
            delivery.status = NotificationDelivery.Status.FAILED
            delivery.failed_at = failed_at
            delivery.error_code = error_code
            delivery.error_message = str(exc)
            delivery.save(
                update_fields=[
                    "status",
                    "failed_at",
                    "error_code",
                    "error_message",
                    "updated_at",
                ],
            )

            if _is_invalid_device_error(exc):
                Device.objects.filter(pk=device.pk).update(
                    is_active=False,
                    last_used_at=failed_at,
                    updated_at=failed_at,
                )

            logger.warning(
                "Web push delivery failed",
                extra={
                    "notification_id": str(notification.pk),
                    "device_id": str(device.pk),
                    "error_code": error_code,
                },
            )
            continue

        sent_at = timezone.now()
        delivery.status = NotificationDelivery.Status.SENT
        delivery.provider_message_id = provider_message_id
        delivery.provider_response = {
            "message_id": provider_message_id,
        }
        delivery.sent_at = sent_at
        delivery.save(
            update_fields=[
                "status",
                "provider_message_id",
                "provider_response",
                "sent_at",
                "updated_at",
            ],
        )
        sent_count += 1

    return sent_count
