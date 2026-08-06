from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.appointments.models import Encounter
from apps.audit_logs.models import AuditEvent
from apps.clinicians.permissions import (
    IsApprovedClinicianOrAdmin,
)
from apps.core.pagination import CommonPageNumberPagination
from apps.patients.permissions import IsClinician

from .models import Consultation
from .serializers import (
    ConsultationCancelSerializer,
    ConsultationCompleteSerializer,
    ConsultationCreateSerializer,
    ConsultationMessageCreateSerializer,
    ConsultationMessageSerializer,
    ConsultationSerializer,
)
from .services import (
    accept_consultation,
    add_consultation_message,
    cancel_consultation,
    complete_consultation,
    create_consultation,
    require_active_participant,
)


def clinician_consultations(request):
    return (
        Consultation.objects
        .filter(
            participants__clinician=(
                request.user.clinician
            ),
            participants__left_at__isnull=True,
            encounter__patient__isnull=False,
        )
        .select_related(
            "encounter",
            "encounter__patient",
            "encounter__department",
            "requester_clinician",
            "requester_clinician__department",
            "requester_clinician__hospital",
            "consultant_clinician",
            "consultant_clinician__department",
            "consultant_clinician__hospital",
        )
        .prefetch_related(
            "participants",
            "participants__clinician",
            "participants__clinician__department",
            "participants__clinician__hospital",
            "messages",
            "messages__sender",
            "messages__sender__department",
            "messages__sender__hospital",
            "messages__attachments",
            "status_history",
            "status_history__changed_by",
            "status_history__changed_by__clinician",
        )
        .distinct()
    )


def serialize_consultation(
    request,
    consultation,
):
    consultation = clinician_consultations(
        request
    ).get(id=consultation.id)

    return ConsultationSerializer(
        consultation,
        context={"request": request},
    ).data


class ConsultationListCreateView(APIView):
    permission_classes = [
        IsClinician,
        IsApprovedClinicianOrAdmin,
    ]

    def get(self, request):
        consultations = clinician_consultations(
            request
        )
        box = (
            request.query_params
            .get("box", "all")
            .strip()
            .lower()
        )
        requested_status = (
            request.query_params
            .get("status", "")
            .strip()
            .upper()
        )
        requested_priority = (
            request.query_params
            .get("priority", "")
            .strip()
            .upper()
        )
        search = (
            request.query_params
            .get("search", "")
            .strip()
        )

        if box not in {
            "all",
            "received",
            "sent",
        }:
            raise ValidationError({
                "box": "올바른 협진함이 아닙니다.",
            })
        if box == "received":
            consultations = consultations.filter(
                consultant_clinician=(
                    request.user.clinician
                ),
            )
        elif box == "sent":
            consultations = consultations.filter(
                requester_clinician=(
                    request.user.clinician
                ),
            )

        valid_statuses = {
            value
            for value, _label
            in Consultation.Status.choices
        }
        if (
            requested_status
            and requested_status not in valid_statuses
        ):
            raise ValidationError({
                "status": "올바른 협진 상태가 아닙니다.",
            })
        if requested_status:
            consultations = consultations.filter(
                status=requested_status,
            )

        valid_priorities = {
            value
            for value, _label
            in Consultation.Priority.choices
        }
        if (
            requested_priority
            and requested_priority
            not in valid_priorities
        ):
            raise ValidationError({
                "priority": (
                    "올바른 우선순위가 아닙니다."
                ),
            })
        if requested_priority:
            consultations = consultations.filter(
                priority=requested_priority,
            )

        if search:
            consultations = consultations.filter(
                Q(subject__icontains=search)
                | Q(question__icontains=search)
                | Q(
                    encounter__patient__name__icontains=(
                        search
                    )
                )
                | Q(
                    encounter__patient__medical_record_number__icontains=(
                        search
                    )
                )
                | Q(
                    requester_clinician__name__icontains=(
                        search
                    )
                )
                | Q(
                    consultant_clinician__name__icontains=(
                        search
                    )
                )
            )

        paginator = CommonPageNumberPagination()
        page = paginator.paginate_queryset(
            consultations,
            request,
            view=self,
        )
        serializer = ConsultationSerializer(
            page,
            many=True,
            context={"request": request},
        )

        return paginator.get_paginated_response(
            serializer.data
        )

    def post(self, request):
        serializer = ConsultationCreateSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        consultation = create_consultation(
            requester=request.user.clinician,
            consultant=serializer.context[
                "consultant"
            ],
            encounter=serializer.context[
                "encounter"
            ],
            subject=data["subject"],
            priority=data["priority"],
            question=data["question"],
            due_at=data.get("due_at"),
        )

        return Response(
            {
                "data": serialize_consultation(
                    request,
                    consultation,
                ),
            },
            status=status.HTTP_201_CREATED,
        )


