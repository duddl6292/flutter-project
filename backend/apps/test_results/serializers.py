from rest_framework import serializers

from .models import TestResult


class TestResultSerializer(serializers.ModelSerializer):
    test_result_id = serializers.UUIDField(source="id", read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(source="patient", queryset=__import__("apps.patients.models", fromlist=["Patient"]).Patient.objects.all())
    case_id = serializers.PrimaryKeyRelatedField(source="case", queryset=__import__("apps.ct_analysis.models", fromlist=["CTCase"]).CTCase.objects.all(), required=False, allow_null=True)
    class Meta:
        model = TestResult
        fields = ("test_result_id", "patient_id", "case_id", "test_type", "title", "performed_at", "status", "summary", "clinician_comment", "result_file_uri", "is_released_to_patient", "released_at", "released_by", "created_at", "updated_at")
        read_only_fields = (
            "is_released_to_patient", "released_at", "released_by", "created_at", "updated_at",
        )

    def validate(self, attrs):
        case = attrs.get("case", getattr(self.instance, "case", None))
        patient = attrs.get("patient", getattr(self.instance, "patient", None))
        if case and patient and case.patient_id != patient.id:
            raise serializers.ValidationError({"case": "Case and patient do not match."})
        return attrs
