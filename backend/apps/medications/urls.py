from django.urls import path
from .views import MedicationRecordViewSet, MedicationScheduleViewSet, PatientMedicationViewSet

urlpatterns = [
    path("patients/me/medications", PatientMedicationViewSet.as_view({"get": "list"}), name="patient-medications"),
    path("medication-schedules", MedicationScheduleViewSet.as_view({"get": "list"}), name="medication-schedule-list"),
    path("medication-records", MedicationRecordViewSet.as_view({"get": "list", "post": "create"}), name="medication-record-list"),
]