class ConsultationContextListView(APIView):
    permission_classes = [
        IsClinician,
        IsApprovedClinicianOrAdmin,
    ]

    def get(self, request):
        search = (
            request.query_params
            .get("search", "")
            .strip()
        )
        encounters = (
            Encounter.objects
            .filter(
                attending_clinician=(
                    request.user.clinician
                ),
                patient__isnull=False,
            )
            .select_related(
                "patient",
                "department",
            )
        )

        if search:
            encounters = encounters.filter(
                Q(patient__name__icontains=search)
                | Q(
                    patient__medical_record_number__icontains=(
                        search
                    )
                )
                | Q(encounter_number__icontains=search)
            )

        return Response({
            "data": [
                {
                    "encounter_id": str(encounter.id),
                    "encounter_number": (
                        encounter.encounter_number
                    ),
                    "patient_id": str(
                        encounter.patient_id
                    ),
                    "patient_number": (
                        encounter.patient
                        .medical_record_number
                    ),
                    "patient_name": (
                        encounter.patient.name
                    ),
                    "department_name": (
                        encounter.department.name
                    ),
                    "created_at": encounter.created_at,
                }
                for encounter in encounters.order_by(
                    "-created_at"
                )[:100]
            ],
        })


class ConsultationDetailView(APIView):
    permission_classes = [
        IsClinician,
        IsApprovedClinicianOrAdmin,
    ]

    def get(self, request, consultation_id):
        consultation = get_object_or_404(
            clinician_consultations(request),
            id=consultation_id,
        )
        participant = require_active_participant(
            consultation=consultation,
            clinician=request.user.clinician,
        )
        participant.last_read_at = timezone.now()
        participant.save(
            update_fields=[
                "last_read_at",
                "updated_at",
            ]
        )
        AuditEvent.objects.create(
            actor=request.user,
            patient=consultation.encounter.patient,
            encounter=consultation.encounter,
            action=AuditEvent.Action.VIEWED,
            resource_type="consultation",
            resource_id=consultation.id,
        )

        consultation = clinician_consultations(
            request
        ).get(id=consultation.id)

        return Response({
            "data": ConsultationSerializer(
                consultation,
                context={"request": request},
            ).data,
        })


class ConsultationAcceptView(APIView):
    permission_classes = [
        IsClinician,
        IsApprovedClinicianOrAdmin,
    ]

    def post(self, request, consultation_id):
        consultation = get_object_or_404(
            clinician_consultations(request),
            id=consultation_id,
        )
        consultation = accept_consultation(
            consultation=consultation,
            clinician=request.user.clinician,
        )

        return Response({
            "data": serialize_consultation(
                request,
                consultation,
            ),
        })


class ConsultationMessageListCreateView(APIView):
    permission_classes = [
        IsClinician,
        IsApprovedClinicianOrAdmin,
    ]

    def post(self, request, consultation_id):
        consultation = get_object_or_404(
            clinician_consultations(request),
            id=consultation_id,
        )
        serializer = (
            ConsultationMessageCreateSerializer(
                data=request.data,
            )
        )
        serializer.is_valid(raise_exception=True)
        message = add_consultation_message(
            consultation=consultation,
            clinician=request.user.clinician,
            content=(
                serializer.validated_data["content"]
            ),
        )

        return Response(
            {
                "data": ConsultationMessageSerializer(
                    message
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )


class ConsultationCompleteView(APIView):
    permission_classes = [
        IsClinician,
        IsApprovedClinicianOrAdmin,
    ]

    def post(self, request, consultation_id):
        consultation = get_object_or_404(
            clinician_consultations(request),
            id=consultation_id,
        )
        serializer = ConsultationCompleteSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        consultation = complete_consultation(
            consultation=consultation,
            clinician=request.user.clinician,
            response=(
                serializer.validated_data["response"]
            ),
        )

        return Response({
            "data": serialize_consultation(
                request,
                consultation,
            ),
        })


class ConsultationCancelView(APIView):
    permission_classes = [
        IsClinician,
        IsApprovedClinicianOrAdmin,
    ]

    def post(self, request, consultation_id):
        consultation = get_object_or_404(
            clinician_consultations(request),
            id=consultation_id,
        )
        serializer = ConsultationCancelSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        consultation = cancel_consultation(
            consultation=consultation,
            clinician=request.user.clinician,
            reason=(
                serializer.validated_data
                .get("reason", "")
                .strip()
            ),
        )

        return Response({
            "data": serialize_consultation(
                request,
                consultation,
            ),
        })
