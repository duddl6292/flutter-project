from datetime import timedelta

from django.db import transaction

from apps.appointments.models import Appointment

from .models import (
    Clinician,
    ClinicianAvailability,
    ClinicianTimeOff,
)


class ClinicianTimeOffConflictError(Exception):
    """휴진 시간에 기존 예약이 존재함."""

    def __init__(self, appointment_ids):
        self.appointment_ids = list(appointment_ids)
        super().__init__(
            "휴진 시간에 기존 예약이 있어 먼저 조정해야 합니다."
        )


@transaction.atomic
def create_clinician_availability(
    *,
    clinician_id,
    weekday: int,
    start_time,
    end_time,
    effective_from,
    effective_to=None,
) -> ClinicianAvailability:
    """의료진 단위 잠금 후 중복되지 않는 근무시간을 생성한다."""

    clinician = (
        Clinician.objects
        .select_for_update()
        .get(id=clinician_id)
    )

    return ClinicianAvailability.objects.create(
        clinician=clinician,
        weekday=weekday,
        start_time=start_time,
        end_time=end_time,
        effective_from=effective_from,
        effective_to=effective_to,
    )


@transaction.atomic
def create_clinician_time_off(
    *,
    clinician_id,
    start_at,
    end_at,
    created_by,
    reason: str = "",
) -> ClinicianTimeOff:
    """기존 예약 충돌 확인 후 의료진 휴진을 생성한다."""

    clinician = (
        Clinician.objects
        .select_for_update()
        .get(id=clinician_id)
    )

    possible_conflicts = (
        Appointment.objects
        .filter(
            clinician=clinician,
            scheduled_at__lt=end_at,
            scheduled_at__gte=start_at - timedelta(days=1),
        )
        .exclude(
            status__in=[
                Appointment.Status.CANCELLED,
                Appointment.Status.NO_SHOW,
            ],
        )
    )

    conflicting_ids = []

    for appointment in possible_conflicts:
        appointment_end = (
            appointment.scheduled_at
            + timedelta(minutes=appointment.duration_minutes)
        )

        if appointment_end > start_at:
            conflicting_ids.append(appointment.id)

    if conflicting_ids:
        raise ClinicianTimeOffConflictError(conflicting_ids)

    return ClinicianTimeOff.objects.create(
        clinician=clinician,
        start_at=start_at,
        end_at=end_at,
        reason=reason,
        created_by=created_by,
    )
