from django.db.models import Q
from rest_framework.views import APIView

from apps.core.permissions import ClinicianOrAdmin
from apps.core.responses import success
from apps.core.viewsets import WrappedModelViewSet

from .models import Clinician, Department
from .serializers import ClinicianSerializer, DepartmentSerializer


class DepartmentListView(WrappedModelViewSet):
    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentSerializer
    http_method_names = ("get", "head", "options")


class ClinicianListView(WrappedModelViewSet):
    serializer_class = ClinicianSerializer
    http_method_names = ("get", "head", "options")

    def get_queryset(self):
        queryset = Clinician.objects.select_related("user", "department")
        keyword = self.request.query_params.get("keyword")
        if keyword:
            queryset = queryset.filter(Q(user__first_name__icontains=keyword) | Q(user__last_name__icontains=keyword) | Q(hospital_name__icontains=keyword))
        department = self.request.query_params.get("department")
        return queryset.filter(department_id=department) if department else queryset


class ClinicianDetailView(WrappedModelViewSet):
    queryset = Clinician.objects.select_related("user", "department")
    serializer_class = ClinicianSerializer
    lookup_url_kwarg = "clinician_id"
    http_method_names = ("get", "head", "options")


class ClinicianDashboardView(APIView):
    permission_classes = (ClinicianOrAdmin,)

    def get(self, request):
        clinician = request.user.clinician
        return success({
            "clinician": ClinicianSerializer(clinician).data,
            "scheduled_appointments": clinician.appointments.filter(status="SCHEDULED").count(),
            "open_consultations": clinician.assigned_consultations.exclude(status__in=("COMPLETED", "CANCELLED")).count(),
        })
