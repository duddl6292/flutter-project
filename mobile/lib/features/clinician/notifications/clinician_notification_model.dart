enum ClinicianNotificationType { consultation, testResult, schedule, system }

class ClinicianNotification {
  const ClinicianNotification({
    required this.id,
    required this.type,
    required this.title,
    required this.message,
    required this.createdAt,
    required this.isRead,
  });
  final String id, title, message;
  final ClinicianNotificationType type;
  final DateTime? createdAt;
  final bool isRead;
  factory ClinicianNotification.fromJson(Map<String, dynamic> json) =>
      ClinicianNotification(
        id: json['id']?.toString() ?? '',
        type: switch (json['type']) {
          'consultation' => ClinicianNotificationType.consultation,
          'test_result' => ClinicianNotificationType.testResult,
          'schedule' => ClinicianNotificationType.schedule,
          _ => ClinicianNotificationType.system,
        },
        title: json['title']?.toString() ?? '',
        message: json['message']?.toString() ?? '',
        createdAt: DateTime.tryParse(json['created_at']?.toString() ?? ''),
        isRead: json['is_read'] == true,
      );
}
