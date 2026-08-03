from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.appointments.models import Encounter
from apps.clinicians.models import Clinician

from .models import (
    Patient,
    PatientIdentityResolutionLog,
    ProvisionalIdentity,
)


@dataclass(frozen=True)
class IdentityResolutionResult:
    """
    신원확인 Service 처리 결과.
    """

    provisional_identity_uuid: UUID
    patient: Patient
    resolution_log: PatientIdentityResolutionLog
    resolution_type: str
    moved_encounter_count: int


def _validate_resolving_clinician(
    resolved_by: Clinician,
) -> None:
    """
    신원확인을 수행할 수 있는 의료진인지 검증한다.
    """
    if resolved_by.approval_status != (
        Clinician.ApprovalStatus.APPROVED
    ):
        raise ValidationError({
            "resolved_by": (
                "승인 완료된 의료진만 "
                "신원확인을 처리할 수 있습니다."
            ),
        })

    if not resolved_by.user.is_active:
        raise ValidationError({
            "resolved_by": (
                "비활성화된 의료진 계정은 "
                "신원확인을 처리할 수 없습니다."
            ),
        })

    if resolved_by.hospital_id is None:
        raise ValidationError({
            "resolved_by": (
                "소속 병원이 없는 의료진은 "
                "신원확인을 처리할 수 없습니다."
            ),
        })


def _get_locked_provisional_identity(
    provisional_identity_id: UUID,
) -> ProvisionalIdentity:
    """
    신원확인 중 동시 처리를 방지하기 위해
    임시 신원 행을 잠근다.
    """
    try:
        provisional_identity = (
            ProvisionalIdentity.objects
            .select_for_update()
            .get(id=provisional_identity_id)
        )
    except ProvisionalIdentity.DoesNotExist as exc:
        raise ValidationError({
            "provisional_identity": (
                "신원미상 환자 정보를 찾을 수 없습니다."
            ),
        }) from exc

    if provisional_identity.status != (
        ProvisionalIdentity.Status.UNIDENTIFIED
    ):
        raise ValidationError({
            "provisional_identity": (
                "이미 신원확인이 완료된 임시 신원입니다."
            ),
        })

    if (
        provisional_identity.resolved_patient_id is not None
        or provisional_identity.resolved_at is not None
        or provisional_identity.resolved_by_id is not None
    ):
        raise ValidationError({
            "provisional_identity": (
                "신원미상 환자의 상태와 "
                "신원확인 정보가 일치하지 않습니다."
            ),
        })

    return provisional_identity


def _get_locked_encounter_ids(
    *,
    provisional_identity: ProvisionalIdentity,
    resolved_by: Clinician,
) -> list[UUID]:
    """
    임시 신원에 연결된 진료 건을 잠그고
    처리 의료진의 소속 병원과 일치하는지 확인한다.
    """
    encounters = (
        Encounter.objects
        .select_for_update()
        .filter(
            provisional_identity=provisional_identity,
            patient__isnull=True,
        )
        .order_by("id")
    )

    encounter_ids = list(
        encounters.values_list("id", flat=True)
    )

    if not encounter_ids:
        raise ValidationError({
            "provisional_identity": (
                "신원미상 환자에게 연결된 "
                "진료 건이 존재하지 않습니다."
            ),
        })

    has_invalid_hospital = (
        Encounter.objects
        .filter(id__in=encounter_ids)
        .filter(
            Q(hospital_id__isnull=True)
            | ~Q(hospital_id=resolved_by.hospital_id)
        )
        .exists()
    )

    if has_invalid_hospital:
        raise ValidationError({
            "provisional_identity": (
                "다른 병원의 신원미상 진료 건이 포함되어 있어 "
                "현재 의료진이 처리할 수 없습니다."
            ),
        })

    return encounter_ids


