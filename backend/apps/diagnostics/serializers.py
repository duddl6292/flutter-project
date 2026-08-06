from django.utils import timezone
from rest_framework import serializers

from apps.appointments.models import Encounter

from .models import (
    DiagnosticReport,
    DiagnosticReportAsset,
    Examination,
    ExaminationCatalog,
    ExaminationObservation,
)


class ExaminationObservationSerializer(
    serializers.ModelSerializer
):
    observation_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )
    interpretation_label = serializers.CharField(
        source="get_interpretation_display",
        read_only=True,
    )
    formatted_value = serializers.SerializerMethodField()

    class Meta:
        model = ExaminationObservation
        fields = [
            "observation_id",
            "code",
            "name",
            "sequence",
            "value_type",
            "numeric_value",
            "text_value",
            "coded_value",
            "boolean_value",
            "formatted_value",
            "unit",
            "reference_low",
            "reference_high",
            "reference_text",
            "interpretation",
            "interpretation_label",
        ]

    def get_formatted_value(self, observation):
        value_mapping = {
            ExaminationObservation.ValueType.NUMERIC: (
                observation.numeric_value
            ),
            ExaminationObservation.ValueType.TEXT: (
                observation.text_value
            ),
            ExaminationObservation.ValueType.CODED: (
                observation.coded_value
            ),
            ExaminationObservation.ValueType.BOOLEAN: (
                observation.boolean_value
            ),
        }
        value = value_mapping.get(
            observation.value_type
        )
        if value is None:
            return "-"
        if isinstance(value, bool):
            return "예" if value else "아니요"
        return str(value)


class DiagnosticReportAssetSerializer(
    serializers.ModelSerializer
):
    asset_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )
    stored_object_id = serializers.UUIDField(
        read_only=True,
    )
    asset_type_label = serializers.CharField(
        source="get_asset_type_display",
        read_only=True,
    )

    class Meta:
        model = DiagnosticReportAsset
        fields = [
            "asset_id",
            "stored_object_id",
            "asset_type",
            "asset_type_label",
            "display_name",
            "created_at",
        ]


class DiagnosticReportSerializer(
    serializers.ModelSerializer
):
    report_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )
    status_label = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    author_name = serializers.CharField(
        source="author.name",
        read_only=True,
    )
    assets = DiagnosticReportAssetSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = DiagnosticReport
        fields = [
            "report_id",
            "revision_number",
            "author_name",
            "status",
            "status_label",
            "title",
            "summary",
            "conclusion",
            "issued_at",
            "signed_at",
            "is_released_to_patient",
            "released_at",
            "assets",
            "created_at",
            "updated_at",
        ]


