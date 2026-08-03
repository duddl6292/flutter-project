from datetime import (
    datetime,
    time,
    timedelta,
)

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.patients.permissions import (
    IsClinicianOrAdmin,
)

from .models import Appointment
from .serializers import (
    AppointmentCreateSerializer,
    AppointmentSummarySerializer,
)


class AppointmentListCreateView(APIView):
    permission_classes = [
        IsClinicianOrAdmin,
    ]

    def get(self, request):
        appointments = (
            Appointment.objects
            .select_related(
                "patient",
                "clinician",
                "department",
                "hospital",
            )
        )

        if request.user.role == "CLINICIAN":
            appointments = appointments.filter(
                clinician__user=request.user,
            )

        requested_status = (
            request.query_params
            .get("status", "")
            .strip()
            .upper()
        )

        valid_statuses = {
            value
            for value, _label
            in Appointment.Status.choices
        }

        if requested_status in valid_statuses:
            appointments = appointments.filter(
                status=requested_status,
            )

        date_from = (
            request.query_params
            .get("date_from")
        )

        date_to = (
            request.query_params
            .get("date_to")
        )

        current_timezone = (
            timezone.get_current_timezone()
        )

        if date_from:
            start_date = datetime.strptime(
                date_from,
                "%Y-%m-%d",
            ).date()

            start_at = timezone.make_aware(
                datetime.combine(
                    start_date,
                    time.min,
                ),
                current_timezone,
            )

            appointments = appointments.filter(
                scheduled_at__gte=start_at,
            )

        if date_to:
            end_date = datetime.strptime(
                date_to,
                "%Y-%m-%d",
            ).date()

            end_at = timezone.make_aware(
                datetime.combine(
                    end_date
                    + timedelta(days=1),
                    time.min,
                ),
                current_timezone,
            )

            appointments = appointments.filter(
                scheduled_at__lt=end_at,
            )

        appointments = appointments.order_by(
            "scheduled_at",
        )

        serializer = AppointmentSummarySerializer(
            appointments,
            many=True,
        )

        return Response({
            "data": serializer.data,
            "meta": {
                "total_count":
                    appointments.count(),
            },
        })

    @transaction.atomic
    def post(self, request):
        serializer = AppointmentCreateSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True,
        )

        appointment = serializer.save()

        response_serializer = (
            AppointmentSummarySerializer(
                appointment,
            )
        )

        return Response(
            {
                "data":
                    response_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )