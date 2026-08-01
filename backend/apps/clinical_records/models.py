from django.db import models

from apps.appointments.models import Appointment
from apps.clinicians.models import Clinician
from apps.core.models import UUIDTimeStampedModel
from apps.patients.models import Patient


class ClinicalRecord(UUIDTimeStampedModel):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="clinical_records")
    clinician = models.ForeignKey(Clinician, on_delete=models.PROTECT, related_name="clinical_records")
    appointment = models.ForeignKey(
        Appointment, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="clinical_records",
    )
    recorded_at = models.DateTimeField()
    chief_complaint = models.TextField(blank=True)
    subjective = models.TextField(blank=True)
    objective = models.TextField(blank=True)
    assessment = models.TextField(blank=True)
    plan = models.TextField(blank=True)
    patient_visible_summary = models.TextField(blank=True)

    class Meta:
        ordering = ("-recorded_at",)
