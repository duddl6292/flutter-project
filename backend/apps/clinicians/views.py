from datetime import datetime, time, timedelta

from django.db.models import Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.appointments.models import Appointment, Encounter
from apps.consultations.models import Consultation
from apps.ct_analysis.models import CTCase
from apps.diagnostics.models import Examination

from .models import Clinician, Department
from .permissions import IsClinicianOrAdmin
from .serializers import (
    ClinicianSerializer,
    DepartmentSerializer,
)

from rest_framework.permissions import AllowAny


APPOINTMENT_STATUS_MAPPING = {
    Appointment.Status.SCHEDULED: "scheduled",
    Appointment.Status.CONFIRMED: "confirmed",
    Appointment.Status.CHECKED_IN: "waiting",
    Appointment.Status.COMPLETED: "completed",
    Appointment.Status.CANCELLED: "cancelled",
    Appointment.Status.NO_SHOW: "no_show",
}

ENCOUNTER_STATUS_MAPPING = {
    Encounter.Status.REGISTERED: "scheduled",
    Encounter.Status.ARRIVED: "waiting",
    Encounter.Status.IN_PROGRESS: "in_progress",
    Encounter.Status.COMPLETED: "completed",
    Encounter.Status.CANCELLED: "cancelled",
}


def _dashboard_date_range(request):
    requested_date = request.query_params.get("date", "").strip()
    selected_date = (
        parse_date(requested_date)
        if requested_date
        else timezone.localdate()
    )
    if selected_date is None:
        raise ValidationError({
            "date": "날짜는 YYYY-MM-DD 형식으로 입력해주세요.",
        })

    current_timezone = timezone.get_current_timezone()
    start_at = timezone.make_aware(
        datetime.combine(selected_date, time.min),
        current_timezone,
    )
    end_at = start_at + timedelta(days=1)
    return selected_date, start_at, end_at


def _age_on_date(birth_date, selected_date):
    if birth_date is None:
        return None
    return (
        selected_date.year
        - birth_date.year
        - (
            (selected_date.month, selected_date.day)
            < (birth_date.month, birth_date.day)
        )
    )

class DepartmentListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        return Department.objects.filter(
            is_active=True
        ).order_by("name")


class ClinicianListView(ListAPIView):
    serializer_class = ClinicianSerializer

    def get_queryset(self):
        queryset = Clinician.objects.select_related(
            "user",
            "hospital",
            "department",
        ).filter(
            approval_status=Clinician.ApprovalStatus.APPROVED,
        )

        keyword = self.request.query_params.get(
            "keyword",
            "",
        ).strip()

        department = self.request.query_params.get(
            "department",
            "",
        ).strip()

        hospital = self.request.query_params.get(
            "hospital",
            "",
        ).strip()

        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword)
                | Q(hospital__name__icontains=keyword)
                | Q(department__name__icontains=keyword)
            )

        if department:
            queryset = queryset.filter(
                department__code=department,
            )

        if hospital:
            queryset = queryset.filter(
                hospital_id=hospital,
            )

        return queryset.order_by("name")


class ClinicianDetailView(RetrieveAPIView):
    serializer_class = ClinicianSerializer
    lookup_url_kwarg = "clinician_id"

    def get_queryset(self):
        return Clinician.objects.select_related(
            "user",
            "hospital",
            "department",
        ).filter(
            approval_status=Clinician.ApprovalStatus.APPROVED,
        )


