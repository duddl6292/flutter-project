from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from apps.notifications.models import (
    Device,
    Notification,
    NotificationDelivery,
)


TEST_NOTIFICATION_CONFIG = {
    Notification.Type.APPOINTMENT: {
        "title": "예약 알림 테스트",
        "body": "진료 예약 알림이 정상적으로 연결되었습니다.",
        "path": "/appointments",
    },
    Notification.Type.TEST_RESULT: {
        "title": "검사 결과 알림 테스트",
        "body": "검사 결과 알림이 정상적으로 연결되었습니다.",
        "path": "/examinations",
    },
    Notification.Type.CONSULTATION: {
        "title": "협진 알림 테스트",
        "body": "협진 요청 알림이 정상적으로 연결되었습니다.",
        "path": "/consultations",
    },
    Notification.Type.SYSTEM: {
        "title": "BrainOn 웹 알림 테스트",
        "body": "웹 푸시 알림 연결이 정상적으로 동작합니다.",
        "path": "/dashboard",
    },
}


class Command(BaseCommand):
    help = "등록된 의료진 웹 브라우저로 FCM 테스트 알림을 전송합니다."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--username",
            required=True,
            help="알림을 받을 사용자 로그인 아이디",
        )
        parser.add_argument(
            "--type",
            choices=tuple(TEST_NOTIFICATION_CONFIG),
            default=Notification.Type.SYSTEM,
            help=(
                "테스트 알림 유형: APPOINTMENT, TEST_RESULT, "
                "CONSULTATION, SYSTEM"
            ),
        )
        parser.add_argument(
            "--path",
            default=None,
            help="알림 클릭 시 이동할 웹 경로 (생략 시 유형별 기본 경로)",
        )

    def handle(self, *args, **options) -> None:
        if not settings.FCM_ENABLED:
            raise CommandError(
                "FCM_ENABLED가 false입니다. .env에서 true로 설정하세요."
            )

        notification_type = options["type"]
        notification_config = TEST_NOTIFICATION_CONFIG[
            notification_type
        ]
        path = options["path"] or notification_config["path"]
        if not path.startswith("/"):
            raise CommandError("--path는 /로 시작해야 합니다.")

        user_model = get_user_model()
        try:
            user = user_model.objects.get(username=options["username"])
        except user_model.DoesNotExist as exc:
            raise CommandError(
                f"사용자를 찾을 수 없습니다: {options['username']}"
            ) from exc

        devices = Device.objects.filter(
            user=user,
            platform=Device.Platform.WEB,
            client_type=Device.ClientType.CLINICIAN_WEB,
            is_active=True,
        )
        device_count = devices.count()
        if device_count == 0:
            raise CommandError(
                "활성화된 웹 알림 기기가 없습니다. "
                "웹에 로그인한 뒤 브라우저 알림을 허용하세요."
            )

        notification = Notification.objects.create(
            recipient=user,
            type=notification_type,
            title=notification_config["title"],
            body=notification_config["body"],
            data={"path": path},
        )

        deliveries = NotificationDelivery.objects.filter(
            notification=notification,
        )
        sent_count = deliveries.filter(
            status=NotificationDelivery.Status.SENT,
        ).count()
        failed_count = deliveries.filter(
            status=NotificationDelivery.Status.FAILED,
        ).count()
        suppressed_count = deliveries.filter(
            status=NotificationDelivery.Status.SUPPRESSED,
        ).count()

        if sent_count == 0:
            failure = deliveries.filter(
                status=NotificationDelivery.Status.FAILED,
            ).first()
            detail = (
                f" ({failure.error_code}: {failure.error_message})"
                if failure
                else ""
            )
            raise CommandError(
                "테스트 알림을 전송하지 못했습니다. "
                f"실패 {failed_count}, 설정으로 제외 {suppressed_count}{detail}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"{notification_type} 웹 테스트 알림 전송 완료: "
                f"{sent_count}/{device_count}개 기기"
            )
        )
