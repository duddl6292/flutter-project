from rest_framework import serializers

from .models import Hospital


class HospitalSerializer(serializers.ModelSerializer):
    hospital_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )

    hospital_name = serializers.CharField(
        source="name",
        read_only=True,
    )

    class Meta:
        model = Hospital
        fields = [
            "hospital_id",
            "hospital_code",
            "hospital_name",
            "address",
            "phone",
        ]