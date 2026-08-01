from django.urls import path
from .views import InferenceCallbackView

urlpatterns = [path("callback", InferenceCallbackView.as_view(), name="inference-callback")]
