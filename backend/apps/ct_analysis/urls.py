from django.urls import path

from .views import (
    CTCaseAssetView,
    CTCaseDetailView,
    CTCaseListCreateView,
    CTCaseRunView,
    CTSourceListView,
)


app_name = "ct_analysis"

urlpatterns = [
    path("sources/", CTSourceListView.as_view(), name="source-list"),
    path("cases/", CTCaseListCreateView.as_view(), name="case-list-create"),
    path("cases/<uuid:case_id>/", CTCaseDetailView.as_view(), name="case-detail"),
    path("cases/<uuid:case_id>/run/", CTCaseRunView.as_view(), name="case-run"),
    path("cases/<uuid:case_id>/source/", CTCaseAssetView.as_view(), {"asset": "source"}, name="case-source"),
    path("cases/<uuid:case_id>/mask/", CTCaseAssetView.as_view(), {"asset": "mask"}, name="case-mask"),
    path("cases/<uuid:case_id>/preview/", CTCaseAssetView.as_view(), {"asset": "preview"}, name="case-preview"),
]
