from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TimeStampedModel


class Consultation(TimeStampedModel):
    """하나의 진료 건에 대한 의료진 간 협진 요청과 답변."""

    class Status(models.TextChoices):
        REQUESTED = "REQUESTED", "협진 요청"
        IN_PROGRESS = "IN_PROGRESS", "협진 진행 중"
        COMPLETED = "COMPLETED", "협진 완료"
        CANCELLED = "CANCELLED", "협진 취소"

    encounter = models.ForeignKey(
        "appointments.Encounter",
        on_delete=models.PROTECT,
        related_name="consultations",
        verbose_name="진료 건",
    )
    requester_clinician = models.ForeignKey(
        "clinicians.Clinician",
        on_delete=models.PROTECT,
        related_name="requested_consultations",
        verbose_name="협진 요청 의료진",
    )
    consultant_clinician = models.ForeignKey(
        "clinicians.Clinician",
        on_delete=models.PROTECT,
        related_name="received_consultations",
        verbose_name="협진 담당 의료진",
    )

    question = models.TextField(
        verbose_name="협진 요청 내용",
    )
    response = models.TextField(
        blank=True,
        verbose_name="협진 답변",
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.REQUESTED,
        db_index=True,
        verbose_name="협진 상태",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="협진 완료 일시",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["encounter", "status"],
                name="consult_encounter_status_idx",
            ),
            models.Index(
                fields=[
                    "requester_clinician",
                    "created_at",
                ],
                name="consult_requester_date_idx",
            ),
            models.Index(
                fields=[
                    "consultant_clinician",
                    "status",
                ],
                name="consult_consultant_status_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(
                    requester_clinician=models.F(
                        "consultant_clinician"
                    )
                ),
                name="consultation_different_clinicians",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        status="COMPLETED",
                        completed_at__isnull=False,
                    )
                    | (
                        ~models.Q(status="COMPLETED")
                        & models.Q(
                            completed_at__isnull=True
                        )
                    )
                ),
                name="consultation_completed_at_valid",
            ),
            models.CheckConstraint(
                condition=(
                    ~models.Q(status="COMPLETED")
                    | ~models.Q(response="")
                ),
                name="consultation_response_required",
            ),
        ]
        verbose_name = "협진"
        verbose_name_plural = "협진"

    def clean(self) -> None:
        super().clean()

        if (
            self.requester_clinician_id
            and self.consultant_clinician_id
            and self.requester_clinician_id
            == self.consultant_clinician_id
        ):
            raise ValidationError(
                {
                    "consultant_clinician": (
                        "협진 요청 의료진과 담당 의료진은 "
                        "서로 달라야 합니다."
                    )
                }
            )

        if self.status == self.Status.COMPLETED:
            if not self.response.strip():
                raise ValidationError(
                    {
                        "response": (
                            "협진 완료 상태에는 "
                            "협진 답변이 필요합니다."
                        )
                    }
                )

            if self.completed_at is None:
                raise ValidationError(
                    {
                        "completed_at": (
                            "협진 완료 상태에는 "
                            "완료 일시가 필요합니다."
                        )
                    }
                )
        elif self.completed_at is not None:
            raise ValidationError(
                {
                    "completed_at": (
                        "협진 완료 상태가 아니면 "
                        "완료 일시를 입력할 수 없습니다."
                    )
                }
            )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"Consultation #{self.pk} - "
            f"{self.status}"
        )