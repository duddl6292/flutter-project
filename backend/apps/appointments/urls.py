from django.urls import path

from .views import (
    AppointmentListCreateView,
)


app_name = "appointments"


urlpatterns = [
    path(
        "",
        AppointmentListCreateView.as_view(),
        name="appointment-list-create",
    ),
]