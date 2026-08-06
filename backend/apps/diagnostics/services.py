from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError,
)

from apps.audit_logs.models import AuditEvent
from apps.notifications.models import Notification

from .models import (
    DiagnosticReport,
    DiagnosticReportStatusHistory,
    Examination,
    ExaminationObservation,
    ExaminationStatusHistory,
)


def notify_examination_clinician(
    *,
    examination: Examination,
    title: str,
    body: str,
    event: str,
) -> Notification | None:
    recipient = None
    if (
        examination.encounter_id
        and examination.encounter.attending_clinician_id
    ):
        recipient = (
            examination.encounter
            .attending_clinician.user
        )
    elif examination.ordered_by_id:
        recipient = examination.ordered_by.user

    if recipient is None:
        return None

    return Notification.objects.create(
        recipient=recipient,
        type=Notification.Type.TEST_RESULT,
        title=title,
        body=body,
        data={
            "examination_id": str(examination.id),
            "path": f"/examinations/{examination.id}",
            "event": event,
        },
    )


@transaction.atomic
def create_examination_result(
    *,
    clinician,
    encounter,
    validated_data,
):
    observations = validated_data.pop("observations")
    report_title = validated_data.pop("report_title")
    report_summary = validated_data.pop(
        "report_summary",
        "",
    )
    report_conclusion = validated_data.pop(
        "report_conclusion",
        "",
    )
    validated_data.pop("encounter_id")
    now = timezone.now()

    examination = Examination.objects.create(
        patient=encounter.patient,
        encounter=encounter,
        hospital=encounter.hospital,
        ordered_by=clinician,
        status=Examination.Status.PRELIMINARY,
        result_available_at=now,
        **validated_data,
    )
    for sequence, observation_data in enumerate(
        observations,
        start=1,
    ):
        ExaminationObservation.objects.create(
            examination=examination,
            sequence=sequence,
            **observation_data,
        )

    report = DiagnosticReport.objects.create(
        examination=examination,
        author=clinician,
        status=DiagnosticReport.Status.DRAFT,
        title=report_title,
        summary=report_summary,
        conclusion=report_conclusion,
    )
    ExaminationStatusHistory.objects.create(
        examination=examination,
        previous_status="",
        new_status=Examination.Status.PRELIMINARY,
        changed_by=clinician.user,
    )
    DiagnosticReportStatusHistory.objects.create(
        report=report,
        previous_status="",
        new_status=DiagnosticReport.Status.DRAFT,
        changed_by=clinician.user,
    )
    AuditEvent.objects.create(
        actor=clinician.user,
        patient=encounter.patient,
        encounter=encounter,
        action=AuditEvent.Action.CREATED,
        resource_type="examination",
        resource_id=examination.id,
    )
    notify_examination_clinician(
        examination=examination,
        title="검사 결과가 등록되었습니다.",
        body=(
            f"{encounter.patient.name} 환자의 "
            f"{examination.test_name} 결과를 확인해주세요."
        ),
        event="REGISTERED",
    )
    return examination


@transaction.atomic
def finalize_examination_result(
    *,
    examination,
    clinician,
    summary,
    conclusion,
):
    examination = (
        Examination.objects
        .select_related(
            "patient",
            "encounter__attending_clinician__user",
            "ordered_by__user",
        )
        .select_for_update()
        .get(id=examination.id)
    )
    report = examination.reports.first()
    if report is None:
        raise ValidationError({
            "report": "확정할 판독 보고서가 없습니다.",
        })
    if report.author_id != clinician.id:
        raise PermissionDenied(
            "판독 보고서 작성자만 "
            "최종 결과를 확정할 수 있습니다."
        )
    if examination.status != Examination.Status.PRELIMINARY:
        raise ValidationError({
            "status": (
                "예비 결과 상태에서만 "
                "최종 확정할 수 있습니다."
            ),
        })

    now = timezone.now()
    previous_examination_status = examination.status
    previous_report_status = report.status
    examination.status = Examination.Status.FINAL
    examination.result_available_at = now
    examination.save(
        update_fields=[
            "status",
            "result_available_at",
            "updated_at",
        ]
    )
    report.status = DiagnosticReport.Status.FINAL
    report.summary = summary
    report.conclusion = conclusion
    report.issued_at = now
    report.signed_at = now
    report.signed_by = clinician.user
    report.save(
        update_fields=[
            "status",
            "summary",
            "conclusion",
            "issued_at",
            "signed_at",
            "signed_by",
            "updated_at",
        ]
    )
    ExaminationStatusHistory.objects.create(
        examination=examination,
        previous_status=previous_examination_status,
        new_status=examination.status,
        changed_by=clinician.user,
    )
    DiagnosticReportStatusHistory.objects.create(
        report=report,
        previous_status=previous_report_status,
        new_status=report.status,
        changed_by=clinician.user,
    )
    AuditEvent.objects.create(
        actor=clinician.user,
        patient=examination.patient,
        encounter=examination.encounter,
        action=AuditEvent.Action.UPDATED,
        resource_type="diagnostic_report",
        resource_id=report.id,
        metadata={"event": "FINALIZED"},
    )
    notify_examination_clinician(
        examination=examination,
        title="검사 결과가 최종 확정되었습니다.",
        body=(
            f"{examination.patient.name} 환자의 "
            f"{examination.test_name} 최종 결과를 확인해주세요."
        ),
        event="FINALIZED",
    )
    return examination


@transaction.atomic
def release_examination_result(
    *,
    examination,
    clinician,
):
    examination = (
        Examination.objects
        .select_for_update()
        .get(id=examination.id)
    )
    report = examination.reports.first()
    if report is None or report.status not in {
        DiagnosticReport.Status.FINAL,
        DiagnosticReport.Status.CORRECTED,
    }:
        raise ValidationError({
            "status": (
                "최종 또는 정정 결과만 "
                "환자에게 공개할 수 있습니다."
            ),
        })
    if report.is_released_to_patient:
        return examination

    now = timezone.now()
    report.is_released_to_patient = True
    report.released_at = now
    report.released_by = clinician.user
    report.save(
        update_fields=[
            "is_released_to_patient",
            "released_at",
            "released_by",
            "updated_at",
        ]
    )
    DiagnosticReportStatusHistory.objects.create(
        report=report,
        previous_status=report.status,
        new_status=report.status,
        changed_by=clinician.user,
        is_released_to_patient=True,
    )
    AuditEvent.objects.create(
        actor=clinician.user,
        patient=examination.patient,
        encounter=examination.encounter,
        action=AuditEvent.Action.RELEASED,
        resource_type="diagnostic_report",
        resource_id=report.id,
    )

    patient_user = examination.patient.user
    if patient_user is not None:
        Notification.objects.create(
            recipient=patient_user,
            type=Notification.Type.TEST_RESULT,
            title="검사 결과가 공개되었습니다.",
            body=(
                f"{examination.test_name} "
                "결과를 확인할 수 있습니다."
            ),
            data={
                "examination_id": str(examination.id),
                "path": f"/examinations/{examination.id}",
                "event": "RELEASED",
            },
        )

    return examination
