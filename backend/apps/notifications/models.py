from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel


class Device(TimeStampedModel):
    """사용자의 FCM 기기 토큰과 기기 상태를 관리한다."""

    class Platform(models.TextChoices):
        ANDROID = "ANDROID", "Android"
        IOS = "IOS", "iOS"
        WEB = "WEB", "Web"

    class ClientType(models.TextChoices):
        PATIENT_APP = "PATIENT_APP", "환자 앱"
        CLINICIAN_APP = "CLINICIAN_APP", "의료진 앱"
        CLINICIAN_WEB = "CLINICIAN_WEB", "의료진 웹"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="devices",
        verbose_name="사용자",
    )
    platform = models.CharField(
        max_length=16,
        choices=Platform.choices,
        db_index=True,
        verbose_name="플랫폼",
    )
    client_type = models.CharField(
        max_length=24,
        choices=ClientType.choices,
        db_index=True,
        verbose_name="클라이언트 유형",
    )
    device_identifier = models.CharField(
        max_length=255,
        verbose_name="앱 설치 또는 브라우저 식별자",
    )
    fcm_token = models.CharField(
        max_length=512,
        unique=True,
        verbose_name="FCM 토큰",
    )
    device_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="기기 이름",
    )
    app_version = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="앱 버전",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="활성 여부",
    )
    registered_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="등록 일시",
    )
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="마지막 사용 일시",
    )

    class Meta:
        ordering = ["-last_used_at", "-registered_at"]
        indexes = [
            models.Index(
                fields=["user", "is_active"],
                name="device_user_active_idx",
            ),
            models.Index(
                fields=["platform", "is_active"],
                name="device_platform_active_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "client_type",
                    "device_identifier",
                ],
                name="device_user_client_ident_uniq",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        client_type="CLINICIAN_WEB",
                        platform="WEB",
                    )
                    | models.Q(
                        client_type__in=[
                            "PATIENT_APP",
                            "CLINICIAN_APP",
                        ],
                        platform__in=[
                            "ANDROID",
                            "IOS",
                        ],
                    )
                ),
                name="device_client_platform_valid",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(last_used_at__isnull=True)
                    | models.Q(
                        last_used_at__gte=models.F(
                            "registered_at"
                        )
                    )
                ),
                name="device_last_used_after_reg",
            ),
        ]
        verbose_name = "사용자 기기"
        verbose_name_plural = "사용자 기기"

    def clean(self) -> None:
        super().clean()

        web_client = (
            self.client_type
            == self.ClientType.CLINICIAN_WEB
        )
        web_platform = (
            self.platform == self.Platform.WEB
        )

        if web_client != web_platform:
            raise ValidationError({
                "platform": (
                    "의료진 웹은 WEB 플랫폼만, 앱은 "
                    "ANDROID 또는 IOS 플랫폼만 사용할 수 있습니다."
                ),
            })

        if (
            self.last_used_at is not None
            and self.last_used_at < self.registered_at
        ):
            raise ValidationError(
                {
                    "last_used_at": (
                        "마지막 사용 일시는 등록 일시보다 "
                        "빠를 수 없습니다."
                    )
                }
            )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        device_label = self.device_name or self.platform

        return (
            f"{self.user.username} - "
            f"{device_label}"
        )


