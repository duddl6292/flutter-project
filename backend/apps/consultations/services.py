from datetime import timedelta

from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError,
)

from apps.notifications.models import Notification

from .models import (
    Consultation,
    ConsultationMessage,
    ConsultationParticipant,
    ConsultationStatusHistory,
    EncounterAccessGrant,
)


GRANT_PERMISSIONS = [
    "READ_ENCOUNTER_SUMMARY",
    "READ_CLINICAL_RECORD",
    "READ_TEST_RESULTS",
    "READ_IMAGING",
]


def notify_consultation(
    *,
    recipient,
    consultation,
    title,
    body,
    event,
    actor_name="",
):
    return Notification.objects.create(
        recipient=recipient,
        type=Notification.Type.CONSULTATION,
        title=title,
        body=body,
        data={
            "consultation_id": str(
                consultation.id
            ),
            "path": (
                "/consultations/"
                f"{consultation.id}"
            ),
            "event": event,
            "actor_name": actor_name,
        },
    )


def add_status_history(
    *,
    consultation,
    previous_status,
    changed_by,
    reason="",
):
    return ConsultationStatusHistory.objects.create(
        consultation=consultation,
        previous_status=previous_status,
        new_status=consultation.status,
        changed_by=changed_by,
        reason=reason,
    )


def add_message(
    *,
    consultation,
    sender,
    content,
    is_system=False,
):
    last_sequence = (
        ConsultationMessage.objects
        .filter(consultation=consultation)
        .aggregate(value=Max("sequence"))["value"]
        or 0
    )

    return ConsultationMessage.objects.create(
        consultation=consultation,
        sender=None if is_system else sender,
        sequence=last_sequence + 1,
        content=content,
        is_system=is_system,
    )


@transaction.atomic
def create_consultation(
    *,
    requester,
    consultant,
    encounter,
    subject,
    priority,
    question,
    due_at,
):
    consultation = Consultation.objects.create(
        encounter=encounter,
        requester_clinician=requester,
        consultant_clinician=consultant,
        subject=subject,
        priority=priority,
        question=question,
        due_at=due_at,
    )
    now = timezone.now()

    ConsultationParticipant.objects.create(
        consultation=consultation,
        clinician=requester,
        role=(
            ConsultationParticipant.Role.REQUESTER
        ),
        added_by=requester.user,
        last_read_at=now,
    )
    ConsultationParticipant.objects.create(
        consultation=consultation,
        clinician=consultant,
        role=(
            ConsultationParticipant.Role.CONSULTANT
        ),
        added_by=requester.user,
    )
    add_message(
        consultation=consultation,
        sender=requester,
        content=question,
    )
    add_status_history(
        consultation=consultation,
        previous_status="",
        changed_by=requester.user,
    )

    grant_expiry = (
        due_at
        if due_at is not None
        else now + timedelta(days=30)
    )
    if grant_expiry <= now:
        grant_expiry = now + timedelta(days=1)

    EncounterAccessGrant.objects.create(
        consultation=consultation,
        encounter=encounter,
        grantee_clinician=consultant,
        granted_by=requester.user,
        permissions=GRANT_PERMISSIONS,
        expires_at=grant_expiry,
    )
    notify_consultation(
        recipient=consultant.user,
        consultation=consultation,
        title="새 협진 요청",
        body=(
            f"{requester.name} 의료진이 "
            "협진을 요청했습니다."
        ),
        event="REQUESTED",
        actor_name=requester.name,
    )

    return consultation


def require_active_participant(
    *,
    consultation,
    clinician,
):
    try:
        return consultation.participants.get(
            clinician=clinician,
            left_at__isnull=True,
        )
    except ConsultationParticipant.DoesNotExist as exc:
        raise PermissionDenied(
            "이 협진에 참여한 의료진만 "
            "접근할 수 있습니다."
        ) from exc


@transaction.atomic
def accept_consultation(
    *,
    consultation,
    clinician,
):
    consultation = (
        Consultation.objects
        .select_for_update()
        .get(id=consultation.id)
    )

    if (
        consultation.consultant_clinician_id
        != clinician.id
    ):
        raise PermissionDenied(
            "협진 담당 의료진만 "
            "요청을 수락할 수 있습니다."
        )
    if consultation.status != Consultation.Status.REQUESTED:
        raise ValidationError({
            "status": (
                "요청 상태의 협진만 "
                "수락할 수 있습니다."
            ),
        })

    previous_status = consultation.status
    consultation.status = Consultation.Status.IN_PROGRESS
    consultation.accepted_at = timezone.now()
    consultation.save(
        update_fields=[
            "status",
            "accepted_at",
            "updated_at",
        ]
    )
    add_status_history(
        consultation=consultation,
        previous_status=previous_status,
        changed_by=clinician.user,
    )
    add_message(
        consultation=consultation,
        sender=None,
        content=(
            f"{clinician.name} 의료진이 "
            "협진 요청을 수락했습니다."
        ),
        is_system=True,
    )
    notify_consultation(
        recipient=(
            consultation.requester_clinician.user
        ),
        consultation=consultation,
        title="협진 요청 수락",
        body=(
            f"{clinician.name} 의료진이 "
            "협진 요청을 수락했습니다."
        ),
        event="ACCEPTED",
        actor_name=clinician.name,
    )

    return consultation


