from django.urls import path

from .views import (
    ClinicianDashboardView,
    ClinicianDetailView,
    ClinicianListView,
    DepartmentListView,
)


app_name = "clinicians"


urlpatterns = [
    path(
        "departments",
        DepartmentListView.as_view(),
        name="department-list",
    ),
    path(
        "clinicians",
        ClinicianListView.as_view(),
        name="clinician-list",
    ),
    path(
        "clinicians/me/dashboard",
        ClinicianDashboardView.as_view(),
        name="clinician-dashboard",
    ),
    path(
        "clinicians/<uuid:clinician_id>",
        ClinicianDetailView.as_view(),
        name="clinician-detail",
    ),
]