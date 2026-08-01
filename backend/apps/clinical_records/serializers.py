from rest_framework import serializers

from .models import ClinicalRecord


class ClinicalRecordSerializer(serializers.ModelSerializer):
    clinical_record_id = serializers.UUIDField(source="id", read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(source="patient", queryset=__import__("apps.patients.models", fromlist=["Patient"]).Patient.objects.all())
    clinician_id = serializers.UUIDField(source="clinician.id", read_only=True)
    appointment_id = serializers.PrimaryKeyRelatedField(source="appointment", queryset=__import__("apps.appointments.models", fromlist=["Appointment"]).Appointment.objects.all(), required=False, allow_null=True)
    class Meta:
        model = ClinicalRecord
        fields = ("clinical_record_id", "patient_id", "clinician_id", "appointment_id", "recorded_at", "chief_complaint", "subjective", "objective", "assessment", "plan", "patient_visible_summary", "created_at", "updated_at")
        read_only_fields = ("created_at", "updated_at")


class PatientClinicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalRecord
        fields = ("id", "recorded_at", "chief_complaint", "patient_visible_summary", "created_at", "updated_at")
