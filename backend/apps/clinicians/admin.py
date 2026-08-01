from django.contrib import admin
from .models import Clinician, Department
admin.site.register((Clinician, Department))
