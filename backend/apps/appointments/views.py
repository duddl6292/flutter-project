from rest_framework.decorators import action

from apps.core.permissions import ClinicianOrAdmin
from apps.core.responses import success
from apps.core.viewsets import WrappedModelViewSet

from .models import Appointment
from .selectors import visible_appointments
from .serializers import AppointmentSerializer, CancelAppointmentSerializer
from .services import cancel_appointment


class AppointmentViewSet(WrappedModelViewSet):
    serializer_class = AppointmentSerializer
    queryset = Appointment.objects.none()
    lookup_url_kwarg = "appointment_id"

    def get_queryset(self):
        return visible_appointments(self.request.user)

    def get_permissions(self):
        if self.action in {"create", "partial_update"}:
            return [ClinicianOrAdmin()]
        return super().get_permissions()

    @action(detail=True, methods=("post",))
    def cancel(self, request, appointment_id=None):
        serializer = CancelAppointmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = cancel_appointment(self.get_object(), serializer.validated_data.get("cancellation_reason", ""))
        return success(AppointmentSerializer(appointment).data)
