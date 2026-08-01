from rest_framework.decorators import action

from apps.core.permissions import ClinicianOrAdmin
from apps.core.responses import success
from apps.core.viewsets import WrappedModelViewSet

from .models import Prescription
from .selectors import visible_prescriptions
from .serializers import PrescriptionSerializer
from .services import discontinue_prescription


class PrescriptionViewSet(WrappedModelViewSet):
    serializer_class = PrescriptionSerializer
    queryset = Prescription.objects.none()
    lookup_url_kwarg = "prescription_id"

    def get_queryset(self):
        return visible_prescriptions(self.request.user)

    def get_permissions(self):
        if self.action in {"create", "partial_update", "discontinue"}:
            return [ClinicianOrAdmin()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(clinician=self.request.user.clinician)

    @action(detail=True, methods=("post",))
    def discontinue(self, request, prescription_id=None):
        return success(PrescriptionSerializer(discontinue_prescription(self.get_object())).data)
