from django.core.exceptions import ValidationError
from django.db import models

from apps.accounts.models import User


class PatientProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="patient_profile",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self) -> None:
        super().clean()
        if self.user.role != User.Role.PATIENT:
            raise ValidationError({"user": "PATIENT 역할 사용자만 연결할 수 있습니다."})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
