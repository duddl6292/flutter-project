import uuid

from django.test import SimpleTestCase
from django.urls import resolve

from apps.accounts.models import User
from apps.appointments.models import Appointment
from apps.ct_analysis.models import CTCase, InferenceJob


class ModelContractTests(SimpleTestCase):
    def test_major_models_use_uuid_primary_keys(self):
        for model in (User, Appointment, CTCase, InferenceJob):
            self.assertEqual(model._meta.pk.get_internal_type(), "UUIDField")

    def test_contract_enums_are_uppercase(self):
        for choices in (User.Role, Appointment.Status, CTCase.Status, InferenceJob.Status):
            for value, _label in choices.choices:
                self.assertEqual(value, value.upper())


class UrlContractTests(SimpleTestCase):
    def test_uuid_parameter_names_resolve(self):
        identifiers = {
            "/api/v1/patients/{}/summary": "patient_id",
            "/api/v1/appointments/{}/cancel": "appointment_id",
            "/api/v1/cases/{}/result": "case_id",
            "/api/v1/inference-jobs/{}/cancel": "job_id",
        }
        value = uuid.uuid4()
        for template, parameter in identifiers.items():
            match = resolve(template.format(value))
            self.assertEqual(match.kwargs[parameter], value)