class Notification(TimeStampedModel):
    """사용자에게 제공한 앱 알림과 푸시 알림 이력."""

    class Type(models.TextChoices):
        APPOINTMENT = "APPOINTMENT", "진료 예약"
        MEDICATION = "MEDICATION", "복약"
        TEST_RESULT = "TEST_RESULT", "검사 결과"
        CONSULTATION = "CONSULTATION", "협진"
        EMERGENCY = "EMERGENCY", "응급 안내"
        SYSTEM = "SYSTEM", "시스템"
        OTHER = "OTHER", "기타"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="notifications",
        verbose_name="수신 사용자",
    )
    type = models.CharField(
        max_length=24,
        choices=Type.choices,
        db_index=True,
        verbose_name="알림 유형",
    )
    title = models.CharField(
        max_length=200,
        verbose_name="알림 제목",
    )
    body = models.TextField(
        verbose_name="알림 내용",
    )
    data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="추가 데이터",
        help_text=(
            "화면 이동 경로, 관련 객체 UUID 등의 "
            "추가 정보를 저장합니다."
        ),
    )
    is_read = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="읽음 여부",
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="읽은 일시",
    )
    deduplication_key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="중복 방지 키",
        help_text=(
            "동일 알림의 중복 생성을 방지하는 키입니다."
        ),
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=[
                    "recipient",
                    "is_read",
                    "created_at",
                ],
                name="noti_rec_read_date_idx",
            ),
            models.Index(
                fields=["type", "created_at"],
                name="noti_type_date_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        is_read=False,
                        read_at__isnull=True,
                    )
                    | models.Q(
                        is_read=True,
                        read_at__isnull=False,
                    )
                ),
                name="notification_read_state_valid",
            ),
            models.UniqueConstraint(
                fields=[
                    "recipient",
                    "deduplication_key",
                ],
                condition=(
                    models.Q(
                        deduplication_key__isnull=False
                    )
                    & ~models.Q(deduplication_key="")
                ),
                name="notification_rec_dedup_uniq",
            ),
        ]
        verbose_name = "알림"
        verbose_name_plural = "알림"

    def clean(self) -> None:
        super().clean()

        if self.is_read and self.read_at is None:
            raise ValidationError(
                {
                    "read_at": (
                        "읽음 상태의 알림에는 "
                        "읽은 일시가 필요합니다."
                    )
                }
            )

        if not self.is_read and self.read_at is not None:
            raise ValidationError(
                {
                    "read_at": (
                        "읽지 않은 알림에는 "
                        "읽은 일시를 입력할 수 없습니다."
                    )
                }
            )

    def mark_as_read(self) -> None:
        """알림을 읽음 상태로 변경한다."""

        if self.is_read:
            return

        self.is_read = True
        self.read_at = timezone.now()
        self.save()

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"{self.recipient.username} - "
            f"{self.title}"
        )


class NotificationPreference(TimeStampedModel):
    """사용자별 알림 유형과 전달 채널 설정을 관리한다."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
        verbose_name="사용자",
    )
    notification_type = models.CharField(
        max_length=24,
        choices=Notification.Type.choices,
        verbose_name="알림 유형",
    )
    push_enabled = models.BooleanField(
        default=True,
        verbose_name="푸시 알림 사용",
    )
    email_enabled = models.BooleanField(
        default=False,
        verbose_name="이메일 알림 사용",
    )

    class Meta:
        ordering = ["user", "notification_type"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "notification_type"],
                name="noti_pref_user_type_unique",
            ),
        ]
        verbose_name = "알림 설정"
        verbose_name_plural = "알림 설정"

    def __str__(self) -> str:
        return (
            f"{self.user.username} - "
            f"{self.get_notification_type_display()}"
        )


class NotificationSetting(TimeStampedModel):
    """사용자의 모든 알림에 공통으로 적용되는 방해금지 설정."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_setting",
        verbose_name="사용자",
    )
    quiet_hours_enabled = models.BooleanField(
        default=False,
        verbose_name="방해금지 사용",
    )
    quiet_hours_start = models.TimeField(
        null=True,
        blank=True,
        verbose_name="방해금지 시작 시간",
    )
    quiet_hours_end = models.TimeField(
        null=True,
        blank=True,
        verbose_name="방해금지 종료 시간",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        quiet_hours_start__isnull=True,
                        quiet_hours_end__isnull=True,
                    )
                    | models.Q(
                        quiet_hours_start__isnull=False,
                        quiet_hours_end__isnull=False,
                    )
                ),
                name="noti_quiet_hours_pair_valid",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(quiet_hours_enabled=False)
                    | models.Q(
                        quiet_hours_start__isnull=False,
                        quiet_hours_end__isnull=False,
                    )
                ),
                name="noti_quiet_hours_required",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(quiet_hours_start__isnull=True)
                    | ~models.Q(
                        quiet_hours_start=models.F("quiet_hours_end"),
                    )
                ),
                name="noti_quiet_hours_different",
            ),
        ]
        verbose_name = "공통 알림 설정"
        verbose_name_plural = "공통 알림 설정"

    def clean(self) -> None:
        super().clean()

        has_start = self.quiet_hours_start is not None
        has_end = self.quiet_hours_end is not None

        if has_start != has_end:
            raise ValidationError({
                "quiet_hours_start": (
                    "방해금지 시작 시간과 종료 시간을 "
                    "모두 입력해야 합니다."
                ),
                "quiet_hours_end": (
                    "방해금지 시작 시간과 종료 시간을 "
                    "모두 입력해야 합니다."
                ),
            })

        if self.quiet_hours_enabled and not (has_start and has_end):
            raise ValidationError({
                "quiet_hours_start": (
                    "방해금지를 사용하려면 시작 시간이 필요합니다."
                ),
                "quiet_hours_end": (
                    "방해금지를 사용하려면 종료 시간이 필요합니다."
                ),
            })

        if (
            has_start
            and has_end
            and self.quiet_hours_start == self.quiet_hours_end
        ):
            raise ValidationError({
                "quiet_hours_end": (
                    "방해금지 시작 시간과 종료 시간은 달라야 합니다."
                ),
            })

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.user.username} - 방해금지 설정"


