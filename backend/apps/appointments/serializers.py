from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from apps.clinicians.models import Clinician
from apps.patients.models import Patient

from .models import Appointment


class AppointmentSummarySerializer(
    serializers.ModelSerializer
):
    appointment_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )

    patient_id = serializers.UUIDField(
        source="patient.id",
        read_only=True,
    )

    patient_number = serializers.CharField(
        source="patient.medical_record_number",
        read_only=True,
        allow_null=True,
    )

    patient_name = serializers.CharField(
        source="patient.name",
        read_only=True,
    )

    clinician_id = serializers.UUIDField(
        source="clinician.id",
        read_only=True,
    )

    clinician_name = serializers.CharField(
        source="clinician.name",
        read_only=True,
    )

    department_code = serializers.CharField(
        source="department.code",
        read_only=True,
    )

    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
    )

    hospital_id = serializers.UUIDField(
        source="hospital.id",
        read_only=True,
        allow_null=True,
    )

    hospital_name = serializers.CharField(
        source="hospital.name",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Appointment

        fields = [
            "appointment_id",
            "patient_id",
            "patient_number",
            "patient_name",
            "clinician_id",
            "clinician_name",
            "department_code",
            "department_name",
            "hospital_id",
            "hospital_name",
            "scheduled_at",
            "duration_minutes",
            "location",
            "reason",
            "status",
        ]


class AppointmentCreateSerializer(
    serializers.Serializer
):
    patient_id = serializers.UUIDField()

    scheduled_at = serializers.DateTimeField()

    duration_minutes = serializers.ChoiceField(
        choices=Appointment.Duration.choices,
        default=Appointment.Duration.THIRTY,
    )

    location = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
    )

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    def validate(self, attrs):
        request = self.context["request"]

        try:
            clinician = (
                Clinician.objects
                .select_related(
                    "hospital",
                    "department",
                )
                .get(user=request.user)
            )
        except Clinician.DoesNotExist:
            raise serializers.ValidationError({
                "clinician": (
                    "의료진 프로필을 찾을 수 없습니다."
                ),
            })

        if (
            clinician.approval_status
            != Clinician.ApprovalStatus.APPROVED
        ):
            raise serializers.ValidationError({
                "clinician": (
                    "승인된 의료진만 예약을 등록할 수 있습니다."
                ),
            })

        try:
            patient = Patient.objects.get(
                id=attrs["patient_id"],
                status=Patient.Status.ACTIVE,
            )
        except Patient.DoesNotExist:
            raise serializers.ValidationError({
                "patient_id": (
                    "활성 환자를 찾을 수 없습니다."
                ),
            })

        scheduled_at = attrs["scheduled_at"]

        if scheduled_at <= timezone.now():
            raise serializers.ValidationError({
                "scheduled_at": (
                    "과거 시간으로 예약할 수 없습니다."
                ),
            })

        requested_end = (
            scheduled_at
            + timedelta(
                minutes=attrs[
                    "duration_minutes"
                ],
            )
        )

        possible_conflicts = (
            Appointment.objects
            .filter(
                clinician=clinician,
                scheduled_at__lt=requested_end,
                scheduled_at__gte=(
                    scheduled_at
                    - timedelta(hours=8)
                ),
            )
            .exclude(
                status__in=[
                    Appointment.Status.CANCELLED,
                    Appointment.Status.NO_SHOW,
                ],
            )
        )

        for existing in possible_conflicts:
            existing_end = (
                existing.scheduled_at
                + timedelta(
                    minutes=(
                        existing.duration_minutes
                    ),
                )
            )

            if existing_end > scheduled_at:
                raise serializers.ValidationError({
                    "scheduled_at": (
                        "해당 시간에는 이미 "
                        "다른 예약이 있습니다."
                    ),
                })

        attrs["_patient"] = patient
        attrs["_clinician"] = clinician

        return attrs

    def create(self, validated_data):
        patient = validated_data.pop(
            "_patient"
        )

        clinician = validated_data.pop(
            "_clinician"
        )

        validated_data.pop(
            "patient_id"
        )

        return Appointment.objects.create(
            patient=patient,
            clinician=clinician,
            department=clinician.department,
            hospital=clinician.hospital,
            status=Appointment.Status.SCHEDULED,
            **validated_data,
        )
