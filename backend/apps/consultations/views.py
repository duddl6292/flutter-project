from apps.core.permissions import ClinicianOrAdmin
from apps.core.viewsets import WrappedModelViewSet

from .models import Consultation
from .serializers import ConsultationSerializer
from .services import update_consultation


class ConsultationViewSet(WrappedModelViewSet):
    serializer_class = ConsultationSerializer
    permission_classes = (ClinicianOrAdmin,)
    lookup_url_kwarg = "consultation_id"

    def get_queryset(self):
        queryset = Consultation.objects.select_related("patient", "case", "requester_clinician", "consultant_clinician")
        if self.request.user.role == "CLINICIAN":
            queryset = queryset.filter(requester_clinician__user=self.request.user) | queryset.filter(consultant_clinician__user=self.request.user)
        return queryset.distinct()

    def perform_update(self, serializer):
        serializer.instance = update_consultation(serializer.instance, serializer.validated_data)

    def perform_create(self, serializer):
        serializer.save(requester_clinician=self.request.user.clinician)