class NotificationDelivery(TimeStampedModel):
    """푸시·이메일 알림의 전송 및 재시도 결과."""

    class Channel(models.TextChoices):
        PUSH = "PUSH", "푸시"
        EMAIL = "EMAIL", "이메일"

    class Status(models.TextChoices):
        PENDING = "PENDING", "전송 대기"
        SUPPRESSED = "SUPPRESSED", "설정에 따라 보류"
        SENDING = "SENDING", "전송 중"
        SENT = "SENT", "전송 완료"
        DELIVERED = "DELIVERED", "수신 확인"
        FAILED = "FAILED", "전송 실패"
        CANCELLED = "CANCELLED", "취소"

    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name="deliveries",
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.SET_NULL,
        related_name="notification_deliveries",
        null=True,
        blank=True,
    )
    channel = models.CharField(max_length=16, choices=Channel.choices, db_index=True)
    destination = models.CharField(max_length=512, blank=True)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    provider_message_id = models.CharField(max_length=255, blank=True, db_index=True)
    attempt_count = models.PositiveIntegerField(default=0)
    scheduled_at = models.DateTimeField(default=timezone.now, db_index=True)
    next_attempt_at = models.DateTimeField(null=True, blank=True, db_index=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    error_code = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)
    provider_response = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["scheduled_at", "created_at"]
        indexes = [
            models.Index(
                fields=["status", "next_attempt_at"],
                name="notidelivery_retry_idx",
            ),
            models.Index(
                fields=["notification", "channel"],
                name="notidelivery_noti_channel_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(channel="PUSH", device__isnull=False)
                    | models.Q(channel="EMAIL", device__isnull=True)
                ),
                name="notidelivery_target_valid",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(delivered_at__isnull=True)
                    | models.Q(sent_at__isnull=False, delivered_at__gte=models.F("sent_at"))
                ),
                name="notidelivery_time_valid",
            ),
        ]

# Device.fcm_token
# → Flutter·Web 앱에서 발급된 FCM 토큰

# Device.is_active
# → 로그아웃·토큰 만료 기기 비활성화

# Notification.data
# → 관련 예약 UUID, 검사결과 UUID, 화면 경로

# Notification.deduplication_key
# → 같은 알림이 여러 번 생성되는 것 방지
