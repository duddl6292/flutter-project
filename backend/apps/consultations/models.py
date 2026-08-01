from django.db import models

from apps.clinicians.models import Clinician
from apps.core.models import UUIDTimeStampedModel
from apps.ct_analysis.models import CTCase
from apps.patients.models import Patient


class Consultation(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"
        IN_REVIEW = "IN_REVIEW", "In review"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="consultations")
    case = models.ForeignKey(CTCase, null=True, blank=True, on_delete=models.SET_NULL, related_name="consultations")
    requester_clinician = models.ForeignKey(Clinician, on_delete=models.PROTECT, related_name="requested_consultations")
    consultant_clinician = models.ForeignKey(Clinician, on_delete=models.PROTECT, related_name="assigned_consultations")
    question = models.TextField()
    response = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.REQUESTED)
    completed_at = models.DateTimeField(null=True, blank=True)
