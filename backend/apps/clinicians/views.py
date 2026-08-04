from django.db.models import Q
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.consultations.models import Consultation

from .models import Clinician, Department
from .permissions import IsClinicianOrAdmin
from .serializers import (
    ClinicianSerializer,
    DepartmentSerializer,
)

from rest_framework.permissions import AllowAny

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
                        "total": 0,
                        "confirmed": 0,
                        "waiting": 0,
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
                        "total": 0,
                        "processing": 0,
                        "result_waiting": 0,
                    },
                    "ct_analyses": {
                        "total": 0,
                        "processing": 0,
                        "completed": 0,
                    },
                },
                "consultations": consultation_rows,
            }
        })