class ClinicianDashboardView(APIView):
    permission_classes = [IsClinicianOrAdmin]

    def get(self, request):
        clinician = request.user.clinician
        selected_date, start_at, end_at = (
            _dashboard_date_range(request)
        )

        appointment_queryset = (
            Appointment.objects
            .filter(
                clinician=clinician,
                scheduled_at__gte=start_at,
                scheduled_at__lt=end_at,
            )
            .select_related(
                "patient",
                "department",
                "encounter",
            )
        )
        active_appointments = appointment_queryset.exclude(
            status=Appointment.Status.CANCELLED,
        )
        appointments = list(
            active_appointments.order_by("scheduled_at")
        )

        encounter_queryset = (
            Encounter.objects
            .filter(
                attending_clinician=clinician,
                patient__isnull=False,
            )
            .annotate(
                dashboard_at=Coalesce(
                    "arrived_at",
                    "created_at",
                )
            )
            .filter(
                dashboard_at__gte=start_at,
                dashboard_at__lt=end_at,
            )
            .select_related(
                "patient",
                "department",
                "appointment",
            )
            .order_by("dashboard_at")
        )
        encounters = list(encounter_queryset)

        patient_rows_by_id = {}
        schedule_rows = []

        for appointment in appointments:
            encounter = getattr(
                appointment,
                "encounter",
                None,
            )
            display_status = (
                ENCOUNTER_STATUS_MAPPING.get(encounter.status)
                if encounter is not None
                else APPOINTMENT_STATUS_MAPPING.get(
                    appointment.status,
                    appointment.status.lower(),
                )
            )
            patient = appointment.patient
            patient_id = str(patient.id)
            patient_rows_by_id.setdefault(
                patient_id,
                {
                    "patient_id": patient_id,
                    "patient_number": patient.medical_record_number,
                    "name": patient.name,
                    "age": _age_on_date(
                        patient.birth_date,
                        selected_date,
                    ),
                    "gender": patient.sex,
                    "department": appointment.department.name,
                    "appointment_at": appointment.scheduled_at,
                    "status": display_status,
                    "phone": patient.phone,
                },
            )
            schedule_rows.append({
                "schedule_id": str(appointment.id),
                "start_at": appointment.scheduled_at,
                "patient_id": patient_id,
                "patient_name": patient.name,
                "room": appointment.location or "진료실 미정",
                "status": display_status,
            })

        scheduled_appointment_ids = {
            appointment.id
            for appointment in appointments
        }
        for encounter in encounters:
            patient = encounter.patient
            patient_id = str(patient.id)
            display_status = ENCOUNTER_STATUS_MAPPING.get(
                encounter.status,
                encounter.status.lower(),
            )
            encounter_at = (
                encounter.arrived_at
                or encounter.created_at
            )
            existing_patient = patient_rows_by_id.get(patient_id)
            if existing_patient is None:
                patient_rows_by_id[patient_id] = {
                    "patient_id": patient_id,
                    "patient_number": patient.medical_record_number,
                    "name": patient.name,
                    "age": _age_on_date(
                        patient.birth_date,
                        selected_date,
                    ),
                    "gender": patient.sex,
                    "department": encounter.department.name,
                    "appointment_at": encounter_at,
                    "status": display_status,
                    "phone": patient.phone,
                }
            else:
                existing_patient["status"] = display_status

            if (
                encounter.appointment_id
                not in scheduled_appointment_ids
            ):
                schedule_rows.append({
                    "schedule_id": str(encounter.id),
                    "start_at": encounter_at,
                    "patient_id": patient_id,
                    "patient_name": patient.name,
                    "room": (
                        encounter.appointment.location
                        if encounter.appointment_id
                        else "당일 진료"
                    ) or "진료실 미정",
                    "status": display_status,
                })

        patient_rows = sorted(
            patient_rows_by_id.values(),
            key=lambda row: row["appointment_at"],
        )
        schedule_rows.sort(key=lambda row: row["start_at"])

        examination_queryset = (
            Examination.objects
            .filter(hospital=clinician.hospital)
            .filter(
                Q(ordered_by=clinician)
                | Q(encounter__attending_clinician=clinician)
            )
            .annotate(
                dashboard_at=Coalesce(
                    "performed_at",
                    "created_at",
                )
            )
            .filter(
                dashboard_at__gte=start_at,
                dashboard_at__lt=end_at,
            )
            .exclude(status=Examination.Status.CANCELLED)
            .distinct()
        )

        ct_queryset = (
            CTCase.objects
            .filter(
                created_at__gte=start_at,
                created_at__lt=end_at,
            )
            .filter(
                Q(created_by=request.user)
                | Q(encounter__attending_clinician=clinician)
                | Q(
                    imaging_study__examination__ordered_by=(
                        clinician
                    )
                )
            )
            .distinct()
        )

        consultations = (
            Consultation.objects
            .filter(
                participants__clinician=clinician,
                participants__left_at__isnull=True,
                encounter__patient__isnull=False,
            )
            .select_related(
                "encounter",
                "encounter__patient",
                "requester_clinician",
                "requester_clinician__department",
                "consultant_clinician",
                "consultant_clinician__department",
            )
            .distinct()
        )
        consultation_rows = []

        status_mapping = {
            Consultation.Status.REQUESTED: "requested",
            Consultation.Status.IN_PROGRESS: "waiting",
            Consultation.Status.COMPLETED: "completed",
            Consultation.Status.CANCELLED: "cancelled",
        }

        for consultation in consultations[:10]:
            other_clinician = (
                consultation.consultant_clinician
                if (
                    consultation.requester_clinician_id
                    == clinician.id
                )
                else consultation.requester_clinician
            )
            patient = consultation.encounter.patient

            consultation_rows.append({
                "consultation_id": str(
                    consultation.id
                ),
                "status": status_mapping[
                    consultation.status
                ],
                "department": (
                    other_clinician.department.name
                ),
                "title": consultation.subject,
                "patient_id": str(patient.id),
                "patient_display": (
                    f"{patient.name} "
                    "("
                    f"{patient.medical_record_number or '-'}"
                    ")"
                ),
                "requested_at": consultation.created_at,
                "responded_at": consultation.completed_at,
            })

        return Response({
            "data": {
                "clinician": ClinicianSerializer(
                    clinician
                ).data,
                "summary": {
                    "appointments": {
                        "total": active_appointments.count(),
                        "confirmed": active_appointments.filter(
                            status=Appointment.Status.CONFIRMED,
                        ).count(),
                        "waiting": active_appointments.filter(
                            status__in=[
                                Appointment.Status.SCHEDULED,
                                Appointment.Status.CHECKED_IN,
                            ]
                        ).count(),
                    },
                    "consultations": {
                        "total": consultations.count(),
                        "waiting": consultations.filter(
                            status__in=[
                                Consultation.Status.REQUESTED,
                                Consultation.Status.IN_PROGRESS,
                            ]
                        ).count(),
                        "answered": consultations.filter(
                            status=(
                                Consultation.Status.COMPLETED
                            )
                        ).count(),
                    },
                    "tests": {
                        "total": examination_queryset.count(),
                        "processing": examination_queryset.filter(
                            status__in=[
                                Examination.Status.REGISTERED,
                                Examination.Status.IN_PROGRESS,
                            ]
                        ).count(),
                        "result_waiting": examination_queryset.filter(
                            status=Examination.Status.PRELIMINARY,
                        ).count(),
                    },
                    "ct_analyses": {
                        "total": ct_queryset.count(),
                        "processing": ct_queryset.filter(
                            status__in=[
                                CTCase.Status.UPLOADED,
                                CTCase.Status.VALIDATING,
                                CTCase.Status.READY,
                                CTCase.Status.PROCESSING,
                            ]
                        ).count(),
                        "completed": ct_queryset.filter(
                            status=CTCase.Status.COMPLETED,
                        ).count(),
                    },
                },
                "patients": patient_rows,
                "schedules": schedule_rows,
                "activities": [],
                "consultations": consultation_rows,
            }
        })