def _complete_resolution(
    *,
    provisional_identity: ProvisionalIdentity,
    target_patient: Patient,
    resolved_by: Clinician,
    resolution_type: str,
    encounter_ids: list[UUID],
    note: str,
) -> IdentityResolutionResult:
    """
    Encounter 이전, 감사 로그 생성,
    ProvisionalIdentity 삭제를 완료한다.
    """
    resolved_at = timezone.now()
    provisional_identity_uuid = provisional_identity.id

    updated_count = (
        Encounter.objects
        .filter(
            id__in=encounter_ids,
            provisional_identity=provisional_identity,
            patient__isnull=True,
        )
        .update(
            patient=target_patient,
            provisional_identity=None,
            updated_at=resolved_at,
        )
    )

    if updated_count != len(encounter_ids):
        raise ValidationError({
            "provisional_identity": (
                "신원미상 진료 건 일부가 변경되어 "
                "차트 병합을 완료할 수 없습니다."
            ),
        })

    provisional_identity.status = (
        ProvisionalIdentity.Status.RESOLVED
    )
    provisional_identity.resolved_patient = target_patient
    provisional_identity.resolved_at = resolved_at
    provisional_identity.resolved_by = resolved_by

    provisional_identity.full_clean()
    provisional_identity.save(
        update_fields=[
            "status",
            "resolved_patient",
            "resolved_at",
            "resolved_by",
            "updated_at",
        ]
    )

    resolution_log = (
        PatientIdentityResolutionLog.objects.create(
            provisional_identity_uuid=(
                provisional_identity_uuid
            ),
            temporary_number=(
                provisional_identity.temporary_number
            ),
            temporary_name=(
                provisional_identity.temporary_name
            ),
            estimated_sex=(
                provisional_identity.estimated_sex
            ),
            estimated_age=(
                provisional_identity.estimated_age
            ),
            distinguishing_features=(
                provisional_identity.distinguishing_features
            ),
            resolution_type=resolution_type,
            target_patient=target_patient,
            resolved_by=resolved_by,
            resolved_at=resolved_at,
            moved_encounter_ids=[
                str(encounter_id)
                for encounter_id in encounter_ids
            ],
            moved_encounter_count=updated_count,
            note=note.strip(),
        )
    )

    # PostgreSQL Trigger가 삭제 조건을 재검증하고,
    # 삭제 시점 스냅샷을 resolution_log에 기록한다.
    provisional_identity.delete()

    resolution_log.refresh_from_db()

    if resolution_log.provisional_deleted_at is None:
        raise ValidationError({
            "provisional_identity": (
                "임시 신원 삭제 감사 로그가 "
                "정상적으로 기록되지 않았습니다."
            ),
        })

    if not resolution_log.deletion_snapshot:
        raise ValidationError({
            "provisional_identity": (
                "임시 신원 삭제 원본 스냅샷이 "
                "정상적으로 기록되지 않았습니다."
            ),
        })

    return IdentityResolutionResult(
        provisional_identity_uuid=(
            provisional_identity_uuid
        ),
        patient=target_patient,
        resolution_log=resolution_log,
        resolution_type=resolution_type,
        moved_encounter_count=updated_count,
    )


@transaction.atomic
def resolve_to_existing_patient(
    *,
    provisional_identity_id: UUID,
    target_patient_id: UUID,
    resolved_by: Clinician,
    note: str = "",
) -> IdentityResolutionResult:
    """
    신원미상 환자를 기존 Patient 차트에 병합한다.
    """
    _validate_resolving_clinician(resolved_by)

    provisional_identity = (
        _get_locked_provisional_identity(
            provisional_identity_id
        )
    )

    encounter_ids = _get_locked_encounter_ids(
        provisional_identity=provisional_identity,
        resolved_by=resolved_by,
    )

    try:
        target_patient = (
            Patient.objects
            .select_for_update()
            .get(id=target_patient_id)
        )
    except Patient.DoesNotExist as exc:
        raise ValidationError({
            "target_patient": (
                "병합 대상 기존 환자를 찾을 수 없습니다."
            ),
        }) from exc

    if target_patient.status != Patient.Status.ACTIVE:
        raise ValidationError({
            "target_patient": (
                "활성 상태의 기존 환자에게만 "
                "차트를 병합할 수 있습니다."
            ),
        })

    return _complete_resolution(
        provisional_identity=provisional_identity,
        target_patient=target_patient,
        resolved_by=resolved_by,
        resolution_type=(
            PatientIdentityResolutionLog
            .ResolutionType.EXISTING_PATIENT
        ),
        encounter_ids=encounter_ids,
        note=note,
    )


@transaction.atomic
def resolve_to_new_patient(
    *,
    provisional_identity_id: UUID,
    new_patient_data: dict[str, Any],
    resolved_by: Clinician,
    note: str = "",
) -> IdentityResolutionResult:
    """
    신원미상 환자의 정식 Patient 차트를 신규 생성하고
    기존 신원미상 진료 건을 새 차트로 이전한다.
    """
    _validate_resolving_clinician(resolved_by)

    provisional_identity = (
        _get_locked_provisional_identity(
            provisional_identity_id
        )
    )

    encounter_ids = _get_locked_encounter_ids(
        provisional_identity=provisional_identity,
        resolved_by=resolved_by,
    )

    required_fields = [
        "medical_record_number",
        "name",
        "birth_date",
        "sex",
    ]

    missing_fields = [
        field_name
        for field_name in required_fields
        if not new_patient_data.get(field_name)
    ]

    if missing_fields:
        raise ValidationError({
            field_name: "필수 항목입니다."
            for field_name in missing_fields
        })

    target_patient = Patient(
        user=None,
        medical_record_number=str(
            new_patient_data["medical_record_number"]
        ).strip(),
        name=str(
            new_patient_data["name"]
        ).strip(),
        birth_date=new_patient_data["birth_date"],
        sex=new_patient_data["sex"],
        phone=str(
            new_patient_data.get("phone", "")
        ).strip(),
        emergency_contact=str(
            new_patient_data.get(
                "emergency_contact",
                "",
            )
        ).strip(),
        address=str(
            new_patient_data.get("address", "")
        ).strip(),
        status=Patient.Status.ACTIVE,
    )

    target_patient.full_clean()
    target_patient.save()

    return _complete_resolution(
        provisional_identity=provisional_identity,
        target_patient=target_patient,
        resolved_by=resolved_by,
        resolution_type=(
            PatientIdentityResolutionLog
            .ResolutionType.NEW_PATIENT
        ),
        encounter_ids=encounter_ids,
        note=note,
    )