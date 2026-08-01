from rest_framework import serializers

from .models import MedicationRecord, MedicationSchedule


class MedicationScheduleSerializer(serializers.ModelSerializer):
    schedule_id = serializers.UUIDField(source="id", read_only=True)
    prescription_item_id = serializers.UUIDField(source="prescription_item.id", read_only=True)
    class Meta:
        model = MedicationSchedule
        fields = ("medication_record_id", "prescription_item_id", "schedule_id", "scheduled_at", "taken_at", "status", "note", "created_at", "updated_at")


class MedicationRecordSerializer(serializers.ModelSerializer):
    medication_record_id = serializers.UUIDField(source="id", read_only=True)
    prescription_item_id = serializers.PrimaryKeyRelatedField(source="prescription_item", queryset=__import__("apps.prescriptions.models", fromlist=["PrescriptionItem"]).PrescriptionItem.objects.all())
    schedule_id = serializers.PrimaryKeyRelatedField(source="schedule", queryset=__import__("apps.medications.models", fromlist=["MedicationSchedule"]).MedicationSchedule.objects.all(), required=False, allow_null=True)
    class Meta:
        model = MedicationRecord
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")

    def validate_prescription_item(self, item):
        request = self.context["request"]
        if item.prescription.patient.user_id != request.user.id:
            raise serializers.ValidationError("The prescription item does not belong to the current patient.")
        return item

    def validate(self, attrs):
        schedule = attrs.get("schedule")
        item = attrs.get("prescription_item")
        if schedule and item and schedule.prescription_item_id != item.id:
            raise serializers.ValidationError({"schedule": "Schedule and prescription item do not match."})
        return attrs
