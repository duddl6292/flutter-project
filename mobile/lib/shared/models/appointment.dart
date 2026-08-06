class Appointment {
  final String appointmentId;
  final DateTime scheduledAt;
  final String type;
  final String hospitalName;
  final String department;
  final String doctorName;
  final String location;
  final String dDay;
  final String status;

  const Appointment({
    required this.appointmentId,
    required this.scheduledAt,
    required this.type,
    required this.hospitalName,
    required this.department,
    required this.doctorName,
    required this.location,
    required this.dDay,
    required this.status,
  });

  factory Appointment.fromJson(Map<String, dynamic> json) {
    return Appointment(
      appointmentId: json['appointment_id']?.toString() ?? '',
      scheduledAt: DateTime.parse(
        json['scheduled_at']?.toString() ?? '',
      ).toLocal(),
      type: json['reason']?.toString() ?? '',
      hospitalName: json['hospital_name']?.toString() ?? '',
      department: json['department_name']?.toString() ?? '',
      doctorName: json['clinician_name']?.toString() ?? '',
      location: json['location']?.toString() ?? '',
      dDay: _dDay(DateTime.parse(json['scheduled_at']?.toString() ?? '').toLocal()),
      status: json['status_label']?.toString() ?? json['status']?.toString() ?? '',
    );
  }

  static String _dDay(DateTime date) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final target = DateTime(date.year, date.month, date.day);
    final days = target.difference(today).inDays;
    if (days == 0) {
      return 'D-Day';
    }
    return days > 0 ? 'D-$days' : 'D+${days.abs()}';
  }
}
