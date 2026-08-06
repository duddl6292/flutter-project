from datetime import timedelta

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.clinicians.models import (
    Clinician,
    ClinicianAvailability,
    ClinicianTimeOff,
)
from apps.notifications.models import Notification

from .models import (
    Appointment,
    AppointmentStatusHistory,
    Encounter,
)


class AppointmentSchedulingError(Exception):
    """예약 가능 시간 검증 실패."""

    def __init__(self, message: str, *, field: str = "scheduled_at"):
        super().__init__(message)
        self.message = message
        self.field = field


class AppointmentStatusTransitionError(Exception):
    """허용되지 않은 예약 상태 전환."""


class EncounterWorkflowError(Exception):
    """진료 접수 또는 상태 전환 실패."""


ALLOWED_STATUS_TRANSITIONS = {
    Appointment.Status.SCHEDULED: {
        Appointment.Status.CONFIRMED,
        Appointment.Status.CANCELLED,
    },
    Appointment.Status.CONFIRMED: {
        Appointment.Status.CHECKED_IN,
        Appointment.Status.CANCELLED,
        Appointment.Status.NO_SHOW,
    },
    Appointment.Status.CHECKED_IN: {
        Appointment.Status.COMPLETED,
        Appointment.Status.CANCELLED,
    },
    Appointment.Status.COMPLETED: set(),
    Appointment.Status.CANCELLED: set(),
    Appointment.Status.NO_SHOW: set(),
}


def validate_appointment_slot(
    *,
    clinician: Clinician,
    scheduled_at,
    duration_minutes: int,
    exclude_appointment_id=None,
) -> None:
    """근무시간, 휴진 및 기존 예약과의 충돌을 확인한다."""

    requested_end = scheduled_at + timedelta(
        minutes=duration_minutes,
    )
    local_start = timezone.localtime(scheduled_at)
    local_end = timezone.localtime(requested_end)

    active_availabilities = ClinicianAvailability.objects.filter(
        clinician=clinician,
        is_active=True,
    )

    # 근무시간이 한 건이라도 등록된 의료진에게만 엄격히 적용한다.
    # 기존 의료진은 근무시간을 입력하기 전까지 종전 예약 흐름을 유지한다.
    if active_availabilities.exists():
        within_availability = (
            local_start.date() == local_end.date()
            and active_availabilities.filter(
                weekday=local_start.weekday(),
                effective_from__lte=local_start.date(),
                start_time__lte=local_start.time(),
                end_time__gte=local_end.time(),
            )
            .filter(
                Q(effective_to__isnull=True)
                | Q(effective_to__gte=local_start.date())
            )
            .exists()
        )

        if not within_availability:
            raise AppointmentSchedulingError(
                "의료진의 진료 가능 시간이 아닙니다.",
            )

    if ClinicianTimeOff.objects.filter(
        clinician=clinician,
        start_at__lt=requested_end,
        end_at__gt=scheduled_at,
    ).exists():
        raise AppointmentSchedulingError(
            "의료진의 휴진 시간과 겹칩니다.",
        )

    possible_conflicts = (
        Appointment.objects
        .filter(
            clinician=clinician,
            scheduled_at__lt=requested_end,
            scheduled_at__gte=(
                scheduled_at - timedelta(days=1)
            ),
        )
        .exclude(
            status__in=[
                Appointment.Status.CANCELLED,
                Appointment.Status.NO_SHOW,
            ],
        )
    )

    if exclude_appointment_id is not None:
        possible_conflicts = possible_conflicts.exclude(
            id=exclude_appointment_id,
        )

    for existing in possible_conflicts:
        existing_end = (
            existing.scheduled_at
            + timedelta(minutes=existing.duration_minutes)
        )

        if existing_end > scheduled_at:
            raise AppointmentSchedulingError(
                "해당 시간에는 이미 다른 예약이 있습니다.",
            )


def notify_appointment(
    *,
    appointment: Appointment,
    title: str,
    body: str,
    event: str,
) -> Notification:
    clinician_notification = Notification.objects.create(
        recipient=appointment.clinician.user,
        type=Notification.Type.APPOINTMENT,
        title=title,
        body=body,
        data={
            "appointment_id": str(appointment.id),
            "path": "/appointments",
            "event": event,
        },
    )
    patient_user = appointment.patient.user
    if patient_user is not None:
        Notification.objects.create(
            recipient=patient_user,
            type=Notification.Type.APPOINTMENT,
            title=title,
            body=body,
            data={
                "appointment_id": str(appointment.id),
                "path": "/appointments",
                "event": event,
            },
        )
    return clinician_notification


