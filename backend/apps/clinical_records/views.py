from apps.core.permissions import ClinicianOrAdmin
from apps.core.viewsets import WrappedModelViewSet

from .models import ClinicalRecord
from .selectors import visible_clinical_records
from .serializers import ClinicalRecordSerializer, PatientClinicalRecordSerializer


class ClinicalRecordViewSet(WrappedModelViewSet):
    queryset = ClinicalRecord.objects.none()
    lookup_url_kwarg = "clinical_record_id"

    def get_queryset(self):
        return visible_clinical_records(self.request.user)

    def get_serializer_class(self):
        return PatientClinicalRecordSerializer if self.request.user.role == "PATIENT" else ClinicalRecordSerializer

    def get_permissions(self):
        if self.action in {"create", "partial_update"}:
            return [ClinicianOrAdmin()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(clinician=self.request.user.clinician)
