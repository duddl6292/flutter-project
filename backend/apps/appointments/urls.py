from django.urls import path
from .views import AppointmentViewSet

urlpatterns = [
    path("appointments", AppointmentViewSet.as_view({"get": "list", "post": "create"}), name="appointment-list"),
    path("appointments/<uuid:appointment_id>", AppointmentViewSet.as_view({"get": "retrieve", "patch": "partial_update"}), name="appointment-detail"),
    path("appointments/<uuid:appointment_id>/cancel", AppointmentViewSet.as_view({"post": "cancel"}), name="appointment-cancel"),
]
