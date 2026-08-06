from django.db.models import Q
from uuid import UUID
from django.shortcuts import get_object_or_404
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
from apps.patients.access import active_consultation_grants_for
from apps.patients.permissions import IsClinician

from .models import (
    Examination,
    ExaminationCatalog,
    ExaminationObservation,
)
from .serializers import (
    DiagnosticReportFinalizeSerializer,
    ExaminationCreateSerializer,
    ExaminationSerializer,
)
from .services import (
    create_examination_result,
    finalize_examination_result,
    release_examination_result,
)


def clinician_examinations(
    request,
    *,
    include_consultation=False,
):
    clinician = request.user.clinician
    access_filter = (
        Q(hospital=clinician.hospital)
        & (
            Q(ordered_by=clinician)
            | Q(encounter__attending_clinician=clinician)
        )
    )
    if include_consultation:
        shared_encounters = active_consultation_grants_for(
            clinician
        ).values("encounter_id")
        access_filter |= Q(encounter_id__in=shared_encounters)

    return (
        Examination.objects
        .filter(access_filter)
        .select_related(
            "patient",
            "encounter",
            "hospital",
            "ordered_by",
        )
        .prefetch_related(
            "observations",
            "reports",
            "reports__author",
            "reports__assets",
        )
        .distinct()
    )


def serialize_examination(request, examination):
    examination = clinician_examinations(
        request
    ).get(id=examination.id)
    return ExaminationSerializer(examination).data


class ExaminationListCreateView(APIView):
    permission_classes = [
        IsClinician,
        IsApprovedClinicianOrAdmin,
    ]

    def get(self, request):
        examinations = clinician_examinations(
            request,
            include_consultation=True,
        )
        patient_id = (
            request.query_params
            .get("patient_id", "")
            .strip()
        )
        if patient_id:
            try:
                parsed_patient_id = UUID(patient_id)
            except ValueError as exc:
                raise ValidationError({
                    "patient_id": "올바른 환자 ID를 입력해 주세요.",
                }) from exc
            examinations = examinations.filter(
                patient_id=parsed_patient_id,
            )
        requested_status = (
            request.query_params
            .get("status", "")
            .strip()
            .upper()
        )
        requested_category = (
            request.query_params
            .get("category", "")
            .strip()
            .upper()
        )
        requested_interpretation = (
            request.query_params
            .get("interpretation", "")
            .strip()
            .upper()
        )
        released = (
            request.query_params
            .get("released", "")
            .strip()
            .lower()
        )
        search = (
            request.query_params
            .get("search", "")
            .strip()
        )

        valid_statuses = {
            value
            for value, _label
            in Examination.Status.choices
        }
        if (
            requested_status
            and requested_status not in valid_statuses
        ):
            raise ValidationError({
                "status": "올바른 검사 상태가 아닙니다.",
            })
        if requested_status:
            examinations = examinations.filter(
                status=requested_status,
            )

        valid_categories = {
            value
            for value, _label
            in ExaminationCatalog.Category.choices
        }
        if (
            requested_category
            and requested_category not in valid_categories
        ):
            raise ValidationError({
                "category": "올바른 검사 분류가 아닙니다.",
            })
        if requested_category:
            examinations = examinations.filter(
                category=requested_category,
            )

        valid_interpretations = {
            value
            for value, _label
            in ExaminationObservation.Interpretation.choices
        }
        if (
            requested_interpretation
            and requested_interpretation
            not in valid_interpretations
        ):
            raise ValidationError({
                "interpretation": (
                    "올바른 결과 판정이 아닙니다."
                ),
            })
        if requested_interpretation:
            examinations = examinations.filter(
                observations__interpretation=(
                    requested_interpretation
                )
            )

        if released in {"true", "1"}:
            examinations = examinations.filter(
                reports__is_released_to_patient=True,
            )
        elif released in {"false", "0"}:
            examinations = examinations.filter(
                reports__is_released_to_patient=False,
            )
        elif released:
            raise ValidationError({
                "released": "공개 여부를 확인해주세요.",
            })

        if search:
            examinations = examinations.filter(
                Q(test_name__icontains=search)
                | Q(test_code__icontains=search)
                | Q(patient__name__icontains=search)
                | Q(
                    patient__medical_record_number__icontains=(
                        search
                    )
                )
            )

        paginator = CommonPageNumberPagination()
        page = paginator.paginate_queryset(
            examinations.distinct(),
            request,
            view=self,
        )
        return paginator.get_paginated_response(
            ExaminationSerializer(
                page,
                many=True,
            ).data
        )

    def post(self, request):
        serializer = ExaminationCreateSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        examination = create_examination_result(
            clinician=request.user.clinician,
            encounter=serializer.context["encounter"],
            validated_data={
                **serializer.validated_data,
            },
        )
        return Response(
            {
                "data": serialize_examination(
                    request,
                    examination,
                ),
            },
            status=status.HTTP_201_CREATED,
        )


class ExaminationContextListView(APIView):
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
                hospital__isnull=False,
            )
            .select_related("patient", "department")
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
                    "patient_name": encounter.patient.name,
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


class ExaminationDetailView(APIView):
    permission_classes = [
        IsClinician,
        IsApprovedClinicianOrAdmin,
    ]

    def get(self, request, examination_id):
        examination = get_object_or_404(
            clinician_examinations(
                request,
                include_consultation=True,
            ),
            id=examination_id,
        )
        AuditEvent.objects.create(
            actor=request.user,
            patient=examination.patient,
            encounter=examination.encounter,
            action=AuditEvent.Action.VIEWED,
            resource_type="examination",
            resource_id=examination.id,
        )
        return Response({
            "data": ExaminationSerializer(
                examination
            ).data,
        })


class ExaminationFinalizeView(APIView):
    permission_classes = [
        IsClinician,
        IsApprovedClinicianOrAdmin,
    ]

    def post(self, request, examination_id):
        examination = get_object_or_404(
            clinician_examinations(request),
            id=examination_id,
        )
        serializer = DiagnosticReportFinalizeSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        examination = finalize_examination_result(
            examination=examination,
            clinician=request.user.clinician,
            summary=serializer.validated_data.get(
                "summary",
                "",
            ),
            conclusion=serializer.validated_data[
                "conclusion"
            ],
        )
        return Response({
            "data": serialize_examination(
                request,
                examination,
            ),
        })


class ExaminationReleaseView(APIView):
    permission_classes = [
        IsClinician,
        IsApprovedClinicianOrAdmin,
    ]

    def post(self, request, examination_id):
        examination = get_object_or_404(
            clinician_examinations(request),
            id=examination_id,
        )
        examination = release_examination_result(
            examination=examination,
            clinician=request.user.clinician,
        )
        return Response({
            "data": serialize_examination(
                request,
                examination,
            ),
        })
