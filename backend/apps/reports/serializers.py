from datetime import date

from rest_framework import serializers


class ClinicianReportQuerySerializer(
    serializers.Serializer
):
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, attrs):
        start_date: date = attrs["start_date"]
        end_date: date = attrs["end_date"]

        if end_date < start_date:
            raise serializers.ValidationError({
                "end_date": (
                    "종료일은 시작일보다 빠를 수 없습니다."
                ),
            })

        if (end_date - start_date).days > 366:
            raise serializers.ValidationError({
                "end_date": (
                    "조회 기간은 최대 1년까지 선택할 수 있습니다."
                ),
            })

        return attrs


class ClinicianReportDetailQuerySerializer(
    ClinicianReportQuerySerializer
):
    class DetailType:
        ENCOUNTERS = "encounters"
        APPOINTMENTS = "appointments"
        PRESCRIPTIONS = "prescriptions"
        CT_ANALYSES = "ct_analyses"

        choices = [
            (ENCOUNTERS, "진료"),
            (APPOINTMENTS, "예약"),
            (PRESCRIPTIONS, "처방"),
            (CT_ANALYSES, "CT 분석"),
        ]

    type = serializers.ChoiceField(
        choices=DetailType.choices,
    )
    status = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=32,
    )
    medicine = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
    )
