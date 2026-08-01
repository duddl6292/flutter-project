from django.db import models

from apps.clinicians.models import Clinician, Department
from apps.core.models import UUIDTimeStampedModel
from apps.patients.models import Patient


class Appointment(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        NO_SHOW = "NO_SHOW", "No show"

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="appointments")
    clinician = models.ForeignKey(Clinician, on_delete=models.PROTECT, related_name="appointments")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="appointments")
    scheduled_at = models.DateTimeField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.SCHEDULED)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)

    class Meta:
        ordering = ("-scheduled_at",)
