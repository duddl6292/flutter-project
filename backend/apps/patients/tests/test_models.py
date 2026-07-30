from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.accounts.models import User
from apps.patients.models import PatientProfile


class PatientProfileTests(TestCase):
    def test_patient_role_is_accepted(self) -> None:
        user = User.objects.create_user(
            username="patient",
            password="test-pass",
            role=User.Role.PATIENT,
        )
        profile = PatientProfile.objects.create(user=user)
        self.assertEqual(profile.user, user)

    def test_non_patient_role_is_rejected(self) -> None:
        user = User.objects.create_user(
            username="clinician-for-patient",
            password="test-pass",
            role=User.Role.CLINICIAN,
        )
        with self.assertRaises(ValidationError):
            PatientProfile.objects.create(user=user)
