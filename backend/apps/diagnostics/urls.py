from django.urls import path

from .views import (
    ExaminationContextListView,
    ExaminationDetailView,
    ExaminationFinalizeView,
    ExaminationListCreateView,
    ExaminationReleaseView,
)


app_name = "diagnostics"


urlpatterns = [
    path(
        "",
        ExaminationListCreateView.as_view(),
        name="list-create",
    ),
    path(
        "contexts/",
        ExaminationContextListView.as_view(),
        name="contexts",
    ),
    path(
        "<uuid:examination_id>/",
        ExaminationDetailView.as_view(),
        name="detail",
    ),
    path(
        "<uuid:examination_id>/finalize/",
        ExaminationFinalizeView.as_view(),
        name="finalize",
    ),
    path(
        "<uuid:examination_id>/release/",
        ExaminationReleaseView.as_view(),
        name="release",
    ),
]
