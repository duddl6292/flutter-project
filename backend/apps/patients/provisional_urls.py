from django.urls import path

from .views import (
    ProvisionalIdentityDetailView,
    ProvisionalIdentityListCreateView,
)


app_name = "provisional_identities"


urlpatterns = [
    path(
        "",
        ProvisionalIdentityListCreateView.as_view(),
        name="provisional-identity-list-create",
    ),
    path(
        "<uuid:provisional_identity_id>/",
        ProvisionalIdentityDetailView.as_view(),
        name="provisional-identity-detail",
    ),
]