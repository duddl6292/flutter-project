from django.core.exceptions import ValidationError
from django.db import models

from apps.accounts.models import User
from apps.core.models import UUIDTimeStampedModel


class Department(UUIDTimeStampedModel):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Clinician(UUIDTimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="clinician")
    license_number = models.CharField(max_length=64, unique=True)
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="clinicians"
    )
    hospital_name = models.CharField(max_length=200)

    def clean(self):
        super().clean()
        if self.user.role != User.Role.CLINICIAN:
            raise ValidationError({"user": "Only CLINICIAN users can own a clinician profile."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.license_number})"
