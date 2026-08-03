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

# Device.fcm_token
# → Flutter·Web 앱에서 발급된 FCM 토큰

# Device.is_active
# → 로그아웃·토큰 만료 기기 비활성화

# Notification.data
# → 관련 예약 UUID, 검사결과 UUID, 화면 경로

# Notification.deduplication_key
# → 같은 알림이 여러 번 생성되는 것 방지