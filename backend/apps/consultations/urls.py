from django.urls import path

from .views import (
    ConsultationAcceptView,
    ConsultationCancelView,
    ConsultationCompleteView,
    ConsultationContextListView,
    ConsultationDetailView,
    ConsultationListCreateView,
    ConsultationMessageListCreateView,
)


app_name = "consultations"


urlpatterns = [
    path(
        "",
        ConsultationListCreateView.as_view(),
        name="list-create",
    ),
    path(
        "contexts/",
        ConsultationContextListView.as_view(),
        name="contexts",
    ),
    path(
        "<uuid:consultation_id>/",
        ConsultationDetailView.as_view(),
        name="detail",
    ),
    path(
        "<uuid:consultation_id>/accept/",
        ConsultationAcceptView.as_view(),
        name="accept",
    ),
    path(
        "<uuid:consultation_id>/messages/",
        ConsultationMessageListCreateView.as_view(),
        name="messages",
    ),
    path(
        "<uuid:consultation_id>/complete/",
        ConsultationCompleteView.as_view(),
        name="complete",
    ),
    path(
        "<uuid:consultation_id>/cancel/",
        ConsultationCancelView.as_view(),
        name="cancel",
    ),
]
