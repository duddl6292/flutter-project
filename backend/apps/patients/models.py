from django.core.exceptions import ValidationError
from django.db import models

from apps.accounts.models import User
from apps.core.models import UUIDTimeStampedModel


class Patient(UUIDTimeStampedModel):
    class Sex(models.TextChoices):
        M = "M", "Male"
        F = "F", "Female"
        UNKNOWN = "UNKNOWN", "Unknown"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        MERGED = "MERGED", "Merged"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient")
    medical_record_number = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=150)
    birth_date = models.DateField()
    sex = models.CharField(max_length=10, choices=Sex.choices, default=Sex.UNKNOWN)
    phone = models.CharField(max_length=30, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    merged_into = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT,
        related_name="merged_patients",
    )

    def clean(self):
        super().clean()
        if self.user.role != User.Role.PATIENT:
            raise ValidationError({"user": "Only PATIENT users can own a patient profile."})
        if self.merged_into_id == self.id:
            raise ValidationError({"merged_into": "A patient cannot be merged into itself."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.medical_record_number})"
