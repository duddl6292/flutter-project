from django.db.models import Q
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Clinician, Department
from .permissions import IsClinicianOrAdmin
from .serializers import (
    ClinicianSerializer,
    DepartmentSerializer,
)


class DepartmentListView(ListAPIView):
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

        return Response({
            "data": {
                "clinician": ClinicianSerializer(
                    clinician
                ).data,
            }
        })