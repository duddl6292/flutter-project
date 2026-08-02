from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TimeStampedModel


class TestResult(TimeStampedModel):
    """의료진 검토 후 환자에게 제공하는 공식 검사 결과."""

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "작성 중"
        FINAL = "FINAL", "최종"
        CORRECTED = "CORRECTED", "정정"
        CANCELLED = "CANCELLED", "취소"

    encounter = models.ForeignKey(
        "appointments.Encounter",
        on_delete=models.PROTECT,
        related_name="test_results",
    )
    case = models.ForeignKey(
        "ct_analysis.CTCase",
        on_delete=models.PROTECT,
        related_name="test_results",
    )

    test_type = models.CharField(max_length=64)
    title = models.CharField(max_length=200)
    performed_at = models.DateTimeField()

    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    summary = models.TextField()
    clinician_comment = models.TextField(blank=True)
    result_file_uri = models.CharField(
        max_length=1024,
        blank=True,
    )

    is_released_to_patient = models.BooleanField(default=False)
    released_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    released_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="released_test_results",
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_test_results",
    )

    class Meta:
        ordering = ["-performed_at", "-created_at"]
        indexes = [
            models.Index(
                fields=["encounter", "performed_at"],
                name="testresult_encounter_idx",
            ),
            models.Index(
                fields=["status", "performed_at"],
                name="testresult_status_date_idx",
            ),
            models.Index(
                fields=["is_released_to_patient", "released_at"],
                name="testresult_release_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(is_released_to_patient=False)
                    | (
                        models.Q(is_released_to_patient=True)
                        & models.Q(released_at__isnull=False)
                        & models.Q(released_by__isnull=False)
                        & models.Q(
                            status__in=[
                                "FINAL",
                                "CORRECTED",
                            ]
                        )
                    )
                ),
                name="testresult_release_required",
            ),
        ]

    def clean(self) -> None:
        super().clean()

        if (
            self.case_id
            and self.encounter_id
            and self.case.encounter_id != self.encounter_id
        ):
            raise ValidationError(
                {
                    "encounter": (
                        "TestResult의 encounter와 "
                        "CTCase의 encounter가 같아야 합니다."
                    )
                }
            )

        if self.is_released_to_patient:
            if self.status not in {
                self.Status.FINAL,
                self.Status.CORRECTED,
            }:
                raise ValidationError(
                    {
                        "status": (
                            "최종 또는 정정 상태의 결과만 "
                            "환자에게 공개할 수 있습니다."
                        )
                    }
                )

            if self.released_at is None:
                raise ValidationError(
                    {
                        "released_at": (
                            "환자 공개 시 공개일시가 필요합니다."
                        )
                    }
                )

            if self.released_by_id is None:
                raise ValidationError(
                    {
                        "released_by": (
                            "환자 공개 시 공개 담당자가 필요합니다."
                        )
                    }
                )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.title} - {self.status}"