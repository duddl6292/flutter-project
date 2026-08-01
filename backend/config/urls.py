"""Root URL configuration."""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from apps.accounts.views import MeView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/users/me", MeView.as_view(), name="user-me"),
    path("api/v1/", include("apps.core.urls")),
    path("api/v1/", include("apps.clinicians.urls")),
    path("api/v1/", include("apps.patients.urls")),
    path("api/v1/", include("apps.appointments.urls")),
    path("api/v1/", include("apps.clinical_records.urls")),
    path("api/v1/", include("apps.prescriptions.urls")),
    path("api/v1/", include("apps.medications.urls")),
    path("api/v1/", include("apps.test_results.urls")),
    path("api/v1/", include("apps.consultations.urls")),
    path("api/v1/", include("apps.ct_analysis.urls")),
    path("api/v1/", include("apps.notifications.urls")),
    path("internal/v1/inference/", include("apps.ct_analysis.internal_urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
