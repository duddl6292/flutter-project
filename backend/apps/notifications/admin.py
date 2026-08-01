from django.contrib import admin
from .models import Device, Notification
admin.site.register((Device, Notification))
