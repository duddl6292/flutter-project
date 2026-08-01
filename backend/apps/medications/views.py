from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import PatientOnly
from apps.core.viewsets import WrappedModelViewSet

from .models import MedicationRecord, MedicationSchedule
from .serializers import MedicationRecordSerializer, MedicationScheduleSerializer


class MedicationScheduleViewSet(WrappedModelViewSet):
    serializer_class = MedicationScheduleSerializer
    permission_classes = (PatientOnly,)
    http_method_names = ("get", "head", "options")

    def get_queryset(self):
        return MedicationSchedule.objects.filter(
            prescription_item__prescription__patient__user=self.request.user
        ).select_related("prescription_item")


class MedicationRecordViewSet(WrappedModelViewSet):
    serializer_class = MedicationRecordSerializer
    permission_classes = (PatientOnly,)
    http_method_names = ("get", "post", "head", "options")

    def get_queryset(self):
        return MedicationRecord.objects.filter(patient__user=self.request.user).select_related("prescription_item", "schedule")

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user.patient)


class PatientMedicationViewSet(MedicationScheduleViewSet):
    pass
