from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from apps.medications.models import MedicationSchedule
from apps.notifications.models import Notification
from apps.prescriptions.models import Prescription


class Command(BaseCommand):
    help = "현재 시각에 예정된 환자 복약 알림을 생성하고 FCM으로 발송합니다."

    def handle(self, *args, **options):
        now = timezone.localtime()
        today = now.date()
        window_start = (now - timedelta(minutes=5)).time().replace(second=0, microsecond=0)
        window_end = (now + timedelta(minutes=5)).time().replace(second=59, microsecond=999999)
        schedules = MedicationSchedule.objects.filter(
            is_active=True,
            dose_time__gte=window_start,
            dose_time__lte=window_end,
            start_date__lte=today,
            prescription_item__prescription__status=Prescription.Status.ACTIVE,
        ).filter(Q(end_date__isnull=True) | Q(end_date__gte=today))
        created = 0
        for schedule in schedules.select_related(
            "prescription_item__prescription__encounter__patient__user"
        ).distinct():
            if schedule.days_of_week and today.isoweekday() not in schedule.days_of_week:
                continue
            item = schedule.prescription_item
            user = item.prescription.encounter.patient.user
            if user is None:
                continue
            _, was_created = Notification.objects.get_or_create(
                recipient=user,
                deduplication_key=f"medication:{schedule.id}:{today.isoformat()}",
                defaults={
                    "type": Notification.Type.MEDICATION,
                    "title": "복약 시간입니다.",
                    "body": f"{item.medicine_name} {item.dosage}{item.dose_unit} 복용 시간을 확인해 주세요.",
                    "data": {
                        "schedule_id": str(schedule.id),
                        "path": "/patient",
                        "event": "MEDICATION_DUE",
                    },
                },
            )
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f"복약 알림 {created}건 생성"))
