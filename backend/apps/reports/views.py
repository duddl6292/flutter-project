from datetime import datetime, time, timedelta

from django.db.models import Count, OuterRef, Subquery
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.appointments.models import Appointment, Encounter
from apps.clinicians.permissions import (
    IsApprovedClinicianOrAdmin,
)
from apps.core.pagination import CommonPageNumberPagination
from apps.ct_analysis.models import CTCase, InferenceJob
from apps.patients.permissions import IsClinician
from apps.prescriptions.models import (
    Prescription,
    PrescriptionItem,
)

from .serializers import (
    ClinicianReportDetailQuerySerializer,
    ClinicianReportQuerySerializer,
)


def _period_bounds(start_date, end_date):
    current_timezone = timezone.get_current_timezone()
    start_at = timezone.make_aware(
        datetime.combine(start_date, time.min),
        current_timezone,
    )
    end_at = timezone.make_aware(
        datetime.combine(
            end_date + timedelta(days=1),
            time.min,
        ),
        current_timezone,
    )

    return start_at, end_at


def _status_counts(queryset, choices):
    grouped = {
        row["status"]: row["count"]
        for row in (
            queryset
            .values("status")
            .annotate(count=Count("id"))
        )
    }

    return [
        {
            "status": value,
            "label": label,
            "count": grouped.get(value, 0),
        }
        for value, label in choices
    ]


class ClinicianSummaryReportView(APIView):
    permission_classes = [
        IsClinician,
        IsApprovedClinicianOrAdmin,
    ]

    def get(self, request):
        query_serializer = (
            ClinicianReportQuerySerializer(
                data=request.query_params,
            )
        )
        query_serializer.is_valid(raise_exception=True)
        start_date = (
            query_serializer.validated_data[
                "start_date"
            ]
        )
        end_date = (
            query_serializer.validated_data[
                "end_date"
            ]
        )
        start_at, end_at = _period_bounds(
            start_date,
            end_date,
        )
        clinician = request.user.clinician

        appointments = Appointment.objects.filter(
            clinician=clinician,
            scheduled_at__gte=start_at,
            scheduled_at__lt=end_at,
        )
        appointment_total = appointments.count()
        appointment_completed = appointments.filter(
            status=Appointment.Status.COMPLETED,
        ).count()
        appointment_completion_rate = (
            round(
                appointment_completed
                / appointment_total
                * 100,
                1,
            )
            if appointment_total
            else 0.0
        )

        completed_encounters = Encounter.objects.filter(
            attending_clinician=clinician,
            patient__isnull=False,
            status=Encounter.Status.COMPLETED,
            completed_at__gte=start_at,
            completed_at__lt=end_at,
        )
        patient_count = (
            completed_encounters
            .values("patient_id")
            .distinct()
            .count()
        )

        daily_grouped = {
            row["day"]: row["count"]
            for row in (
                completed_encounters
                .annotate(day=TruncDate("completed_at"))
                .values("day")
                .annotate(
                    count=Count(
                        "patient_id",
                        distinct=True,
                    )
                )
                .order_by("day")
            )
        }
        daily_encounters = []
        current_date = start_date

        while current_date <= end_date:
            daily_encounters.append({
                "date": current_date.isoformat(),
                "count": daily_grouped.get(
                    current_date,
                    0,
                ),
            })
            current_date += timedelta(days=1)

        prescriptions = Prescription.objects.filter(
            clinician=clinician,
            prescribed_at__gte=start_at,
            prescribed_at__lt=end_at,
        )
        prescription_count = prescriptions.count()

        top_medicines = list(
            PrescriptionItem.objects
            .filter(
                prescription__clinician=clinician,
                prescription__prescribed_at__gte=(
                    start_at
                ),
                prescription__prescribed_at__lt=end_at,
            )
            .values("medicine_name")
            .annotate(count=Count("id"))
            .order_by("-count", "medicine_name")[:5]
        )

        ct_analysis_count = (
            InferenceJob.objects
            .filter(
                requested_by=request.user,
                created_at__gte=start_at,
                created_at__lt=end_at,
            )
            .values("case_id")
            .distinct()
            .count()
        )

        return Response({
            "data": {
                "clinician": {
                    "clinician_id": str(clinician.id),
                    "name": clinician.name,
                },
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
                "summary": {
                    "patient_count": patient_count,
                    "appointment_completion_rate": (
                        appointment_completion_rate
                    ),
                    "prescription_count": (
                        prescription_count
                    ),
                    "ct_analysis_count": ct_analysis_count,
                },
                "daily_encounters": daily_encounters,
                "appointment_statuses": _status_counts(
                    appointments,
                    Appointment.Status.choices,
                ),
                "prescription_statuses": _status_counts(
                    prescriptions,
                    Prescription.Status.choices,
                ),
                "top_medicines": top_medicines,
            },
        })


