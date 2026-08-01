from django.urls import path

from .views import (
    PatientDetailView,
    PatientListView,
    PatientMeView,
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
        "<uuid:patient_id>/",
        PatientDetailView.as_view(),
        name="patient-detail",
    ),
]