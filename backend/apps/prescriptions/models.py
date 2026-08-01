from django.db import models

from apps.clinicians.models import Clinician
from apps.clinical_records.models import ClinicalRecord
from apps.core.models import UUIDTimeStampedModel
from apps.patients.models import Patient


class Prescription(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        DISCONTINUED = "DISCONTINUED", "Discontinued"
        COMPLETED = "COMPLETED", "Completed"

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="prescriptions")
    clinician = models.ForeignKey(Clinician, on_delete=models.PROTECT, related_name="prescriptions")
    clinical_record = models.ForeignKey(
        ClinicalRecord, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="prescriptions",
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    notes = models.TextField(blank=True)
    discontinued_at = models.DateTimeField(null=True, blank=True)


class PrescriptionItem(UUIDTimeStampedModel):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="items")
    medicine_name = models.CharField(max_length=200)
    dosage = models.DecimalField(max_digits=10, decimal_places=3)
    dose_unit = models.CharField(max_length=30)
    frequency = models.CharField(max_length=100)
    route = models.CharField(max_length=50)
    instructions = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