def _patient_payload(patient):
    if patient is None:
        return {
            "patient_id": None,
            "patient_number": None,
            "patient_name": "신원 미상",
        }

    return {
        "patient_id": str(patient.id),
        "patient_number": (
            patient.medical_record_number
        ),
        "patient_name": patient.name,
    }


class ClinicianDetailReportView(APIView):
    permission_classes = [
        IsClinician,
        IsApprovedClinicianOrAdmin,
    ]

    def get(self, request):
        query_serializer = (
            ClinicianReportDetailQuerySerializer(
                data=request.query_params,
            )
        )
        query_serializer.is_valid(raise_exception=True)
        query = query_serializer.validated_data
        start_at, end_at = _period_bounds(
            query["start_date"],
            query["end_date"],
        )
        detail_type = query["type"]
        requested_status = query.get(
            "status",
            "",
        ).strip().upper()
        medicine = query.get(
            "medicine",
            "",
        ).strip()
        clinician = request.user.clinician

        if (
            detail_type
            == ClinicianReportDetailQuerySerializer
            .DetailType.ENCOUNTERS
        ):
            completed_encounters = (
                Encounter.objects
                .filter(
                    attending_clinician=clinician,
                    patient__isnull=False,
                    status=Encounter.Status.COMPLETED,
                    completed_at__gte=start_at,
                    completed_at__lt=end_at,
                )
            )
            latest_encounter = (
                completed_encounters
                .filter(patient_id=OuterRef("patient_id"))
                .order_by("-completed_at", "-created_at")
            )
            queryset = (
                completed_encounters
                .filter(
                    id=Subquery(
                        latest_encounter.values("id")[:1]
                    )
                )
                .select_related("patient")
                .order_by("-completed_at")
            )
            if requested_status:
                queryset = queryset.filter(
                    status=requested_status,
                )
            serializer = self._encounter_data

        elif (
            detail_type
            == ClinicianReportDetailQuerySerializer
            .DetailType.APPOINTMENTS
        ):
            queryset = (
                Appointment.objects
                .filter(
                    clinician=clinician,
                    scheduled_at__gte=start_at,
                    scheduled_at__lt=end_at,
                )
                .select_related("patient")
                .order_by("-scheduled_at")
            )
            if requested_status:
                queryset = queryset.filter(
                    status=requested_status,
                )
            serializer = self._appointment_data

        elif (
            detail_type
            == ClinicianReportDetailQuerySerializer
            .DetailType.PRESCRIPTIONS
        ):
            queryset = (
                Prescription.objects
                .filter(
                    clinician=clinician,
                    encounter__patient__isnull=False,
                    prescribed_at__gte=start_at,
                    prescribed_at__lt=end_at,
                )
                .select_related("encounter__patient")
                .prefetch_related("items")
                .order_by("-prescribed_at")
            )
            if requested_status:
                queryset = queryset.filter(
                    status=requested_status,
                )
            if medicine:
                queryset = queryset.filter(
                    items__medicine_name=medicine,
                ).distinct()
            serializer = self._prescription_data

        else:
            matching_jobs = InferenceJob.objects.filter(
                case_id=OuterRef("pk"),
                requested_by=request.user,
                created_at__gte=start_at,
                created_at__lt=end_at,
            ).order_by("-created_at")
            queryset = (
                CTCase.objects
                .filter(
                    inference_jobs__requested_by=(
                        request.user
                    ),
                    inference_jobs__created_at__gte=(
                        start_at
                    ),
                    inference_jobs__created_at__lt=end_at,
                )
                .select_related(
                    "encounter__patient",
                )
                .annotate(
                    requested_at=Subquery(
                        matching_jobs.values(
                            "created_at"
                        )[:1],
                    ),
                    latest_job_status=Subquery(
                        matching_jobs.values(
                            "status"
                        )[:1],
                    ),
                )
            )
            if requested_status:
                queryset = queryset.filter(
                    inference_jobs__requested_by=(
                        request.user
                    ),
                    inference_jobs__created_at__gte=(
                        start_at
                    ),
                    inference_jobs__created_at__lt=end_at,
                    inference_jobs__status=(
                        requested_status
                    ),
                )
            queryset = queryset.distinct().order_by(
                "-requested_at"
            )
            serializer = self._ct_analysis_data

        paginator = CommonPageNumberPagination()
        page = paginator.paginate_queryset(
            queryset,
            request,
            view=self,
        )

        return paginator.get_paginated_response([
            serializer(item)
            for item in page
        ])

    @staticmethod
    def _encounter_data(encounter):
        return {
            "record_id": str(encounter.id),
            "type": "encounters",
            **_patient_payload(encounter.patient),
            "occurred_at": (
                encounter.completed_at.isoformat()
            ),
            "reference": encounter.encounter_number,
            "status": encounter.status,
            "status_label": (
                encounter.get_status_display()
            ),
            "details": {
                "encounter_type": (
                    encounter.get_encounter_type_display()
                ),
                "started_at": (
                    encounter.started_at.isoformat()
                    if encounter.started_at
                    else None
                ),
                "completed_at": (
                    encounter.completed_at.isoformat()
                ),
            },
        }

    @staticmethod
    def _appointment_data(appointment):
        return {
            "record_id": str(appointment.id),
            "type": "appointments",
            **_patient_payload(appointment.patient),
            "occurred_at": (
                appointment.scheduled_at.isoformat()
            ),
            "reference": f"예약 {appointment.id}",
            "status": appointment.status,
            "status_label": (
                appointment.get_status_display()
            ),
            "details": {
                "duration_minutes": (
                    appointment.duration_minutes
                ),
                "location": appointment.location,
                "reason": appointment.reason,
                "cancellation_reason": (
                    appointment.cancellation_reason
                ),
            },
        }

    @staticmethod
    def _prescription_data(prescription):
        items = [
            {
                "medicine_name": item.medicine_name,
                "dosage": str(item.dosage),
                "dose_unit": item.dose_unit,
                "frequency": item.frequency,
                "route": item.route,
            }
            for item in prescription.items.all()
        ]

        return {
            "record_id": str(prescription.id),
            "type": "prescriptions",
            **_patient_payload(
                prescription.encounter.patient
            ),
            "occurred_at": (
                prescription.prescribed_at.isoformat()
            ),
            "reference": (
                prescription.encounter.encounter_number
            ),
            "status": prescription.status,
            "status_label": (
                prescription.get_status_display()
            ),
            "details": {
                "notes": prescription.notes,
                "items": items,
            },
        }

    @staticmethod
    def _ct_analysis_data(case):
        job_status_labels = dict(
            InferenceJob.Status.choices
        )
        patient = case.encounter.patient

        return {
            "record_id": str(case.id),
            "type": "ct_analyses",
            **_patient_payload(patient),
            "occurred_at": case.requested_at.isoformat(),
            "reference": f"CT {case.id}",
            "status": case.latest_job_status,
            "status_label": job_status_labels.get(
                case.latest_job_status,
                case.latest_job_status,
            ),
            "details": {
                "study_type": (
                    case.get_study_type_display()
                ),
                "case_status": case.status,
                "case_status_label": (
                    case.get_status_display()
                ),
                "description": case.description,
                "performed_at": (
                    case.performed_at.isoformat()
                    if case.performed_at
                    else None
                ),
            },
        }
