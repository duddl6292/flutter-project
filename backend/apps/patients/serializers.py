from rest_framework import serializers

from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    patient_id = serializers.UUIDField(source="id", read_only=True)
    user_id = serializers.UUIDField(source="user.id", read_only=True)

    class Meta:
        model = Patient
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "merged_into")


class PatientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ("name", "birth_date", "sex", "phone", "emergency_contact", "address")

    def create(self, validated_data):
        from .services import create_patient
        return create_patient(**validated_data)


class PatientSelfUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ("phone", "emergency_contact", "address")
