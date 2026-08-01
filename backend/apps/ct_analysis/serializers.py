from rest_framework import serializers

from .models import CTCase, InferenceJob, InferenceResult


class CTCaseSerializer(serializers.ModelSerializer):
    case_id = serializers.UUIDField(source="id", read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(source="patient", queryset=__import__("apps.patients.models", fromlist=["Patient"]).Patient.objects.all())
    class Meta:
        model = CTCase
        fields = ("case_id", "patient_id", "study_type", "description", "status", "input_uri", "created_at", "updated_at")
        read_only_fields = ("status", "input_uri", "created_at", "updated_at")


class UploadUrlSerializer(serializers.Serializer):
    file_name = serializers.CharField(default="ct.nii.gz")
    content_type = serializers.CharField()


class UploadCompleteSerializer(serializers.Serializer):
    object_path = serializers.CharField()
    file_size = serializers.IntegerField(min_value=1)
    sha256 = serializers.RegexField(r"^[0-9a-fA-F]{64}$")
    content_type = serializers.CharField()


class InferenceStartSerializer(serializers.Serializer):
    parameters = serializers.JSONField(required=False, default=dict)


class InferenceJobSerializer(serializers.ModelSerializer):
    job_id = serializers.UUIDField(source="id", read_only=True)
    case_id = serializers.UUIDField(source="case.id", read_only=True)

    class Meta:
        model = InferenceJob
        fields = "__all__"


class InferenceResultSerializer(serializers.ModelSerializer):
    case_id = serializers.UUIDField(source="case.id", read_only=True)
    job_id = serializers.UUIDField(source="job.id", read_only=True)
    class Meta:
        model = InferenceResult
        fields = "__all__"


class InferenceCallbackSerializer(serializers.Serializer):
    job_id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=InferenceJob.Status.choices)
    progress = serializers.IntegerField(min_value=0, max_value=100, required=False)
    result = serializers.JSONField(required=False, default=dict)
    error = serializers.JSONField(required=False, default=dict)
