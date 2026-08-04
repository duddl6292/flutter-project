from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel


class Consultation(TimeStampedModel):
    """하나의 진료 건에 대한 의료진 간 협진 요청과 답변."""

    class Status(models.TextChoices):
        REQUESTED = "REQUESTED", "협진 요청"
        IN_PROGRESS = "IN_PROGRESS", "협진 진행 중"
        COMPLETED = "COMPLETED", "협진 완료"
        CANCELLED = "CANCELLED", "협진 취소"

    class Priority(models.TextChoices):
        ROUTINE = "ROUTINE", "일반"
        URGENT = "URGENT", "긴급"
        EMERGENCY = "EMERGENCY", "응급"

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

    subject = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="협진 제목",
    )
    priority = models.CharField(
        max_length=16,
        choices=Priority.choices,
        default=Priority.ROUTINE,
        db_index=True,
        verbose_name="우선순위",
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
    due_at = models.DateTimeField(null=True, blank=True, db_index=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="cancelled_consultations",
        null=True,
        blank=True,
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

        if self.status == self.Status.CANCELLED:
            if self.cancelled_at is None or self.cancelled_by_id is None:
                raise ValidationError("취소된 협진에는 취소 일시와 취소자가 필요합니다.")
        elif self.cancelled_at is not None or self.cancelled_by_id is not None:
            raise ValidationError("취소 상태가 아닌 협진에는 취소 정보를 입력할 수 없습니다.")

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"Consultation #{self.pk} - "
            f"{self.status}"
        )


class ConsultationParticipant(TimeStampedModel):
    """다자 협진 참여 의료진과 읽음 상태."""

    class Role(models.TextChoices):
        REQUESTER = "REQUESTER", "요청자"
        CONSULTANT = "CONSULTANT", "협진자"
        OBSERVER = "OBSERVER", "참관자"

    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name="participants",
    )
    clinician = models.ForeignKey(
        "clinicians.Clinician",
        on_delete=models.PROTECT,
        related_name="consultation_participations",
    )
    role = models.CharField(max_length=16, choices=Role.choices)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="added_consultation_participants",
    )
    joined_at = models.DateTimeField(default=timezone.now)
    left_at = models.DateTimeField(null=True, blank=True)
    last_read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["joined_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["consultation", "clinician"],
                name="consult_participant_uniq",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(left_at__isnull=True)
                    | models.Q(left_at__gte=models.F("joined_at"))
                ),
                name="consult_participant_left_valid",
            ),
        ]


class ConsultationMessage(TimeStampedModel):
    """협진 안에서 의료진이 주고받는 순차 메시지."""

    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        "clinicians.Clinician",
        on_delete=models.PROTECT,
        related_name="consultation_messages",
        null=True,
        blank=True,
    )
    sequence = models.PositiveIntegerField()
    content = models.TextField()
    is_system = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["sequence"]
        constraints = [
            models.UniqueConstraint(
                fields=["consultation", "sequence"],
                name="consult_message_seq_uniq",
            ),
            models.CheckConstraint(
                condition=models.Q(sequence__gte=1),
                name="consult_message_seq_positive",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(is_system=True, sender__isnull=True)
                    | models.Q(is_system=False, sender__isnull=False)
                ),
                name="consult_message_sender_valid",
            ),
        ]


class ConsultationAttachment(TimeStampedModel):
    """협진 메시지에 첨부된 파일·영상·AI 결과·공식 결과."""

    message = models.ForeignKey(
        ConsultationMessage,
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    stored_object = models.ForeignKey(
        "assets.StoredObject",
        on_delete=models.PROTECT,
        related_name="consultation_attachments",
        null=True,
        blank=True,
    )
    imaging_study = models.ForeignKey(
        "imaging.ImagingStudy",
        on_delete=models.PROTECT,
        related_name="consultation_attachments",
        null=True,
        blank=True,
    )
    inference_result = models.ForeignKey(
        "ct_analysis.InferenceResult",
        on_delete=models.PROTECT,
        related_name="consultation_attachments",
        null=True,
        blank=True,
    )
    test_result = models.ForeignKey(
        "test_results.TestResult",
        on_delete=models.PROTECT,
        related_name="consultation_attachments",
        null=True,
        blank=True,
    )
    display_name = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        stored_object__isnull=False,
                        imaging_study__isnull=True,
                        inference_result__isnull=True,
                        test_result__isnull=True,
                    )
                    | models.Q(
                        stored_object__isnull=True,
                        imaging_study__isnull=False,
                        inference_result__isnull=True,
                        test_result__isnull=True,
                    )
                    | models.Q(
                        stored_object__isnull=True,
                        imaging_study__isnull=True,
                        inference_result__isnull=False,
                        test_result__isnull=True,
                    )
                    | models.Q(
                        stored_object__isnull=True,
                        imaging_study__isnull=True,
                        inference_result__isnull=True,
                        test_result__isnull=False,
                    )
                ),
                name="consult_attachment_one_source",
            ),
        ]


class ConsultationStatusHistory(TimeStampedModel):
    """협진 상태 변경 이력."""

    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.PROTECT,
        related_name="status_history",
    )
    previous_status = models.CharField(max_length=16, blank=True)
    new_status = models.CharField(max_length=16, choices=Consultation.Status.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="consultation_status_changes",
    )
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(
                fields=["consultation", "created_at"],
                name="consulthist_consult_date_idx",
            ),
        ]


class EncounterAccessGrant(TimeStampedModel):
    """협진 참여자에게 특정 진료 건 접근 권한을 한시적으로 부여한다."""

    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name="access_grants",
    )
    encounter = models.ForeignKey(
        "appointments.Encounter",
        on_delete=models.PROTECT,
        related_name="consultation_access_grants",
    )
    grantee_clinician = models.ForeignKey(
        "clinicians.Clinician",
        on_delete=models.PROTECT,
        related_name="encounter_access_grants",
    )
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="granted_encounter_access",
    )
    permissions = models.JSONField(default=list, blank=True)
    expires_at = models.DateTimeField(db_index=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="revoked_encounter_access",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["consultation", "grantee_clinician"],
                condition=models.Q(revoked_at__isnull=True),
                name="consult_active_grant_uniq",
            ),
            models.CheckConstraint(
                condition=models.Q(expires_at__gt=models.F("created_at")),
                name="consult_grant_expiry_valid",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(revoked_at__isnull=True, revoked_by__isnull=True)
                    | models.Q(revoked_at__isnull=False, revoked_by__isnull=False)
                ),
                name="consult_grant_revoke_valid",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if self.consultation_id and self.encounter_id != self.consultation.encounter_id:
            raise ValidationError({"encounter": "협진과 접근 권한의 진료 건이 일치해야 합니다."})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
