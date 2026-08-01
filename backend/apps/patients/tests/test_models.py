from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.accounts.models import User
from apps.patients.models import Patient


class PatientTests(TestCase):
    def test_patient_role_is_accepted(self):
        user = User.objects.create_user(username="patient", password="test-pass", role=User.Role.PATIENT)
        patient = Patient.objects.create(user=user, medical_record_number="MRN-1", name="Demo", birth_date=date(1990, 1, 1))
        self.assertEqual(patient.user, user)

    def test_non_patient_role_is_rejected(self):
        user = User.objects.create_user(username="clinician-for-patient", password="test-pass", role=User.Role.CLINICIAN)
        with self.assertRaises(ValidationError):
            Patient.objects.create(user=user, medical_record_number="MRN-2", name="Demo", birth_date=date(1990, 1, 1))
