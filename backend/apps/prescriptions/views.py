from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.clinical_records.models import ClinicalRecord
from apps.clinicians.permissions import (
    IsApprovedClinicianOrAdmin,
)
from apps.core.pagination import CommonPageNumberPagination
from apps.patients.permissions import IsClinician

from .models import Prescription
from .serializers import (
    ClinicianPrescriptionCreateSerializer,
    ClinicianPrescriptionSerializer,
    PrescriptionStatusUpdateSerializer,
)


def _clinician_prescriptions(request):
    return (
        Prescription.objects
        .filter(
            clinician=request.user.clinician,
            encounter__patient__isnull=False,
        )
        .select_related(
            "encounter",
            "encounter__patient",
            "clinical_record",
            "clinician",
        )
        .prefetch_related("items")
    )


class ClinicianPrescriptionListCreateView(APIView):
    permission_classes = [
        IsClinician,
        IsApprovedClinicianOrAdmin,
    ]

    def get(self, request):
        prescriptions = _clinician_prescriptions(request)
        requested_status = (
            request.query_params
            .get("status", "")
            .strip()
            .upper()
        )
        search = (
            request.query_params
            .get("search", "")
            .strip()
        )

        valid_statuses = {
            value
            for value, _label
            in Prescription.Status.choices
        }

        if (
            requested_status
            and requested_status not in valid_statuses
        ):
            raise ValidationError({
                "status": "올바른 처방 상태가 아닙니다.",
            })

        if requested_status:
            prescriptions = prescriptions.filter(
                status=requested_status,
            )

        if search:
            prescriptions = prescriptions.filter(
                Q(
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
                    items__medicine_name__icontains=search
                )
            ).distinct()

        paginator = CommonPageNumberPagination()
        page = paginator.paginate_queryset(
            prescriptions,
            request,
            view=self,
        )
        serializer = ClinicianPrescriptionSerializer(
            page,
            many=True,
        )

        return paginator.get_paginated_response(
            serializer.data,
        )

    def post(self, request):
        input_serializer = (
            ClinicianPrescriptionCreateSerializer(
                data=request.data,
                context={"request": request},
            )
        )
        input_serializer.is_valid(raise_exception=True)
        prescription = input_serializer.save()
        prescription = _clinician_prescriptions(
            request,
        ).get(id=prescription.id)

        return Response(
            {
                "data": ClinicianPrescriptionSerializer(
                    prescription,
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )


class ClinicianPrescriptionContextListView(APIView):
    permission_classes = [
        IsClinician,
        IsApprovedClinicianOrAdmin,
    ]

    def get(self, request):
        clinician = request.user.clinician
        search = (
            request.query_params
            .get("search", "")
            .strip()
        )
        records = (
            ClinicalRecord.objects
            .filter(
                clinician=clinician,
                encounter__patient__isnull=False,
            )
            .select_related(
                "encounter",
                "encounter__patient",
            )
        )

        if search:
            records = records.filter(
                Q(
                    encounter__patient__name__icontains=(
                        search
                    )
                )
                | Q(
                    encounter__patient__medical_record_number__icontains=(
                        search
                    )
                )
            )

        data = [
            {
                "clinical_record_id": str(record.id),
                "encounter_id": str(record.encounter_id),
                "encounter_number": (
                    record.encounter.encounter_number
                ),
                "patient_id": str(
                    record.encounter.patient_id
                ),
                "patient_number": (
                    record.encounter.patient
                    .medical_record_number
                ),
                "patient_name": (
                    record.encounter.patient.name
                ),
                "recorded_at": (
                    record.recorded_at.isoformat()
                ),
            }
            for record in records[:100]
        ]

        return Response({"data": data})


class ClinicianPrescriptionDetailView(APIView):
    permission_classes = [
        IsClinician,
        IsApprovedClinicianOrAdmin,
    ]

    def get(self, request, prescription_id):
        prescription = get_object_or_404(
            _clinician_prescriptions(request),
            id=prescription_id,
        )

        return Response({
            "data": ClinicianPrescriptionSerializer(
                prescription,
            ).data,
        })


class ClinicianPrescriptionStatusView(APIView):
    permission_classes = [
        IsClinician,
        IsApprovedClinicianOrAdmin,
    ]

    transitions = {
        Prescription.Status.DRAFT: {
            Prescription.Status.ACTIVE,
            Prescription.Status.CANCELLED,
        },
        Prescription.Status.ACTIVE: {
            Prescription.Status.COMPLETED,
            Prescription.Status.DISCONTINUED,
            Prescription.Status.CANCELLED,
        },
        Prescription.Status.COMPLETED: set(),
        Prescription.Status.DISCONTINUED: set(),
        Prescription.Status.CANCELLED: set(),
    }

    @transaction.atomic
    def patch(self, request, prescription_id):
        input_serializer = (
            PrescriptionStatusUpdateSerializer(
                data=request.data,
            )
        )
        input_serializer.is_valid(raise_exception=True)

        prescription = get_object_or_404(
            _clinician_prescriptions(request)
            .select_for_update(),
            id=prescription_id,
        )
        next_status = (
            input_serializer.validated_data["status"]
        )

        if next_status not in self.transitions[
            prescription.status
        ]:
            raise ValidationError({
                "status": (
                    f"{prescription.status} 상태에서 "
                    f"{next_status} 상태로 변경할 수 없습니다."
                ),
            })

        prescription.status = next_status
        prescription.discontinued_at = (
            timezone.now()
            if next_status
            == Prescription.Status.DISCONTINUED
            else None
        )
        prescription.save(
            update_fields=[
                "status",
                "discontinued_at",
                "updated_at",
            ],
        )

        prescription = _clinician_prescriptions(
            request,
        ).get(id=prescription.id)

        return Response({
            "data": ClinicianPrescriptionSerializer(
                prescription,
            ).data,
        })
