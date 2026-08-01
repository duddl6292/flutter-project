from django.db import models

from apps.clinicians.models import Clinician
from apps.core.models import UUIDTimeStampedModel
from apps.ct_analysis.models import CTCase
from apps.patients.models import Patient


class TestResult(UUIDTimeStampedModel):
    class TestType(models.TextChoices):
        BRAIN_CT = "BRAIN_CT", "Brain CT"
        MRI = "MRI", "MRI"
        LAB = "LAB", "Laboratory"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        FINAL = "FINAL", "Final"

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="test_results")
    case = models.ForeignKey(CTCase, null=True, blank=True, on_delete=models.SET_NULL, related_name="test_results")
    test_type = models.CharField(max_length=16, choices=TestType.choices)
    title = models.CharField(max_length=200)
    performed_at = models.DateTimeField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    summary = models.TextField(blank=True)
    clinician_comment = models.TextField(blank=True)
    result_file_uri = models.CharField(max_length=1000, blank=True)
    is_released_to_patient = models.BooleanField(default=False)
    released_at = models.DateTimeField(null=True, blank=True)
    released_by = models.ForeignKey(Clinician, null=True, blank=True, on_delete=models.SET_NULL, related_name="released_test_results")
    created_by = models.ForeignKey(Clinician, on_delete=models.PROTECT, related_name="created_test_results")
