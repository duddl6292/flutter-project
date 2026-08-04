"""Root URL configuration."""

from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/", include("apps.core.urls")),
    path("api/v1/hospitals/", include("apps.hospitals.urls")),
    path("api/v1/clinicians/", include("apps.clinicians.urls")),
    path("api/v1/patients/", include("apps.patients.urls")),
    path("api/v1/appointments/", include("apps.appointments.urls")),
    path("api/v1/encounters/", include("apps.appointments.encounter_urls")),
    path("api/v1/prescriptions/", include("apps.prescriptions.urls")),
    path("api/v1/reports/", include("apps.reports.urls")),
    path("api/v1/notifications/", include("apps.notifications.urls")),
    path("api/v1/provisional-identities/", include("apps.patients.provisional_urls")),
]
