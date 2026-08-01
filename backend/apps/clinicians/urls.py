from django.urls import path
from .views import ClinicianDashboardView, ClinicianDetailView, ClinicianListView, DepartmentListView

urlpatterns = [
    path("departments", DepartmentListView.as_view({"get": "list"}), name="department-list"),
    path("clinicians", ClinicianListView.as_view({"get": "list"}), name="clinician-list"),
    path("clinicians/me/dashboard", ClinicianDashboardView.as_view(), name="clinician-dashboard"),
    path("clinicians/<uuid:clinician_id>", ClinicianDetailView.as_view({"get": "retrieve"}), name="clinician-detail"),
]
