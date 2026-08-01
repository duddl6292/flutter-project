from rest_framework import serializers

from .models import Consultation


class ConsultationSerializer(serializers.ModelSerializer):
    consultation_id = serializers.UUIDField(source="id", read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(source="patient", queryset=__import__("apps.patients.models", fromlist=["Patient"]).Patient.objects.all())
    case_id = serializers.PrimaryKeyRelatedField(source="case", queryset=__import__("apps.ct_analysis.models", fromlist=["CTCase"]).CTCase.objects.all(), required=False, allow_null=True)
    requester_clinician_id = serializers.UUIDField(source="requester_clinician.id", read_only=True)
    consultant_clinician_id = serializers.PrimaryKeyRelatedField(source="consultant_clinician", queryset=__import__("apps.clinicians.models", fromlist=["Clinician"]).Clinician.objects.all())
    class Meta:
        model = Consultation
        fields = ("consultation_id", "patient_id", "case_id", "requester_clinician_id", "consultant_clinician_id", "question", "response", "status", "created_at", "completed_at", "updated_at")
        read_only_fields = ("completed_at", "created_at", "updated_at")

    def validate(self, attrs):
        instance = self.instance
        if instance and instance.status == Consultation.Status.COMPLETED:
            immutable = {"patient", "case", "requester_clinician", "consultant_clinician", "question", "response"}
            if immutable.intersection(attrs):
                raise serializers.ValidationError("Completed consultation content cannot be modified.")
        requester = attrs.get("requester_clinician", getattr(instance, "requester_clinician", None))
        consultant = attrs.get("consultant_clinician", getattr(instance, "consultant_clinician", None))
        if requester and consultant and requester.id == consultant.id:
            raise serializers.ValidationError("Requester and consultant must differ.")
        return attrs
