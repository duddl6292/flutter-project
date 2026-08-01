from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import Appointment


@transaction.atomic
def cancel_appointment(appointment, reason=""):
    appointment = Appointment.objects.select_for_update().get(pk=appointment.pk)
    if appointment.status == Appointment.Status.CANCELLED:
        raise ValidationError("Appointment is already cancelled.", code="CONFLICT")
    if appointment.status != Appointment.Status.SCHEDULED:
        raise ValidationError("Only scheduled appointments can be cancelled.")
    appointment.status = Appointment.Status.CANCELLED
    appointment.cancelled_at = timezone.now()
    appointment.cancellation_reason = reason
    appointment.save(update_fields=("status", "cancelled_at", "cancellation_reason", "updated_at"))
    return appointment
