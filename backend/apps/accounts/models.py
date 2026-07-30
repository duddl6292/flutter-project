from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = "PATIENT", "환자"
        CLINICIAN = "CLINICIAN", "의료진"
        ADMIN = "ADMIN", "관리자"

    role = models.CharField(max_length=16, choices=Role.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = [*AbstractUser.REQUIRED_FIELDS, "role"]

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(role=""),
                name="accounts_user_role_required",
            )
        ]