@transaction.atomic
def register_appointment_encounter(
    *,
    appointment_id,
    registered_by,
) -> tuple[Encounter, bool]:
    """오늘 예약을 담당 의료진의 진료 대기 건으로 등록한다."""
    appointment = (
        Appointment.objects
        .select_for_update(of=("self",))
        .select_related(
            "patient",
            "clinician__user",
            "department",
            "hospital",
        )
        .get(id=appointment_id)
    )

    if appointment.clinician.user_id != registered_by.id:
        raise EncounterWorkflowError(
            "본인 예약만 진료관리에 등록할 수 있습니다."
        )

    existing_encounter = Encounter.objects.filter(
        appointment=appointment,
    ).first()
    if existing_encounter is not None:
        return existing_encounter, False

    if (
        timezone.localdate(appointment.scheduled_at)
        != timezone.localdate()
    ):
        raise EncounterWorkflowError(
            "오늘 예약만 진료관리에 등록할 수 있습니다."
        )

    allowed_statuses = {
        Appointment.Status.SCHEDULED,
        Appointment.Status.CONFIRMED,
        Appointment.Status.CHECKED_IN,
    }
    if appointment.status not in allowed_statuses:
        raise EncounterWorkflowError(
            "예약·확정·접수 상태의 예약만 등록할 수 있습니다."
        )

    if appointment.status != Appointment.Status.CHECKED_IN:
        previous_status = appointment.status
        appointment.status = Appointment.Status.CHECKED_IN
        appointment.save(update_fields=["status", "updated_at"])
        AppointmentStatusHistory.objects.create(
            appointment=appointment,
            previous_status=previous_status,
            new_status=Appointment.Status.CHECKED_IN,
            changed_by=registered_by,
            reason="진료관리 등록",
        )
        notify_appointment(
            appointment=appointment,
            title="진료 접수가 완료되었습니다.",
            body=(
                f"{appointment.patient.name} 환자가 "
                "진료 대기 목록에 등록되었습니다."
            ),
            event="CHECKED_IN",
        )

    now = timezone.now()
    encounter = Encounter.objects.create(
        encounter_number=f"ENC-{appointment.id.hex}",
        patient=appointment.patient,
        appointment=appointment,
        department=appointment.department,
        hospital=appointment.hospital,
        attending_clinician=appointment.clinician,
        registered_by=registered_by,
        encounter_type=Encounter.EncounterType.OUTPATIENT,
        status=Encounter.Status.ARRIVED,
        arrived_at=now,
    )
    return encounter, True


@transaction.atomic
def create_appointment(
    *,
    patient,
    clinician_id,
    created_by,
    scheduled_at,
    duration_minutes: int,
    location: str = "",
    reason: str = "",
) -> Appointment:
    """의료진 단위 잠금 후 예약과 최초 상태 이력을 함께 생성한다."""

    clinician = (
        Clinician.objects
        .select_for_update()
        .select_related("hospital", "department")
        .get(id=clinician_id)
    )

    validate_appointment_slot(
        clinician=clinician,
        scheduled_at=scheduled_at,
        duration_minutes=duration_minutes,
    )

    appointment = Appointment.objects.create(
        patient=patient,
        clinician=clinician,
        department=clinician.department,
        hospital=clinician.hospital,
        created_by=created_by,
        scheduled_at=scheduled_at,
        duration_minutes=duration_minutes,
        location=location,
        reason=reason,
        status=Appointment.Status.SCHEDULED,
    )

    AppointmentStatusHistory.objects.create(
        appointment=appointment,
        previous_status="",
        new_status=Appointment.Status.SCHEDULED,
        changed_by=created_by,
        reason="예약 생성",
    )

    notify_appointment(
        appointment=appointment,
        title="새 예약이 등록되었습니다.",
        body=f"{patient.name} 환자의 예약을 확인해주세요.",
        event="CREATED",
    )

    return appointment


@transaction.atomic
def update_appointment(
    *,
    appointment_id,
    changed_by,
    scheduled_at,
    duration_minutes: int,
    location: str = "",
    reason: str = "",
) -> Appointment:
    appointment = (
        Appointment.objects
        .select_for_update()
        .select_related("clinician__user", "patient")
        .get(id=appointment_id)
    )

    if appointment.status in {
        Appointment.Status.COMPLETED,
        Appointment.Status.CANCELLED,
        Appointment.Status.NO_SHOW,
    }:
        raise AppointmentStatusTransitionError(
            "완료·취소·미방문 예약은 수정할 수 없습니다."
        )

    validate_appointment_slot(
        clinician=appointment.clinician,
        scheduled_at=scheduled_at,
        duration_minutes=duration_minutes,
        exclude_appointment_id=appointment.id,
    )

    appointment.scheduled_at = scheduled_at
    appointment.duration_minutes = duration_minutes
    appointment.location = location
    appointment.reason = reason
    appointment.save(
        update_fields=[
            "scheduled_at",
            "duration_minutes",
            "location",
            "reason",
            "updated_at",
        ],
    )

    notify_appointment(
        appointment=appointment,
        title="예약 정보가 변경되었습니다.",
        body=f"{appointment.patient.name} 환자의 예약 정보를 확인해주세요.",
        event="UPDATED",
    )

    return appointment


