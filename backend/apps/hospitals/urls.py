from django.urls import path

from .views import HospitalListView


app_name = "hospitals"


urlpatterns = [
    path(
        "",
        HospitalListView.as_view(),
        name="hospital-list",
    ),
]