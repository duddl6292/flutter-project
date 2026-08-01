from django.db import models

from apps.core.models import UUIDTimeStampedModel
from apps.patients.models import Patient
from apps.prescriptions.models import PrescriptionItem


class MedicationStatus(models.TextChoices):
    SCHEDULED = "SCHEDULED", "Scheduled"
    TAKEN = "TAKEN", "Taken"
    MISSED = "MISSED", "Missed"
    SKIPPED = "SKIPPED", "Skipped"


class MedicationSchedule(UUIDTimeStampedModel):
    prescription_item = models.ForeignKey(
        PrescriptionItem, on_delete=models.CASCADE, related_name="schedules"
    )
    scheduled_at = models.DateTimeField()
    status = models.CharField(max_length=16, choices=MedicationStatus.choices, default=MedicationStatus.SCHEDULED)


class MedicationRecord(UUIDTimeStampedModel):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="medication_records")
    prescription_item = models.ForeignKey(
        PrescriptionItem, on_delete=models.PROTECT, related_name="medication_records"
    )
    schedule = models.ForeignKey(
        MedicationSchedule, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="records",
    )
    scheduled_at = models.DateTimeField()
    taken_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=MedicationStatus.choices, default=MedicationStatus.SCHEDULED)
    note = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("patient", "schedule"),
                condition=models.Q(schedule__isnull=False),
                name="unique_medication_record_per_patient_schedule",
            )
        ]
