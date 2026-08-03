from django.urls import path

from .views import (
    ProvisionalIdentityDetailView,
    ProvisionalIdentityListCreateView,
    ProvisionalIdentityResolveView,
)


app_name = "provisional-identities"


urlpatterns = [
    path(
        "",
        ProvisionalIdentityListCreateView.as_view(),
        name="provisional-identity-list-create",
    ),
    path(
        "<uuid:provisional_identity_id>/resolve/",
        ProvisionalIdentityResolveView.as_view(),
        name="provisional-identity-resolve",
    ),
    path(
        "<uuid:provisional_identity_id>/",
        ProvisionalIdentityDetailView.as_view(),
        name="provisional-identity-detail",
    ),
]