from django.contrib import admin
from .models import CTCase, InferenceJob, InferenceResult
admin.site.register((CTCase, InferenceJob, InferenceResult))
