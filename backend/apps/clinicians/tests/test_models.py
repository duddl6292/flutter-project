from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.accounts.models import User
from apps.clinicians.models import Clinician, Department
from apps.hospitals.models import Hospital


class ClinicianModelTests(TestCase):
    def setUp(self):
        self.hospital = Hospital.objects.create(
            hospital_code="H001",
            name="테스트 병원",
        )

        self.department = Department.objects.create(
            code="NEU",
            name="신경과",
        )

    def test_clinician_can_be_created(self):
        user = User.objects.create_user(
            username="123456",
            password="test-password",
            role=User.Role.CLINICIAN,
        )

        clinician = Clinician.objects.create(
            user=user,
            name="테스트 의사",
            license_number="123456",
            hospital=self.hospital,
            department=self.department,
        )

        self.assertEqual(
            clinician.user.role,
            User.Role.CLINICIAN,
        )