class ExaminationSerializer(serializers.ModelSerializer):
    examination_id = serializers.UUIDField(
        source="id",
        read_only=True,
    )
    status_label = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    category_label = serializers.CharField(
        source="get_category_display",
        read_only=True,
    )
    source_label = serializers.CharField(
        source="get_source_display",
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
    patient_birth_date = serializers.DateField(
        source="patient.birth_date",
        read_only=True,
        allow_null=True,
    )
    patient_sex = serializers.CharField(
        source="patient.sex",
        read_only=True,
    )
    encounter_id = serializers.UUIDField(
        source="encounter.id",
        read_only=True,
        allow_null=True,
    )
    encounter_number = serializers.CharField(
        source="encounter.encounter_number",
        read_only=True,
        allow_null=True,
    )
    hospital_name = serializers.CharField(
        source="hospital.name",
        read_only=True,
    )
    ordered_by_name = serializers.CharField(
        source="ordered_by.name",
        read_only=True,
        allow_null=True,
    )
    observations = ExaminationObservationSerializer(
        many=True,
        read_only=True,
    )
    report = serializers.SerializerMethodField()
    overall_interpretation = serializers.SerializerMethodField()
    overall_interpretation_label = serializers.SerializerMethodField()
    abnormal_count = serializers.SerializerMethodField()

    class Meta:
        model = Examination
        fields = [
            "examination_id",
            "patient_id",
            "patient_number",
            "patient_name",
            "patient_birth_date",
            "patient_sex",
            "encounter_id",
            "encounter_number",
            "hospital_name",
            "ordered_by_name",
            "test_code",
            "test_name",
            "category",
            "category_label",
            "accession_number",
            "status",
            "status_label",
            "source",
            "source_label",
            "performed_at",
            "result_available_at",
            "overall_interpretation",
            "overall_interpretation_label",
            "abnormal_count",
            "observations",
            "report",
            "created_at",
            "updated_at",
        ]

    def get_report(self, examination):
        report = examination.reports.first()
        if report is None:
            return None
        return DiagnosticReportSerializer(report).data

    def get_overall_interpretation(self, examination):
        interpretations = {
            item.interpretation
            for item in examination.observations.all()
        }
        for value in (
            ExaminationObservation.Interpretation.CRITICAL,
            ExaminationObservation.Interpretation.ABNORMAL,
            ExaminationObservation.Interpretation.HIGH,
            ExaminationObservation.Interpretation.LOW,
            ExaminationObservation.Interpretation.NORMAL,
        ):
            if value in interpretations:
                return value
        return ExaminationObservation.Interpretation.UNKNOWN

    def get_overall_interpretation_label(
        self,
        examination,
    ):
        value = self.get_overall_interpretation(
            examination
        )
        return dict(
            ExaminationObservation.Interpretation.choices
        )[value]

    def get_abnormal_count(self, examination):
        abnormal_values = {
            ExaminationObservation.Interpretation.LOW,
            ExaminationObservation.Interpretation.HIGH,
            ExaminationObservation.Interpretation.ABNORMAL,
            ExaminationObservation.Interpretation.CRITICAL,
        }
        return sum(
            1
            for item in examination.observations.all()
            if item.interpretation in abnormal_values
        )


class ExaminationObservationInputSerializer(
    serializers.Serializer
):
    code = serializers.CharField(max_length=64)
    name = serializers.CharField(max_length=200)
    value_type = serializers.ChoiceField(
        choices=ExaminationObservation.ValueType.choices,
    )
    numeric_value = serializers.DecimalField(
        max_digits=20,
        decimal_places=8,
        required=False,
        allow_null=True,
    )
    text_value = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    coded_value = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    boolean_value = serializers.BooleanField(
        required=False,
        allow_null=True,
    )
    unit = serializers.CharField(
        max_length=40,
        required=False,
        allow_blank=True,
    )
    reference_low = serializers.DecimalField(
        max_digits=20,
        decimal_places=8,
        required=False,
        allow_null=True,
    )
    reference_high = serializers.DecimalField(
        max_digits=20,
        decimal_places=8,
        required=False,
        allow_null=True,
    )
    reference_text = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
    )
    interpretation = serializers.ChoiceField(
        choices=(
            ExaminationObservation.Interpretation.choices
        ),
        default=(
            ExaminationObservation.Interpretation.UNKNOWN
        ),
    )

    def validate(self, attrs):
        value_type = attrs["value_type"]
        value_fields = {
            ExaminationObservation.ValueType.NUMERIC: (
                attrs.get("numeric_value") is not None
            ),
            ExaminationObservation.ValueType.TEXT: bool(
                attrs.get("text_value", "").strip()
            ),
            ExaminationObservation.ValueType.CODED: bool(
                attrs.get("coded_value", "").strip()
            ),
            ExaminationObservation.ValueType.BOOLEAN: (
                attrs.get("boolean_value") is not None
            ),
        }
        if not value_fields.get(value_type, False):
            raise serializers.ValidationError(
                "결과 유형에 맞는 값을 입력해주세요."
            )
        if (
            attrs.get("reference_low") is not None
            and attrs.get("reference_high") is not None
            and attrs["reference_high"]
            < attrs["reference_low"]
        ):
            raise serializers.ValidationError({
                "reference_high": (
                    "참고 상한은 하한보다 "
                    "작을 수 없습니다."
                ),
            })
        return attrs


class ExaminationCreateSerializer(serializers.Serializer):
    encounter_id = serializers.UUIDField()
    test_code = serializers.CharField(max_length=64)
    test_name = serializers.CharField(max_length=200)
    category = serializers.ChoiceField(
        choices=ExaminationCatalog.Category.choices,
    )
    source = serializers.ChoiceField(
        choices=Examination.Source.choices,
        default=Examination.Source.INTERNAL,
    )
    performed_at = serializers.DateTimeField()
    observations = ExaminationObservationInputSerializer(
        many=True,
        allow_empty=False,
    )
    report_title = serializers.CharField(max_length=200)
    report_summary = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    report_conclusion = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    def validate_encounter_id(self, value):
        clinician = self.context["request"].user.clinician
        try:
            encounter = (
                Encounter.objects
                .select_related("patient", "hospital")
                .get(
                    id=value,
                    attending_clinician=clinician,
                    patient__isnull=False,
                    hospital__isnull=False,
                )
            )
        except Encounter.DoesNotExist as exc:
            raise serializers.ValidationError(
                "검사 결과를 작성할 수 있는 "
                "진료 건을 찾을 수 없습니다."
            ) from exc
        self.context["encounter"] = encounter
        return value

    def validate_performed_at(self, value):
        if value > timezone.now():
            raise serializers.ValidationError(
                "검사 시행일은 현재보다 이후일 수 없습니다."
            )
        return value


class DiagnosticReportFinalizeSerializer(
    serializers.Serializer
):
    summary = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    conclusion = serializers.CharField()

    def validate_conclusion(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "최종 결론을 입력해주세요."
            )
        return value
