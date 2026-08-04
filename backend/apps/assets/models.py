from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TimeStampedModel


class StoredObject(TimeStampedModel):
    """스토리지 객체의 위치와 무결성 메타데이터."""

    class Provider(models.TextChoices):
        GCS = "GCS", "Google Cloud Storage"
        S3 = "S3", "Amazon S3 호환"
        LOCAL = "LOCAL", "로컬 스토리지"

    class Status(models.TextChoices):
        PENDING = "PENDING", "업로드 대기"
        AVAILABLE = "AVAILABLE", "사용 가능"
        QUARANTINED = "QUARANTINED", "격리"
        DELETED = "DELETED", "삭제"

    provider = models.CharField(
        max_length=16,
        choices=Provider.choices,
        default=Provider.GCS,
        db_index=True,
    )
    bucket_name = models.CharField(max_length=255)
    object_key = models.CharField(max_length=1024)
    original_filename = models.CharField(max_length=255, blank=True)
    content_type = models.CharField(max_length=150, blank=True)
    file_format = models.CharField(max_length=32, blank=True, db_index=True)
    file_size_bytes = models.PositiveBigIntegerField(default=0)
    sha256 = models.CharField(max_length=64, blank=True, db_index=True)
    encryption_key_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="uploaded_objects",
    )
    available_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["status", "created_at"],
                name="storedobj_status_date_idx",
            ),
            models.Index(
                fields=["sha256", "file_size_bytes"],
                name="storedobj_hash_size_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "bucket_name", "object_key"],
                name="storedobj_location_uniq",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(status="AVAILABLE", available_at__isnull=False)
                    | ~models.Q(status="AVAILABLE")
                ),
                name="storedobj_available_at_req",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(status="DELETED", deleted_at__isnull=False)
                    | ~models.Q(status="DELETED")
                ),
                name="storedobj_deleted_at_req",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if self.status == self.Status.AVAILABLE and self.available_at is None:
            raise ValidationError({"available_at": "사용 가능한 파일에는 완료 일시가 필요합니다."})
        if self.status == self.Status.DELETED and self.deleted_at is None:
            raise ValidationError({"deleted_at": "삭제된 파일에는 삭제 일시가 필요합니다."})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.provider}://{self.bucket_name}/{self.object_key}"
