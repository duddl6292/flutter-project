from django.urls import path

from .views import (
    NotificationListView,
    NotificationMarkAllReadView,
    NotificationMarkReadView,
    NotificationSettingsView,
)


app_name = "notifications"


urlpatterns = [
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
