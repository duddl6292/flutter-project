from rest_framework import serializers

from .models import Clinician, Department


class DepartmentSerializer(serializers.ModelSerializer):
    department_id = serializers.UUIDField(source="id", read_only=True)
    class Meta:
        model = Department
        fields = "__all__"


class ClinicianSerializer(serializers.ModelSerializer):
    clinician_id = serializers.UUIDField(source="id", read_only=True)
    user_id = serializers.UUIDField(source="user.id", read_only=True)
    name = serializers.SerializerMethodField()
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Clinician
        fields = "__all__"

    def get_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
