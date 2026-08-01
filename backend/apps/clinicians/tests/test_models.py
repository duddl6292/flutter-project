from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.accounts.models import User
from apps.clinicians.models import Clinician, Department


class ClinicianTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(code="NEU", name="Neurology")

    def test_clinician_role_is_accepted(self):
        user = User.objects.create_user(username="clinician", password="test-pass", role=User.Role.CLINICIAN)
        clinician = Clinician.objects.create(user=user, license_number="LIC-1", department=self.department, hospital_name="Demo Hospital")
        self.assertEqual(clinician.user, user)

    def test_non_clinician_role_is_rejected(self):
        user = User.objects.create_user(username="patient-for-clinician", password="test-pass", role=User.Role.PATIENT)
        with self.assertRaises(ValidationError):
            Clinician.objects.create(user=user, license_number="LIC-2", department=self.department, hospital_name="Demo Hospital")
