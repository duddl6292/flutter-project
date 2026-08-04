from django.urls import path

from .views import (
    ClinicianDetailReportView,
    ClinicianSummaryReportView,
)


app_name = "reports"


urlpatterns = [
    path(
        "clinician-summary/",
        ClinicianSummaryReportView.as_view(),
        name="clinician-summary",
    ),
    path(
        "clinician-details/",
        ClinicianDetailReportView.as_view(),
        name="clinician-details",
    ),
]
