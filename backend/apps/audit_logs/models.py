from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class AuditEvent(TimeStampedModel):
    """환자 데이터 열람·수정·다운로드를 기록하는 감사 이벤트."""

    class Action(models.TextChoices):
        CREATED = "CREATED", "생성"
        VIEWED = "VIEWED", "열람"
        UPDATED = "UPDATED", "수정"
        DELETED = "DELETED", "삭제"
        DOWNLOADED = "DOWNLOADED", "다운로드"
        EXPORTED = "EXPORTED", "내보내기"
        RELEASED = "RELEASED", "환자 공개"
        ANALYSIS_REQUESTED = "ANALYSIS_REQUESTED", "AI 분석 요청"
        TOOL_EXECUTED = "TOOL_EXECUTED", "챗봇 도구 실행"
        AUTHENTICATED = "AUTHENTICATED", "인증"
        PERMISSION_DENIED = "PERMISSION_DENIED", "접근 거부"

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="audit_events",
        null=True,
        blank=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="audit_events",
        null=True,
        blank=True,
    )
    encounter = models.ForeignKey(
        "appointments.Encounter",
        on_delete=models.PROTECT,
        related_name="audit_events",
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=32, choices=Action.choices, db_index=True)
    resource_type = models.CharField(max_length=100, db_index=True)
    resource_id = models.UUIDField(null=True, blank=True, db_index=True)
    request_id = models.CharField(max_length=100, blank=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    outcome = models.CharField(max_length=32, default="SUCCESS", db_index=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["actor", "created_at"],
                name="audit_actor_date_idx",
            ),
            models.Index(
                fields=["patient", "created_at"],
                name="audit_patient_date_idx",
            ),
            models.Index(
                fields=["resource_type", "resource_id"],
                name="audit_resource_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.action} {self.resource_type}:{self.resource_id or '-'}"
