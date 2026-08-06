from django.urls import path

from .views import (
    AppointmentDetailView,
    AppointmentListCreateView,
)


app_name = "appointments"


urlpatterns = [
    path(
        "",
        AppointmentListCreateView.as_view(),
        name="appointment-list-create",
    ),
    path(
        "<uuid:appointment_id>/",
        AppointmentDetailView.as_view(),
        name="appointment-detail",
    ),
]