@transaction.atomic
def change_appointment_status(
    *,
    appointment_id,
    new_status: str,
    changed_by,
    reason: str = "",
    cancellation_reason: str = "",
) -> Appointment:
    """예약과 상태 이력을 하나의 트랜잭션에서 변경한다."""

    appointment = (
        Appointment.objects
        .select_related("clinician__user", "patient")
        .select_for_update()
        .get(id=appointment_id)
    )
    previous_status = appointment.status
    allowed_statuses = ALLOWED_STATUS_TRANSITIONS.get(
        previous_status,
        set(),
    )

    if new_status not in allowed_statuses:
        raise AppointmentStatusTransitionError(
            f"{previous_status}에서 {new_status}(으)로 변경할 수 없습니다."
        )

    linked_encounter = None
    if (
        previous_status == Appointment.Status.CHECKED_IN
        and new_status == Appointment.Status.CANCELLED
    ):
        linked_encounter = (
            Encounter.objects
            .select_for_update()
            .filter(appointment=appointment)
            .first()
        )
        if (
            linked_encounter is not None
            and linked_encounter.status
            not in {
                Encounter.Status.REGISTERED,
                Encounter.Status.ARRIVED,
                Encounter.Status.CANCELLED,
            }
        ):
            raise AppointmentStatusTransitionError(
                "이미 진료가 시작되었거나 완료된 예약은 취소할 수 없습니다."
            )

    appointment.status = new_status

    if new_status == Appointment.Status.CANCELLED:
        appointment.cancelled_at = timezone.now()
        appointment.cancelled_by = changed_by
        appointment.cancellation_reason = (
            cancellation_reason or reason
        )

    appointment.save()

    if (
        linked_encounter is not None
        and linked_encounter.status != Encounter.Status.CANCELLED
    ):
        linked_encounter.status = Encounter.Status.CANCELLED
        linked_encounter.save(update_fields=["status", "updated_at"])

    AppointmentStatusHistory.objects.create(
        appointment=appointment,
        previous_status=previous_status,
        new_status=new_status,
        changed_by=changed_by,
        reason=reason,
    )

    notify_appointment(
        appointment=appointment,
        title="예약 상태가 변경되었습니다.",
        body=(
            f"{appointment.patient.name} 환자의 예약이 "
            f"{appointment.get_status_display()} 상태로 변경되었습니다."
        ),
        event=f"STATUS_{new_status}",
    )

    return appointment


ENCOUNTER_STATUS_TRANSITIONS = {
    Encounter.Status.REGISTERED: set(),
    Encounter.Status.ARRIVED: {
        Encounter.Status.IN_PROGRESS,
    },
    Encounter.Status.IN_PROGRESS: {
        Encounter.Status.COMPLETED,
    },
    Encounter.Status.COMPLETED: set(),
    Encounter.Status.CANCELLED: set(),
}


@transaction.atomic
def change_encounter_status(
    *,
    encounter_id,
    new_status: str,
    changed_by,
) -> Encounter:
    encounter = (
        Encounter.objects
        .select_related("appointment")
        .select_for_update(of=("self",))
        .get(id=encounter_id)
)

    if (
        encounter.attending_clinician.user_id
        != changed_by.id
    ):
        raise EncounterWorkflowError(
            "본인 진료 건만 변경할 수 있습니다."
        )

    allowed = ENCOUNTER_STATUS_TRANSITIONS.get(
        encounter.status,
        set(),
    )

    if new_status not in allowed:
        raise EncounterWorkflowError(
            f"{encounter.status}에서 {new_status}(으)로 "
            "변경할 수 없습니다."
        )

    now = timezone.now()

    if new_status == Encounter.Status.ARRIVED:
        encounter.arrived_at = encounter.arrived_at or now

    if new_status == Encounter.Status.IN_PROGRESS:
        encounter.arrived_at = encounter.arrived_at or now
        encounter.started_at = encounter.started_at or now

    if new_status == Encounter.Status.COMPLETED:
        if not encounter.clinical_records.exists():
            raise EncounterWorkflowError(
                "진료기록을 저장한 후 진료를 완료해주세요."
            )

        encounter.started_at = encounter.started_at or now
        encounter.completed_at = now

        if (
            encounter.appointment_id
            and encounter.appointment.status
            == Appointment.Status.CHECKED_IN
        ):
            change_appointment_status(
                appointment_id=encounter.appointment_id,
                new_status=Appointment.Status.COMPLETED,
                changed_by=changed_by,
                reason="진료 완료",
            )

    encounter.status = new_status
    encounter.save()

    return encounter
