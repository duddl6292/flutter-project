enum ClinicianScheduleStatus { inProgress, waiting, confirmed, completed }

class ClinicianSchedule {
  const ClinicianSchedule({
    required this.id,
    required this.patientId,
    required this.startsAt,
    required this.patientName,
    required this.description,
    required this.status,
  });
  final String id, patientId, patientName, description;
  final DateTime startsAt;
  final ClinicianScheduleStatus status;

  factory ClinicianSchedule.fromJson(Map<String, dynamic> json) =>
      ClinicianSchedule(
        id: json['appointment_id']?.toString() ?? '',
        patientId: json['patient_id']?.toString() ?? '',
        startsAt:
            DateTime.tryParse(
              json['scheduled_at']?.toString() ?? '',
            )?.toLocal() ??
            DateTime.fromMillisecondsSinceEpoch(0),
        patientName: json['patient_name']?.toString() ?? '',
        description: json['reason']?.toString() ?? '',
        status: switch (json['status']?.toString()) {
          'COMPLETED' => ClinicianScheduleStatus.completed,
          'CONFIRMED' => ClinicianScheduleStatus.confirmed,
          'IN_PROGRESS' => ClinicianScheduleStatus.inProgress,
          _ => ClinicianScheduleStatus.waiting,
        },
      );
}
