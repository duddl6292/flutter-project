from django.utils import timezone
from rest_framework import serializers

from apps.clinicians.models import Clinician
from apps.clinical_records.serializers import (
    ClinicalRecordSerializer,
)
from apps.patients.models import Patient

from .models import Appointment, Encounter
from .services import (
    AppointmentSchedulingError,
    create_appointment,
)


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

        request = self.context["request"]

        try:
            return create_appointment(
                patient=patient,
                clinician_id=clinician.id,
                created_by=request.user,
                **validated_data,
            )
        except AppointmentSchedulingError as exc:
            raise serializers.ValidationError({
                exc.field: exc.message,
            }) from exc


class EncounterListQuerySerializer(serializers.Serializer):
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    status = serializers.ChoiceField(
        choices=Encounter.Status.choices,
        required=False,
    )
    search = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
    )

    def validate(self, attrs):
        date_from = attrs.get("date_from")
        date_to = attrs.get("date_to")

        if date_from and date_to and date_to < date_from:
            raise serializers.ValidationError({
                "date_to": (
                    "종료일은 시작일보다 빠를 수 없습니다."
                ),
            })

        return attrs


class EncounterStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=Encounter.Status.choices,
    )


class EncounterSummarySerializer(
    serializers.ModelSerializer
):
    encounter_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )
    encounter_type_label = serializers.CharField(
        source="get_encounter_type_display",
        read_only=True,
    )
    status_label = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    patient_id = serializers.UUIDField(
        source="patient.id",
        read_only=True,
        allow_null=True,
    )
    patient_number = serializers.CharField(
        source="patient.medical_record_number",
        read_only=True,
        allow_null=True,
    )
    patient_name = serializers.SerializerMethodField()
    patient_birth_date = serializers.DateField(
        source="patient.birth_date",
        read_only=True,
        allow_null=True,
    )
    patient_sex = serializers.CharField(
        source="patient.sex",
        read_only=True,
        allow_null=True,
    )
    appointment_id = serializers.UUIDField(
        source="appointment.id",
        read_only=True,
        allow_null=True,
    )
    scheduled_at = serializers.DateTimeField(
        source="appointment.scheduled_at",
        read_only=True,
        allow_null=True,
    )
    appointment_reason = serializers.CharField(
        source="appointment.reason",
        read_only=True,
        allow_null=True,
    )
    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
    )
    clinician_id = serializers.UUIDField(
        source="attending_clinician.id",
        read_only=True,
    )
    clinician_name = serializers.CharField(
        source="attending_clinician.name",
        read_only=True,
    )
    hospital_name = serializers.CharField(
        source="hospital.name",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Encounter
        fields = [
            "encounter_id",
            "encounter_number",
            "encounter_type",
            "encounter_type_label",
            "status",
            "status_label",
            "patient_id",
            "patient_number",
            "patient_name",
            "patient_birth_date",
            "patient_sex",
            "appointment_id",
            "scheduled_at",
            "appointment_reason",
            "department_name",
            "clinician_id",
            "clinician_name",
            "hospital_name",
            "arrived_at",
            "started_at",
            "completed_at",
            "created_at",
        ]

    def get_patient_name(self, encounter):
        if encounter.patient_id:
            return encounter.patient.name

        return encounter.provisional_identity.temporary_name


class EncounterDetailSerializer(
    EncounterSummarySerializer
):
    clinical_record = serializers.SerializerMethodField()
    prescriptions = serializers.SerializerMethodField()
    ct_cases = serializers.SerializerMethodField()

    class Meta(EncounterSummarySerializer.Meta):
        fields = [
            *EncounterSummarySerializer.Meta.fields,
            "clinical_record",
            "prescriptions",
            "ct_cases",
        ]

    def get_clinical_record(self, encounter):
        record = encounter.clinical_records.first()

        if record is None:
            return None

        return ClinicalRecordSerializer(record).data

    def get_prescriptions(self, encounter):
        return [
            {
                "prescription_id": str(prescription.id),
                "status": prescription.status,
                "status_label": (
                    prescription.get_status_display()
                ),
                "prescribed_at": prescription.prescribed_at,
                "medicine_names": [
                    item.medicine_name
                    for item in prescription.items.all()
                ],
            }
            for prescription in encounter.prescriptions.all()
        ]

    def get_ct_cases(self, encounter):
        return [
            {
                "case_id": str(case.id),
                "study_type": case.study_type,
                "study_type_label": (
                    case.get_study_type_display()
                ),
                "status": case.status,
                "status_label": case.get_status_display(),
                "performed_at": case.performed_at,
                "created_at": case.created_at,
            }
            for case in encounter.ct_cases.all()
        ]
