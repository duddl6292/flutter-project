from django.urls import path

from .views import LoginView, LogoutView, MeView, PasswordResetView, RefreshView


urlpatterns = [
    path("login", LoginView.as_view(), name="auth-login"),
    path("token/refresh", RefreshView.as_view(), name="auth-refresh"),
    path("logout", LogoutView.as_view(), name="auth-logout"),
    path("password/reset", PasswordResetView.as_view(), name="password-reset"),
]
