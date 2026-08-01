from rest_framework import serializers

from apps.clinicians.serializers import ClinicianSerializer, DepartmentSerializer

from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    appointment_id = serializers.UUIDField(source="id", read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(source="patient", queryset=__import__("apps.patients.models", fromlist=["Patient"]).Patient.objects.all())
    clinician_id = serializers.PrimaryKeyRelatedField(source="clinician", queryset=__import__("apps.clinicians.models", fromlist=["Clinician"]).Clinician.objects.all(), write_only=True)
    department_id = serializers.PrimaryKeyRelatedField(source="department", queryset=__import__("apps.clinicians.models", fromlist=["Department"]).Department.objects.all(), write_only=True)
    clinician = ClinicianSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    class Meta:
        model = Appointment
        fields = ("appointment_id", "patient_id", "clinician_id", "department_id", "clinician", "department", "scheduled_at", "reason", "status", "created_at", "updated_at")
        read_only_fields = ("created_at", "updated_at")

    def validate(self, attrs):
        clinician = attrs.get("clinician", getattr(self.instance, "clinician", None))
        department = attrs.get("department", getattr(self.instance, "department", None))
        if clinician and department and clinician.department_id != department.id:
            raise serializers.ValidationError({"department": "Clinician does not belong to this department."})
        if self.instance and self.instance.status in {
            Appointment.Status.COMPLETED, Appointment.Status.CANCELLED
        } and attrs:
            raise serializers.ValidationError("Completed or cancelled appointments cannot be modified.")
        return attrs


class CancelAppointmentSerializer(serializers.Serializer):
    cancellation_reason = serializers.CharField(required=False, allow_blank=True)
