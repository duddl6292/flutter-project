from rest_framework import serializers

from apps.hospitals.serializers import HospitalSerializer

from .models import Clinician, Department


class DepartmentSerializer(serializers.ModelSerializer):
    department_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )

    class Meta:
        model = Department
        fields = (
            "department_id",
            "code",
            "name",
            "is_active",
        )


class ClinicianSerializer(serializers.ModelSerializer):
    clinician_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )

    user_id = serializers.UUIDField(
        read_only=True,
    )

    hospital = HospitalSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = Clinician
        fields = (
            "clinician_id",
            "user_id",
            "name",
            "license_number",
            "hospital",
            "department",
            "approval_status",
            "created_at",
            "updated_at",
        )
