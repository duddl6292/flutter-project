from __future__ import annotations

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import (
    BooleanField,
    DateTimeField,
    Exists,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
    UUIDField,
    Value,
)
from django.utils import timezone

from apps.appointments.models import Appointment, Encounter
from apps.consultations.models import Consultation, EncounterAccessGrant

from .models import Patient


def _clinician_for(user):
    if getattr(user, "role", None) != "CLINICIAN":
        return None

    try:
        return user.clinician
    except (AttributeError, ObjectDoesNotExist):
        return None


def _hospital_appointment_exists(clinician):
    return Appointment.objects.filter(
        patient_id=OuterRef("pk"),
    ).filter(
        Q(hospital=clinician.hospital)
        | Q(
            hospital__isnull=True,
            clinician__hospital=clinician.hospital,
        )
    )


def _hospital_encounter_exists(clinician):
    return Encounter.objects.filter(
        patient_id=OuterRef("pk"),
    ).filter(
        Q(hospital=clinician.hospital)
        | Q(
            hospital__isnull=True,
            attending_clinician__hospital=clinician.hospital,
        )
    )


def _hospital_examination_exists(clinician):
    from apps.diagnostics.models import Examination

    return Examination.objects.filter(
        patient_id=OuterRef("pk"),
        hospital=clinician.hospital,
    )


def active_consultation_grants_for(clinician) -> QuerySet:
    """수락되어 진행 중인 협진의 유효한 진료 접근 권한."""
    return EncounterAccessGrant.objects.filter(
        grantee_clinician=clinician,
        consultation__status=Consultation.Status.IN_PROGRESS,
        revoked_at__isnull=True,
        expires_at__gt=timezone.now(),
    )


def accessible_patients_for_user(
    user,
    queryset: QuerySet | None = None,
    *,
    include_consultation: bool = True,
) -> QuerySet:
    """관리자, 소속 병원, 수락한 협진 범위로 환자 queryset을 제한한다."""
    patients = queryset if queryset is not None else Patient.objects.all()

    if getattr(user, "role", None) == "ADMIN":
        return patients.annotate(
            _has_hospital_appointment=Value(
                True,
                output_field=BooleanField(),
            ),
            _has_hospital_encounter=Value(
                True,
                output_field=BooleanField(),
            ),
            _has_hospital_examination=Value(
                True,
                output_field=BooleanField(),
            ),
            _shared_consultation_id=Value(
                None,
                output_field=UUIDField(null=True),
            ),
            _shared_access_expires_at=Value(
                None,
                output_field=DateTimeField(null=True),
            ),
        )

    clinician = _clinician_for(user)
    if clinician is None:
        return patients.none()

    grants = active_consultation_grants_for(clinician).filter(
        encounter__patient_id=OuterRef("pk"),
    ).order_by("expires_at")

    patients = patients.annotate(
        _has_hospital_appointment=Exists(
            _hospital_appointment_exists(clinician)
        ),
        _has_hospital_encounter=Exists(
            _hospital_encounter_exists(clinician)
        ),
        _has_hospital_examination=Exists(
            _hospital_examination_exists(clinician)
        ),
        _shared_consultation_id=Subquery(
            grants.values("consultation_id")[:1],
            output_field=UUIDField(),
        ),
        _shared_access_expires_at=Subquery(
            grants.values("expires_at")[:1],
            output_field=DateTimeField(),
        ),
    )

    own_hospital = (
        Q(_has_hospital_appointment=True)
        | Q(_has_hospital_encounter=True)
        | Q(_has_hospital_examination=True)
    )
    if include_consultation:
        return patients.filter(
            own_hospital | Q(_shared_consultation_id__isnull=False)
        )
    return patients.filter(own_hospital)


def accessible_encounters_for_user(
    user,
    queryset: QuerySet | None = None,
    *,
    include_consultation: bool = True,
) -> QuerySet:
    encounters = queryset if queryset is not None else Encounter.objects.all()

    if getattr(user, "role", None) == "ADMIN":
        return encounters

    clinician = _clinician_for(user)
    if clinician is None:
        return encounters.none()

    hospital_scope = (
        Q(hospital=clinician.hospital)
        | Q(
            hospital__isnull=True,
            attending_clinician__hospital=clinician.hospital,
        )
    )
    if not include_consultation:
        return encounters.filter(hospital_scope)

    grant_encounters = active_consultation_grants_for(
        clinician
    ).values("encounter_id")
    return encounters.filter(
        hospital_scope | Q(id__in=grant_encounters)
    )


def patient_access_scope(patient: Patient) -> str | None:
    if (
        getattr(patient, "_has_hospital_appointment", False)
        or getattr(patient, "_has_hospital_encounter", False)
        or getattr(patient, "_has_hospital_examination", False)
    ):
        return "HOSPITAL"
    if getattr(patient, "_shared_consultation_id", None):
        return "CONSULTATION"
    return None
