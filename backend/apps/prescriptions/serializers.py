from django.db import transaction
from rest_framework import serializers

from apps.clinical_records.models import ClinicalRecord

from .models import Prescription, PrescriptionItem


class PrescriptionItemSerializer(
    serializers.ModelSerializer
):
    prescription_item_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )

    class Meta:
        model = PrescriptionItem
        fields = [
            "prescription_item_id",
            "medicine_name",
            "dosage",
            "dose_unit",
            "frequency",
            "route",
            "instructions",
            "start_date",
            "end_date",
        ]


class ClinicianPrescriptionSerializer(
    serializers.ModelSerializer
):
    prescription_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )
    status_label = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    encounter_id = serializers.UUIDField(
        source="encounter.id",
        read_only=True,
    )
    encounter_number = serializers.CharField(
        source="encounter.encounter_number",
        read_only=True,
    )
    clinical_record_id = serializers.UUIDField(
        source="clinical_record.id",
        read_only=True,
    )
    patient_id = serializers.UUIDField(
        source="encounter.patient.id",
        read_only=True,
    )
    patient_number = serializers.CharField(
        source=(
            "encounter.patient."
            "medical_record_number"
        ),
        read_only=True,
        allow_null=True,
    )
    patient_name = serializers.CharField(
        source="encounter.patient.name",
        read_only=True,
    )
    clinician_name = serializers.CharField(
        source="clinician.name",
        read_only=True,
    )
    items = PrescriptionItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Prescription
        fields = [
            "prescription_id",
            "encounter_id",
            "encounter_number",
            "clinical_record_id",
            "patient_id",
            "patient_number",
            "patient_name",
            "clinician_name",
            "status",
            "status_label",
            "notes",
            "prescribed_at",
            "discontinued_at",
            "items",
            "created_at",
            "updated_at",
        ]


class PrescriptionItemInputSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = PrescriptionItem
        fields = [
            "medicine_name",
            "dosage",
            "dose_unit",
            "frequency",
            "route",
            "instructions",
            "start_date",
            "end_date",
        ]

    def validate(self, attrs):
        start_date = attrs["start_date"]
        end_date = attrs.get("end_date")

        if (
            end_date is not None
            and end_date < start_date
        ):
            raise serializers.ValidationError({
                "end_date": (
                    "복용 종료일은 시작일보다 빠를 수 없습니다."
                ),
            })

        return attrs


class ClinicianPrescriptionCreateSerializer(
    serializers.Serializer
):
    clinical_record_id = serializers.UUIDField()
    status = serializers.ChoiceField(
        choices=[
            Prescription.Status.DRAFT,
            Prescription.Status.ACTIVE,
        ],
        default=Prescription.Status.ACTIVE,
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    items = PrescriptionItemInputSerializer(
        many=True,
        allow_empty=False,
    )

    def validate_clinical_record_id(self, value):
        clinician = self.context["request"].user.clinician

        try:
            record = (
                ClinicalRecord.objects
                .select_related(
                    "encounter",
                    "encounter__patient",
                )
                .get(
                    id=value,
                    clinician=clinician,
                    encounter__patient__isnull=False,
                )
            )
        except ClinicalRecord.DoesNotExist as exc:
            raise serializers.ValidationError(
                "처방 가능한 진료기록을 찾을 수 없습니다."
            ) from exc

        self.context["clinical_record"] = record
        return value

    @transaction.atomic
    def create(self, validated_data):
        clinician = self.context["request"].user.clinician
        clinical_record = self.context["clinical_record"]
        items_data = validated_data.pop("items")
        validated_data.pop("clinical_record_id")

        prescription = Prescription.objects.create(
            encounter=clinical_record.encounter,
            clinical_record=clinical_record,
            clinician=clinician,
            **validated_data,
        )

        for item_data in items_data:
            PrescriptionItem.objects.create(
                prescription=prescription,
                **item_data,
            )

        return prescription


class PrescriptionStatusUpdateSerializer(
    serializers.Serializer
):
    status = serializers.ChoiceField(
        choices=Prescription.Status.choices,
    )

