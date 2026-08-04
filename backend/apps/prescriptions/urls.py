from django.urls import path

from .views import (
    ClinicianPrescriptionContextListView,
    ClinicianPrescriptionDetailView,
    ClinicianPrescriptionListCreateView,
    ClinicianPrescriptionStatusView,
)


app_name = "prescriptions"


urlpatterns = [
    path(
        "",
        ClinicianPrescriptionListCreateView.as_view(),
        name="clinician-prescription-list-create",
    ),
    path(
        "contexts/",
        ClinicianPrescriptionContextListView.as_view(),
        name="clinician-prescription-context-list",
    ),
    path(
        "<uuid:prescription_id>/",
        ClinicianPrescriptionDetailView.as_view(),
        name="clinician-prescription-detail",
    ),
    path(
        "<uuid:prescription_id>/status/",
        ClinicianPrescriptionStatusView.as_view(),
        name="clinician-prescription-status",
    ),
]