@transaction.atomic
def add_consultation_message(
    *,
    consultation,
    clinician,
    content,
):
    consultation = (
        Consultation.objects
        .select_for_update()
        .get(id=consultation.id)
    )
    require_active_participant(
        consultation=consultation,
        clinician=clinician,
    )

    if consultation.status in {
        Consultation.Status.COMPLETED,
        Consultation.Status.CANCELLED,
    }:
        raise ValidationError({
            "status": (
                "완료되거나 취소된 협진에는 "
                "메시지를 작성할 수 없습니다."
            ),
        })

    message = add_message(
        consultation=consultation,
        sender=clinician,
        content=content,
    )
    recipient = (
        consultation.consultant_clinician.user
        if (
            clinician.id
            == consultation.requester_clinician_id
        )
        else consultation.requester_clinician.user
    )
    notify_consultation(
        recipient=recipient,
        consultation=consultation,
        title="새 협진 메시지",
        body=f"{clinician.name}: {content[:80]}",
        event="MESSAGE",
        actor_name=clinician.name,
    )

    return message


def revoke_access_grants(
    *,
    consultation,
    revoked_by,
):
    now = timezone.now()
    consultation.access_grants.filter(
        revoked_at__isnull=True,
    ).update(
        revoked_at=now,
        revoked_by=revoked_by,
        updated_at=now,
    )


@transaction.atomic
def complete_consultation(
    *,
    consultation,
    clinician,
    response,
):
    consultation = (
        Consultation.objects
        .select_for_update()
        .get(id=consultation.id)
    )

    if (
        consultation.consultant_clinician_id
        != clinician.id
    ):
        raise PermissionDenied(
            "협진 담당 의료진만 "
            "최종 답변을 등록할 수 있습니다."
        )
    if (
        consultation.status
        != Consultation.Status.IN_PROGRESS
    ):
        raise ValidationError({
            "status": (
                "진행 중인 협진만 "
                "완료할 수 있습니다."
            ),
        })

    previous_status = consultation.status
    consultation.status = Consultation.Status.COMPLETED
    consultation.response = response
    consultation.completed_at = timezone.now()
    consultation.save(
        update_fields=[
            "status",
            "response",
            "completed_at",
            "updated_at",
        ]
    )
    add_message(
        consultation=consultation,
        sender=clinician,
        content=response,
    )
    add_status_history(
        consultation=consultation,
        previous_status=previous_status,
        changed_by=clinician.user,
    )
    revoke_access_grants(
        consultation=consultation,
        revoked_by=clinician.user,
    )
    notify_consultation(
        recipient=(
            consultation.requester_clinician.user
        ),
        consultation=consultation,
        title="협진 답변 완료",
        body=(
            f"{clinician.name} 의료진이 "
            "최종 협진 답변을 등록했습니다."
        ),
        event="COMPLETED",
        actor_name=clinician.name,
    )

    return consultation


@transaction.atomic
def cancel_consultation(
    *,
    consultation,
    clinician,
    reason="",
):
    consultation = (
        Consultation.objects
        .select_for_update()
        .get(id=consultation.id)
    )

    if (
        consultation.requester_clinician_id
        != clinician.id
    ):
        raise PermissionDenied(
            "협진 요청 의료진만 "
            "협진을 취소할 수 있습니다."
        )
    if consultation.status not in {
        Consultation.Status.REQUESTED,
        Consultation.Status.IN_PROGRESS,
    }:
        raise ValidationError({
            "status": (
                "요청 또는 진행 중인 협진만 "
                "취소할 수 있습니다."
            ),
        })

    previous_status = consultation.status
    consultation.status = Consultation.Status.CANCELLED
    consultation.cancelled_at = timezone.now()
    consultation.cancelled_by = clinician.user
    consultation.save(
        update_fields=[
            "status",
            "cancelled_at",
            "cancelled_by",
            "updated_at",
        ]
    )
    add_status_history(
        consultation=consultation,
        previous_status=previous_status,
        changed_by=clinician.user,
        reason=reason,
    )
    add_message(
        consultation=consultation,
        sender=None,
        content=(
            "협진 요청이 취소되었습니다."
            + (
                f" 사유: {reason}"
                if reason
                else ""
            )
        ),
        is_system=True,
    )
    revoke_access_grants(
        consultation=consultation,
        revoked_by=clinician.user,
    )
    notify_consultation(
        recipient=(
            consultation.consultant_clinician.user
        ),
        consultation=consultation,
        title="협진 요청 취소",
        body=(
            f"{clinician.name} 의료진이 "
            "협진 요청을 취소했습니다."
        ),
        event="CANCELLED",
        actor_name=clinician.name,
    )

    return consultation
