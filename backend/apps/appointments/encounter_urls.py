from django.urls import path

from .views import (
    ClinicianEncounterClinicalRecordView,
    ClinicianEncounterDetailView,
    ClinicianEncounterListView,
    ClinicianEncounterStatusView,
)


app_name = "encounters"


urlpatterns = [
    path(
        "",
        ClinicianEncounterListView.as_view(),
        name="clinician-encounter-list",
    ),
    path(
        "<uuid:encounter_id>/",
        ClinicianEncounterDetailView.as_view(),
        name="clinician-encounter-detail",
    ),
    path(
        "<uuid:encounter_id>/status/",
        ClinicianEncounterStatusView.as_view(),
        name="clinician-encounter-status",
    ),
    path(
        "<uuid:encounter_id>/clinical-record/",
        ClinicianEncounterClinicalRecordView.as_view(),
        name="clinician-encounter-clinical-record",
    ),
]
