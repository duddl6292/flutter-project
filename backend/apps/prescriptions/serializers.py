from rest_framework import serializers

from .models import Prescription, PrescriptionItem


class PrescriptionItemSerializer(serializers.ModelSerializer):
    prescription_item_id = serializers.UUIDField(source="id", read_only=True)
    class Meta:
        model = PrescriptionItem
        exclude = ("prescription",)
        read_only_fields = ("id", "created_at", "updated_at")


class PrescriptionSerializer(serializers.ModelSerializer):
    prescription_id = serializers.UUIDField(source="id", read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(source="patient", queryset=__import__("apps.patients.models", fromlist=["Patient"]).Patient.objects.all())
    clinician_id = serializers.UUIDField(source="clinician.id", read_only=True)
    clinical_record_id = serializers.PrimaryKeyRelatedField(source="clinical_record", queryset=__import__("apps.clinical_records.models", fromlist=["ClinicalRecord"]).ClinicalRecord.objects.all(), required=False, allow_null=True)
    items = PrescriptionItemSerializer(many=True)

    class Meta:
        model = Prescription
        fields = ("prescription_id", "patient_id", "clinician_id", "clinical_record_id", "status", "notes", "items", "created_at", "updated_at")
        read_only_fields = ("status", "created_at", "updated_at")

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one prescription item is required.")
        return value

    def create(self, validated_data):
        from .services import create_prescription
        return create_prescription(items=validated_data.pop("items"), **validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("items", None)
        return super().update(instance, validated_data)
