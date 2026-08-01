from django.urls import path
from .views import PatientViewSet

patients = PatientViewSet.as_view({"get": "list", "post": "create"})
patient_detail = PatientViewSet.as_view({"get": "retrieve", "patch": "partial_update"})

urlpatterns = [
    path("patients", patients, name="patient-list"),
    path("patients/me", PatientViewSet.as_view({"get": "me", "patch": "me"}), name="patient-me"),
    path("patients/me/home", PatientViewSet.as_view({"get": "home"}), name="patient-home"),
    path("patients/<uuid:patient_id>", patient_detail, name="patient-detail"),
    path("patients/<uuid:patient_id>/summary", PatientViewSet.as_view({"get": "summary"}), name="patient-summary"),
]
