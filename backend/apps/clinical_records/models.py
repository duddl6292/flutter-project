from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel


class ClinicalRecord(TimeStampedModel):
    """진료 건에 대한 의료진의 SOAP 진료기록."""

    encounter = models.ForeignKey(
        "appointments.Encounter",
        on_delete=models.PROTECT,
        related_name="clinical_records",
        verbose_name="진료 건",
    )
    clinician = models.ForeignKey(
        "clinicians.Clinician",
        on_delete=models.PROTECT,
        related_name="clinical_records",
        verbose_name="작성 의료진",
    )
    recorded_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="기록 일시",
    )

    chief_complaint = models.TextField(
        blank=True,
        verbose_name="주호소",
    )
    subjective = models.TextField(
        blank=True,
        verbose_name="주관적 정보",
    )
    objective = models.TextField(
        blank=True,
        verbose_name="객관적 정보",
    )
    assessment = models.TextField(
        blank=True,
        verbose_name="평가",
    )
    plan = models.TextField(
        blank=True,
        verbose_name="계획",
    )
    patient_visible_summary = models.TextField(
        blank=True,
        verbose_name="환자 공개 요약",
    )

    class Meta:
        ordering = ["-recorded_at", "-created_at"]
        indexes = [
            models.Index(
                fields=["encounter", "recorded_at"],
                name="clinicalrec_encounter_idx",
            ),
            models.Index(
                fields=["clinician", "recorded_at"],
                name="clinicalrec_clinician_idx",
            ),
        ]
        verbose_name = "진료기록"
        verbose_name_plural = "진료기록"

    def clean(self) -> None:
        super().clean()

        if (
            self.encounter_id
            and self.clinician_id
            and self.encounter.department_id
            != self.clinician.department_id
        ):
            raise ValidationError(
                {
                    "clinician": (
                        "진료기록 작성 의료진의 진료과와 "
                        "진료 건의 진료과가 일치해야 합니다."
                    )
                }
            )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"ClinicalRecord #{self.pk} - "
            f"{self.encounter.encounter_number}"
        )