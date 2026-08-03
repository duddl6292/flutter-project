from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TimeStampedModel


class Appointment(TimeStampedModel):
    """환자가 향후 진료받기 위해 등록한 예약."""

    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "예약"
        CONFIRMED = "CONFIRMED", "확정"
        CHECKED_IN = "CHECKED_IN", "접수"
        COMPLETED = "COMPLETED", "완료"
        CANCELLED = "CANCELLED", "취소"
        NO_SHOW = "NO_SHOW", "미방문"

    class Duration(models.IntegerChoices):
        FIFTEEN = 15, "15분"
        THIRTY = 30, "30분"
        SIXTY = 60, "60분"

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="appointments",
    )
    clinician = models.ForeignKey(
        "clinicians.Clinician",
        on_delete=models.PROTECT,
        related_name="appointments",
    )
    department = models.ForeignKey(
        "clinicians.Department",
        on_delete=models.PROTECT,
        related_name="appointments",
    )

    hospital = models.ForeignKey(
        "hospitals.Hospital",
        on_delete=models.PROTECT,
        related_name="appointments",
        null=True,
        blank=True,
        verbose_name="진료 병원",
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="진료 위치",
        help_text="예: 본관 2층 내과 진료실",
    )

    scheduled_at = models.DateTimeField(
        db_index=True,
    )
    duration_minutes = models.PositiveSmallIntegerField(
        choices=Duration.choices,
        default=Duration.THIRTY,
        verbose_name="예약 소요시간(분)",
    )
    reason = models.TextField(
        blank=True,
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    cancellation_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["scheduled_at", "-created_at"]
        indexes = [
            models.Index(
                fields=["status", "scheduled_at"],
                name="appointment_status_date_idx",
            ),
            models.Index(
                fields=["patient", "scheduled_at"],
                name="appointment_patient_date_idx",
            ),
            models.Index(
                fields=["clinician", "scheduled_at"],
                name="appointment_clinician_date_idx",
            ),
            models.Index(
                fields=["hospital", "scheduled_at"],
                name="appointment_hospital_date_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    ~models.Q(status="CANCELLED")
                    | models.Q(cancelled_at__isnull=False)
                ),
                name="appointment_cancelled_at_required",
            ),
        ]

    def clean(self) -> None:
        super().clean()

        # 예약 진료과와 담당 의료진의 진료과 일치 확인
        if (
            self.clinician_id
            and self.department_id
            and self.clinician.department_id
            != self.department_id
        ):
            raise ValidationError(
                {
                    "department": (
                        "예약 진료과는 담당 의료진의 "
                        "진료과와 일치해야 합니다."
                    )
                }
            )

        # 예약 병원과 담당 의료진의 소속 병원 일치 확인
        if (
            self.clinician_id
            and self.hospital_id
            and self.clinician.hospital_id
            != self.hospital_id
        ):
            raise ValidationError(
                {
                    "hospital": (
                        "예약 병원은 담당 의료진의 "
                        "소속 병원과 일치해야 합니다."
                    )
                }
            )

        # 취소 상태에는 취소일시 필수
        if self.status == self.Status.CANCELLED:
            if self.cancelled_at is None:
                raise ValidationError(
                    {
                        "cancelled_at": (
                            "취소된 예약에는 "
                            "취소일시가 필요합니다."
                        )
                    }
                )

        # 취소 상태가 아니면 취소일시 입력 금지
        elif self.cancelled_at is not None:
            raise ValidationError(
                {
                    "cancelled_at": (
                        "취소 상태가 아닌 예약에는 "
                        "취소일시를 입력할 수 없습니다."
                    )
                }
            )

    def save(self, *args, **kwargs) -> None:
        # 신규 예약에서 병원이 비어 있으면
        # 담당 의료진의 현재 소속 병원을 자동 저장
        if self.hospital_id is None and self.clinician_id:
            self.hospital_id = self.clinician.hospital_id

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"Appointment #{self.pk} - "
            f"{self.scheduled_at} - {self.status}"
        )


