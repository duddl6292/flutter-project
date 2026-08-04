from django.urls import path

from .views import (
    DeviceRegisterView,
    DeviceUnregisterView,
    NotificationListView,
    NotificationMarkAllReadView,
    NotificationMarkReadView,
    NotificationSettingsView,
)


app_name = "notifications"


urlpatterns = [
    path(
        "devices/register/",
        DeviceRegisterView.as_view(),
        name="device-register",
    ),
    path(
        "devices/unregister/",
        DeviceUnregisterView.as_view(),
        name="device-unregister",
    ),
    path(
        "",
        NotificationListView.as_view(),
        name="notification-list",
    ),
    path(
        "read-all/",
        NotificationMarkAllReadView.as_view(),
        name="notification-read-all",
    ),
    path(
        "settings/",
        NotificationSettingsView.as_view(),
        name="notification-settings",
    ),
    path(
        "<uuid:notification_id>/read/",
        NotificationMarkReadView.as_view(),
        name="notification-read",
    ),
]
