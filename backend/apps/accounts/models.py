from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import UUIDTimeStampedModel


class User(UUIDTimeStampedModel, AbstractUser):
    class Role(models.TextChoices):
        PATIENT = "PATIENT", "Patient"
        CLINICIAN = "CLINICIAN", "Clinician"
        ADMIN = "ADMIN", "Administrator"

    role = models.CharField(max_length=16, choices=Role.choices)
    REQUIRED_FIELDS = [*AbstractUser.REQUIRED_FIELDS, "role"]

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(role=""), name="accounts_user_role_required"
            )
        ]
