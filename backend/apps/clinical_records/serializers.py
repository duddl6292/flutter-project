from rest_framework import serializers

from .models import ClinicalRecord


class ClinicalRecordSerializer(
    serializers.ModelSerializer
):
    clinical_record_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )

    class Meta:
        model = ClinicalRecord
        fields = [
            "clinical_record_id",
            "recorded_at",
            "chief_complaint",
            "subjective",
            "objective",
            "assessment",
            "plan",
            "patient_visible_summary",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "clinical_record_id",
            "recorded_at",
            "created_at",
            "updated_at",
        ]


class ClinicalRecordUpsertSerializer(
    serializers.Serializer
):
    chief_complaint = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    subjective = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    objective = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    assessment = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    plan = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    patient_visible_summary = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError(
                "저장할 진료기록을 입력해주세요."
            )

        return attrs
