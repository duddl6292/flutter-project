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
        null=True,
        blank=True,
    )
    case = models.ForeignKey(
        "ct_analysis.CTCase",
        on_delete=models.PROTECT,
        related_name="test_results",
    )
    inference_result = models.ForeignKey(
        "ct_analysis.InferenceResult",
        on_delete=models.PROTECT,
        related_name="official_test_results",
        null=True,
        blank=True,
    )
    supersedes = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="corrections",
        null=True,
        blank=True,
    )
    revision_number = models.PositiveIntegerField(default=1)

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
    finalized_at = models.DateTimeField(null=True, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    signed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="signed_test_results",
        null=True,
        blank=True,
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
            models.UniqueConstraint(
                fields=["case", "revision_number"],
                name="testresult_case_revision_uniq",
            ),
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

        if (
            self.inference_result_id
            and self.inference_result.case_id != self.case_id
        ):
            raise ValidationError(
                {"inference_result": "공식 결과와 AI 결과의 CT 분석 건이 일치해야 합니다."}
            )

        if self.supersedes_id and self.supersedes.case_id != self.case_id:
            raise ValidationError(
                {"supersedes": "정정 결과는 동일한 CT 분석 건의 결과를 대상으로 해야 합니다."}
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
        if self._state.adding and self.case_id:
            latest = (
                type(self).objects
                .filter(case_id=self.case_id)
                .order_by("-revision_number", "-created_at")
                .first()
            )
            if latest and self.revision_number <= latest.revision_number:
                self.revision_number = latest.revision_number + 1
            if (
                latest
                and self.status == self.Status.CORRECTED
                and self.supersedes_id is None
            ):
                self.supersedes = latest
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.title} - {self.status}"


class TestResultStatusHistory(TimeStampedModel):
    """공식 검사결과의 상태 및 공개 변경 이력."""

    result = models.ForeignKey(
        TestResult,
        on_delete=models.PROTECT,
        related_name="status_history",
    )
    previous_status = models.CharField(max_length=16, blank=True)
    new_status = models.CharField(max_length=16, choices=TestResult.Status.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="test_result_status_changes",
    )
    reason = models.TextField(blank=True)
    is_released_to_patient = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(
                fields=["result", "created_at"],
                name="testreshist_result_date_idx",
            ),
        ]


class TestResultAsset(TimeStampedModel):
    """CT 공식 결과에 첨부되는 보고서와 환자용 사본."""

    class AssetType(models.TextChoices):
        REPORT = "REPORT", "보고서"
        PATIENT_COPY = "PATIENT_COPY", "환자용 사본"
        OTHER = "OTHER", "기타"

    result = models.ForeignKey(
        TestResult,
        on_delete=models.CASCADE,
        related_name="assets",
    )
    stored_object = models.OneToOneField(
        "assets.StoredObject",
        on_delete=models.PROTECT,
        related_name="test_result_asset",
    )
    asset_type = models.CharField(max_length=16, choices=AssetType.choices)
    display_name = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["asset_type", "created_at"]