class Encounter(TimeStampedModel):
    """환자가 실제로 내원하거나 응급실에 방문해 발생한 진료 건."""

    class EncounterType(models.TextChoices):
        OUTPATIENT = "OUTPATIENT", "외래"
        EMERGENCY = "EMERGENCY", "응급"
        INPATIENT = "INPATIENT", "입원"
        TELEMEDICINE = "TELEMEDICINE", "비대면"

    class Status(models.TextChoices):
        REGISTERED = "REGISTERED", "등록"
        ARRIVED = "ARRIVED", "도착"
        IN_PROGRESS = "IN_PROGRESS", "진료 중"
        COMPLETED = "COMPLETED", "완료"
        CANCELLED = "CANCELLED", "취소"

    encounter_number = models.CharField(
        max_length=40,
        unique=True,
    )

    # 정식 환자와 신원미상 임시환자 중 하나만 연결
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="encounters",
        null=True,
        blank=True,
    )
    provisional_identity = models.ForeignKey(
        "patients.ProvisionalIdentity",
        on_delete=models.PROTECT,
        related_name="encounters",
        null=True,
        blank=True,
    )

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.PROTECT,
        related_name="encounter",
        null=True,
        blank=True,
    )
    department = models.ForeignKey(
        "clinicians.Department",
        on_delete=models.PROTECT,
        related_name="encounters",
    )
    hospital = models.ForeignKey(
        "hospitals.Hospital",
        on_delete=models.PROTECT,
        related_name="encounters",
        null=True,
        blank=True,
        verbose_name="진료 병원",
    )
    attending_clinician = models.ForeignKey(
        "clinicians.Clinician",
        on_delete=models.PROTECT,
        related_name="attended_encounters",
    )
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="registered_encounters",
    )

    encounter_type = models.CharField(
        max_length=16,
        choices=EncounterType.choices,
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.REGISTERED,
    )

    arrived_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["status", "created_at"],
                name="encounter_status_created_idx",
            ),
            models.Index(
                fields=["patient", "created_at"],
                name="encounter_patient_created_idx",
            ),
            models.Index(
                fields=["provisional_identity", "created_at"],
                name="encounter_provisional_idx",
            ),
            models.Index(
                fields=["attending_clinician", "created_at"],
                name="encounter_clinician_idx",
            ),
            models.Index(
                fields=["hospital", "created_at"],
                name="encounter_hospital_created_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        patient__isnull=False,
                        provisional_identity__isnull=True,
                    )
                    | models.Q(
                        patient__isnull=True,
                        provisional_identity__isnull=False,
                    )
                ),
                name="encounter_exactly_one_identity",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(arrived_at__isnull=True)
                    | models.Q(started_at__isnull=True)
                    | models.Q(
                        started_at__gte=models.F("arrived_at")
                    )
                ),
                name="encounter_start_after_arrival",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(started_at__isnull=True)
                    | models.Q(completed_at__isnull=True)
                    | models.Q(
                        completed_at__gte=models.F("started_at")
                    )
                ),
                name="encounter_complete_after_start",
            ),
            models.CheckConstraint(
                condition=(
                    ~models.Q(status="COMPLETED")
                    | models.Q(completed_at__isnull=False)
                ),
                name="encounter_completed_at_required",
            ),
        ]

    def clean(self) -> None:
        super().clean()

        has_patient = self.patient_id is not None
        has_provisional_identity = (
            self.provisional_identity_id is not None
        )

        # 정식 환자 또는 임시 신원 중 하나만 연결
        if has_patient == has_provisional_identity:
            raise ValidationError(
                {
                    "patient": (
                        "정식 환자와 신원미상 임시환자 중 "
                        "하나만 연결해야 합니다."
                    ),
                    "provisional_identity": (
                        "정식 환자와 신원미상 임시환자 중 "
                        "하나만 연결해야 합니다."
                    ),
                }
            )

        # 담당 의료진과 진료과 일치 확인
        if (
            self.attending_clinician_id
            and self.department_id
            and self.attending_clinician.department_id
            != self.department_id
        ):
            raise ValidationError(
                {
                    "department": (
                        "진료과는 담당 의료진의 진료과와 "
                        "일치해야 합니다."
                    )
                }
            )

        # 담당 의료진과 실제 진료 병원 일치 확인
        if (
            self.attending_clinician_id
            and self.hospital_id
            and self.attending_clinician.hospital_id
            != self.hospital_id
        ):
            raise ValidationError(
                {
                    "hospital": (
                        "진료 병원은 담당 의료진의 "
                        "소속 병원과 일치해야 합니다."
                    )
                }
            )

        if self.appointment_id:

            # 신원미상 환자는 정식 예약과 연결 금지
            if self.provisional_identity_id is not None:
                raise ValidationError(
                    {
                        "appointment": (
                            "신원미상 임시환자는 정식 예약과 "
                            "연결할 수 없습니다."
                        )
                    }
                )

            # 예약 환자와 실제 진료 환자 일치 확인
            if self.appointment.patient_id != self.patient_id:
                raise ValidationError(
                    {
                        "patient": (
                            "진료 건의 환자는 예약 환자와 "
                            "일치해야 합니다."
                        )
                    }
                )

            # 예약 진료과와 실제 진료과 일치 확인
            if self.appointment.department_id != self.department_id:
                raise ValidationError(
                    {
                        "department": (
                            "진료 건의 진료과는 예약 진료과와 "
                            "일치해야 합니다."
                        )
                    }
                )

            # 예약 병원과 실제 진료 병원 일치 확인
            if (
                self.appointment.hospital_id
                and self.hospital_id
                and self.appointment.hospital_id
                != self.hospital_id
            ):
                raise ValidationError(
                    {
                        "hospital": (
                            "실제 진료 병원은 예약 병원과 "
                            "일치해야 합니다."
                        )
                    }
                )

            # 취소된 예약으로 실제 진료 건 생성 금지
            if self.appointment.status == Appointment.Status.CANCELLED:
                raise ValidationError(
                    {
                        "appointment": (
                            "취소된 예약으로 진료 건을 "
                            "생성할 수 없습니다."
                        )
                    }
                )

        # 도착일시보다 진료 시작일시가 빠르면 안 됨
        if (
            self.arrived_at
            and self.started_at
            and self.started_at < self.arrived_at
        ):
            raise ValidationError(
                {
                    "started_at": (
                        "진료 시작일시는 도착일시보다 "
                        "빠를 수 없습니다."
                    )
                }
            )

        # 시작일시보다 진료 완료일시가 빠르면 안 됨
        if (
            self.started_at
            and self.completed_at
            and self.completed_at < self.started_at
        ):
            raise ValidationError(
                {
                    "completed_at": (
                        "진료 완료일시는 시작일시보다 "
                        "빠를 수 없습니다."
                    )
                }
            )

        # 완료 상태에는 완료일시 필수
        if (
            self.status == self.Status.COMPLETED
            and self.completed_at is None
        ):
            raise ValidationError(
                {
                    "completed_at": (
                        "완료 상태의 진료에는 완료일시가 필요합니다."
                    )
                }
            )

    def save(self, *args, **kwargs) -> None:
        # 실제 진료 병원이 비어 있으면 자동 입력
        if self.hospital_id is None:
            # 예약이 있고 예약 병원이 저장돼 있으면 우선 사용
            if (
                self.appointment_id
                and self.appointment.hospital_id
            ):
                self.hospital_id = (
                    self.appointment.hospital_id
                )

            # 예약 병원이 없으면 담당 의료진의 소속 병원 사용
            elif self.attending_clinician_id:
                self.hospital_id = (
                    self.attending_clinician.hospital_id
                )

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.encounter_number} - {self.status}"
