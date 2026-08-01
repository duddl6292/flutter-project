from django.contrib import admin
from .models import MedicationRecord, MedicationSchedule
admin.site.register((MedicationRecord, MedicationSchedule))
