from django.urls import path

from .views import (
    PatientAccountClaimIssueView,
    PatientAppointmentListView,
    PatientCTResultListView,
    PatientDetailView,
    PatientFavoriteHospitalDeleteView,
    PatientFavoriteHospitalListCreateView,
    PatientListView,
    PatientMedicalHistoryView,
    PatientMedicationRecordListView,
    PatientMedicationScheduleListView,
    PatientMeView,
    PatientNotificationListView,
    PatientNotificationReadAllView,
    PatientNotificationReadView,
    PatientPrescriptionListView,
    PatientTestResultListView,
)

app_name = "patients"


urlpatterns = [
    path(
        "",
        PatientListView.as_view(),
        name="patient-list",
    ),
    path(
        "me/",
        PatientMeView.as_view(),
        name="patient-me",
    ),

    path(
    "me/medical-history/",
    PatientMedicalHistoryView.as_view(),
    name="patient-medical-history",
    ),
    path(
    "me/appointments/",
    PatientAppointmentListView.as_view(),
    name="patient-appointment-list",
    ),
    path(
        "me/test-results/",
        PatientTestResultListView.as_view(),
        name="patient-test-result-list",
    ),
    path(
        "me/prescriptions/",
        PatientPrescriptionListView.as_view(),
        name="patient-prescription-list",
    ),
    path(
        "me/medication-schedules/",
        PatientMedicationScheduleListView.as_view(),
        name="patient-medication-schedule-list",
    ),
    path(
        "me/medication-records/",
        PatientMedicationRecordListView.as_view(),
        name="patient-medication-record-list",
    ),
    path(
        "me/ct-results/",
        PatientCTResultListView.as_view(),
        name="patient-ct-result-list",
    ),
    path(
    "me/favorite-hospitals/",
    PatientFavoriteHospitalListCreateView.as_view(),
    name="patient-favorite-hospital-list-create",
    ),
    path(
        "me/favorite-hospitals/<uuid:hospital_id>/",
        PatientFavoriteHospitalDeleteView.as_view(),
        name="patient-favorite-hospital-delete",
    ),
    path(
    "me/notifications/",
    PatientNotificationListView.as_view(),
    name="patient-notification-list",
    ),
    path(
        "me/notifications/read-all/",
        PatientNotificationReadAllView.as_view(),
        name="patient-notification-read-all",
    ),
    path(
        "me/notifications/<uuid:notification_id>/read/",
        PatientNotificationReadView.as_view(),
        name="patient-notification-read",
    ),

    path(
    "<uuid:patient_id>/account-claims/",
    PatientAccountClaimIssueView.as_view(),
    name="patient-account-claim-issue",
    ),

    path(
        "<uuid:patient_id>/",
        PatientDetailView.as_view(),
        name="patient-detail",
    ),
]