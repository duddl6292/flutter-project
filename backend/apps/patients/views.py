from rest_framework.decorators import action

from apps.core.permissions import ClinicianOrAdmin, PatientOnly
from apps.core.responses import success
from apps.core.viewsets import WrappedModelViewSet

from .models import Patient
from .selectors import search_patients, visible_patients
from .serializers import PatientCreateSerializer, PatientSelfUpdateSerializer, PatientSerializer


class PatientViewSet(WrappedModelViewSet):
    serializer_class = PatientSerializer
    queryset = Patient.objects.none()
    lookup_url_kwarg = "patient_id"

    def get_queryset(self):
        return search_patients(visible_patients(self.request.user), self.request.query_params.get("keyword"))

    def get_serializer_class(self):
        return PatientCreateSerializer if self.action == "create" else PatientSerializer

    def get_permissions(self):
        if self.action in {"me", "home"}:
            return [PatientOnly()]
        return [ClinicianOrAdmin()]

    @action(detail=False, methods=("get", "patch"), url_path="me")
    def me(self, request):
        patient = visible_patients(request.user).get()
        if request.method == "PATCH":
            serializer = PatientSelfUpdateSerializer(patient, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return success(PatientSerializer(patient).data)

    @action(detail=False, methods=("get",), url_path="me/home")
    def home(self, request):
        patient = visible_patients(request.user).get()
        return success({
            "patient": PatientSerializer(patient).data,
            "upcoming_appointments": patient.appointments.filter(status="SCHEDULED").count(),
            "active_prescriptions": patient.prescriptions.filter(status="ACTIVE").count(),
            "unread_notifications": request.user.notifications.filter(is_read=False).count(),
        })

    @action(detail=True, methods=("get",), url_path="summary")
    def summary(self, request, patient_id=None):
        patient = self.get_object()
        return success({
            "patient": PatientSerializer(patient).data,
            "appointment_count": patient.appointments.count(),
            "prescription_count": patient.prescriptions.count(),
            "test_result_count": patient.test_results.count(),
        })
