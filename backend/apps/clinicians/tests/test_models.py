from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.accounts.models import User
from apps.clinicians.models import ClinicianProfile


class ClinicianProfileTests(TestCase):
    def test_clinician_role_is_accepted(self) -> None:
        user = User.objects.create_user(
            username="clinician",
            password="test-pass",
            role=User.Role.CLINICIAN,
        )
        profile = ClinicianProfile.objects.create(user=user)
        self.assertEqual(profile.user, user)

    def test_non_clinician_role_is_rejected(self) -> None:
        user = User.objects.create_user(
            username="patient-for-clinician",
            password="test-pass",
            role=User.Role.PATIENT,
        )
        with self.assertRaises(ValidationError):
            ClinicianProfile.objects.create(user=user)
