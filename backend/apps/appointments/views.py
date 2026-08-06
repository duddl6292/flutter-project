from datetime import (
    datetime,
    time,
    timedelta,
)
from uuid import UUID

from django.db import transaction
from django.db.models import Q
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.clinical_records.models import ClinicalRecord
from apps.clinical_records.serializers import (
    ClinicalRecordSerializer,
    ClinicalRecordUpsertSerializer,
)
from apps.clinicians.permissions import (
    IsApprovedClinicianOrAdmin,
)
from apps.core.pagination import CommonPageNumberPagination
from apps.patients.permissions import (
    IsClinician,
    IsClinicianOrAdmin,
)

from .models import Appointment, Encounter
from .serializers import (
    AppointmentCreateSerializer,
    AppointmentStatusUpdateSerializer,
    AppointmentSummarySerializer,
    AppointmentUpdateSerializer,
    EncounterDetailSerializer,
    EncounterListQuerySerializer,
    EncounterStatusSerializer,
    EncounterSummarySerializer,
)
from .services import (
    AppointmentStatusTransitionError,
    EncounterWorkflowError,
    change_appointment_status,
    change_encounter_status,
    register_appointment_encounter,
)


class AppointmentListCreateView(APIView):
    permission_classes = [
        IsClinicianOrAdmin,
    ]

    def get(self, request):
        appointments = (
            Appointment.objects
            .select_related(
                "patient",
                "clinician",
                "department",
                "hospital",
                "encounter",
            )
        )

        if request.user.role == "CLINICIAN":
            appointments = appointments.filter(
                clinician__user=request.user,
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
            appointments = appointments.filter(
                patient_id=parsed_patient_id,
            )

        requested_status = (
            request.query_params
            .get("status", "")
            .strip()
            .upper()
        )

        valid_statuses = {
            value
            for value, _label
            in Appointment.Status.choices
        }

        if requested_status in valid_statuses:
            appointments = appointments.filter(
                status=requested_status,
            )

        date_from = (
            request.query_params
            .get("date_from")
        )

        date_to = (
            request.query_params
            .get("date_to")
        )

        current_timezone = (
            timezone.get_current_timezone()
        )

        if date_from:
            start_date = datetime.strptime(
                date_from,
                "%Y-%m-%d",
            ).date()

            start_at = timezone.make_aware(
                datetime.combine(
                    start_date,
                    time.min,
                ),
                current_timezone,
            )

            appointments = appointments.filter(
                scheduled_at__gte=start_at,
            )

        if date_to:
            end_date = datetime.strptime(
                date_to,
                "%Y-%m-%d",
            ).date()

            end_at = timezone.make_aware(
                datetime.combine(
                    end_date
                    + timedelta(days=1),
                    time.min,
                ),
                current_timezone,
            )

            appointments = appointments.filter(
                scheduled_at__lt=end_at,
            )

        appointments = appointments.order_by(
            "scheduled_at",
        )

        serializer = AppointmentSummarySerializer(
            appointments,
            many=True,
        )

        return Response({
            "data": serializer.data,
            "meta": {
                "total_count":
                    appointments.count(),
            },
        })

    @transaction.atomic
    def post(self, request):
        serializer = AppointmentCreateSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True,
        )

        appointment = serializer.save()

        response_serializer = (
            AppointmentSummarySerializer(
                appointment,
            )
        )

        return Response(
            {
                "data":
                    response_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class AppointmentDetailView(APIView):
    permission_classes = [
        IsClinicianOrAdmin,
    ]

    def get_object(self, request, appointment_id):
        appointments = Appointment.objects.select_related(
            "patient",
            "clinician__user",
            "department",
            "hospital",
            "encounter",
        )
        if request.user.role == "CLINICIAN":
            appointments = appointments.filter(
                clinician__user=request.user,
            )
        return get_object_or_404(
            appointments,
            id=appointment_id,
        )

    @transaction.atomic
    def patch(self, request, appointment_id):
        appointment = self.get_object(
            request,
            appointment_id,
        )

        if "status" in request.data:
            serializer = AppointmentStatusUpdateSerializer(
                data=request.data,
            )
            serializer.is_valid(raise_exception=True)
            reason = serializer.validated_data.get(
                "reason",
                "",
            )
            try:
                appointment = change_appointment_status(
                    appointment_id=appointment.id,
                    new_status=serializer.validated_data["status"],
                    changed_by=request.user,
                    reason=reason,
                    cancellation_reason=reason,
                )
            except AppointmentStatusTransitionError as exc:
                raise ValidationError({
                    "status": str(exc),
                }) from exc
        else:
            serializer = AppointmentUpdateSerializer(
                appointment,
                data=request.data,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            appointment = serializer.save()

        return Response({
            "data": AppointmentSummarySerializer(
                appointment,
            ).data,
        })


class AppointmentEncounterRegistrationView(APIView):
    permission_classes = [
        IsClinician,
        IsApprovedClinicianOrAdmin,
    ]

    @transaction.atomic
    def post(self, request, appointment_id):
        get_object_or_404(
            Appointment.objects.filter(
                clinician__user=request.user,
            ),
            id=appointment_id,
        )
        try:
            encounter, created = register_appointment_encounter(
                appointment_id=appointment_id,
                registered_by=request.user,
            )
        except EncounterWorkflowError as exc:
            raise ValidationError({
                "appointment": str(exc),
            }) from exc

        appointment = (
            Appointment.objects
            .select_related(
                "patient",
                "clinician",
                "department",
                "hospital",
                "encounter",
            )
            .get(id=appointment_id)
        )
        return Response(
            {
                "data": {
                    "appointment": AppointmentSummarySerializer(
                        appointment,
                    ).data,
                    "encounter_id": str(encounter.id),
                    "created": created,
                }
            },
            status=(
                status.HTTP_201_CREATED
                if created
                else status.HTTP_200_OK
            ),
        )


def _clinician_encounters(request):
    return (
        Encounter.objects
        .filter(
            attending_clinician=request.user.clinician,
        )
        .select_related(
            "patient",
            "provisional_identity",
            "appointment",
            "department",
            "hospital",
            "attending_clinician",
        )
    )


def _clinician_encounter_details(request):
    return (
        _clinician_encounters(request)
        .prefetch_related(
            "clinical_records",
            "prescriptions__items",
            "ct_cases",
        )
    )


class ClinicianEncounterListView(APIView):
    permission_classes = [
        IsClinician,
        IsApprovedClinicianOrAdmin,
    ]

    def get(self, request):
        query_serializer = EncounterListQuerySerializer(
            data=request.query_params,
        )
        query_serializer.is_valid(raise_exception=True)
        query = query_serializer.validated_data
        encounters = _clinician_encounters(request)
        requested_status = query.get("status")
        search = query.get("search", "").strip()
        current_timezone = timezone.get_current_timezone()

        encounters = encounters.annotate(
            activity_at=Coalesce(
                "arrived_at",
                "created_at",
            )
        )

        if requested_status:
            encounters = encounters.filter(
                status=requested_status,
            )

        if search:
            encounters = encounters.filter(
                Q(patient__name__icontains=search)
                | Q(
                    patient__medical_record_number__icontains=(
                        search
                    )
                )
                | Q(
                    provisional_identity__temporary_name__icontains=(
                        search
                    )
                )
                | Q(encounter_number__icontains=search)
            )

        if query.get("date_from"):
            start_at = timezone.make_aware(
                datetime.combine(
                    query["date_from"],
                    time.min,
                ),
                current_timezone,
            )
            encounters = encounters.filter(
                activity_at__gte=start_at,
            )

        if query.get("date_to"):
            end_at = timezone.make_aware(
                datetime.combine(
                    query["date_to"] + timedelta(days=1),
                    time.min,
                ),
                current_timezone,
            )
            encounters = encounters.filter(
                activity_at__lt=end_at,
            )

        encounters = encounters.order_by("-activity_at")
        paginator = CommonPageNumberPagination()
        page = paginator.paginate_queryset(
            encounters,
            request,
            view=self,
        )

        return paginator.get_paginated_response(
            EncounterSummarySerializer(
                page,
                many=True,
            ).data
        )

class ClinicianEncounterDetailView(APIView):
    permission_classes = [
        IsClinician,
        IsApprovedClinicianOrAdmin,
    ]

    def get(self, request, encounter_id):
        encounter = get_object_or_404(
            _clinician_encounter_details(request),
            id=encounter_id,
        )

        return Response({
            "data": EncounterDetailSerializer(
                encounter,
            ).data,
        })


class ClinicianEncounterStatusView(APIView):
    permission_classes = [
        IsClinician,
        IsApprovedClinicianOrAdmin,
    ]

    @transaction.atomic
    def patch(self, request, encounter_id):
        get_object_or_404(
            _clinician_encounters(request),
            id=encounter_id,
        )
        input_serializer = EncounterStatusSerializer(
            data=request.data,
        )
        input_serializer.is_valid(raise_exception=True)

        try:
            change_encounter_status(
                encounter_id=encounter_id,
                new_status=(
                    input_serializer.validated_data[
                        "status"
                    ]
                ),
                changed_by=request.user,
            )
        except EncounterWorkflowError as exc:
            raise ValidationError({
                "status": str(exc),
            }) from exc

        encounter = _clinician_encounter_details(
            request,
        ).get(id=encounter_id)

        return Response({
            "data": EncounterDetailSerializer(
                encounter,
            ).data,
        })


class ClinicianEncounterClinicalRecordView(APIView):
    permission_classes = [
        IsClinician,
        IsApprovedClinicianOrAdmin,
    ]

    def get(self, request, encounter_id):
        encounter = get_object_or_404(
            _clinician_encounters(request),
            id=encounter_id,
        )
        record = encounter.clinical_records.first()

        return Response({
            "data": (
                ClinicalRecordSerializer(record).data
                if record
                else None
            ),
        })

    @transaction.atomic
    def put(self, request, encounter_id):
        encounter = get_object_or_404(
            _clinician_encounters(request)
            .select_for_update(of=("self",)),
            id=encounter_id,
        )
        input_serializer = (
            ClinicalRecordUpsertSerializer(
                data=request.data,
            )
        )
        input_serializer.is_valid(raise_exception=True)
        record = encounter.clinical_records.first()
        created = record is None

        if record is None:
            record = ClinicalRecord(
                encounter=encounter,
                clinician=request.user.clinician,
            )

        for field, value in (
            input_serializer.validated_data.items()
        ):
            setattr(record, field, value)

        record.recorded_at = timezone.now()
        record.save()

        return Response(
            {
                "data": ClinicalRecordSerializer(
                    record,
                ).data,
            },
            status=(
                status.HTTP_201_CREATED
                if created
                else status.HTTP_200_OK
            ),
        )
