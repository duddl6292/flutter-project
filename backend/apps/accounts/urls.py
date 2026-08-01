from django.urls import path

from .views import (
    ClinicianLoginView,
    ClinicianSignupView,
    PatientLoginView,
    PatientSignupView,
    TokenRefreshAPIView,
)


app_name = "accounts"


urlpatterns = [
    path(
        "patient/signup/",
        PatientSignupView.as_view(),
        name="patient-signup",
    ),
    path(
        "patient/login/",
        PatientLoginView.as_view(),
        name="patient-login",
    ),
    path(
        "clinician/signup/",
        ClinicianSignupView.as_view(),
        name="clinician-signup",
    ),
    path(
        "clinician/login/",
        ClinicianLoginView.as_view(),
        name="clinician-login",
    ),
    path(
        "token/refresh/",
        TokenRefreshAPIView.as_view(),
        name="token-refresh",
    ),
]