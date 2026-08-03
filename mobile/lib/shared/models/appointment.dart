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
      ),
      type: json['type']?.toString() ?? '',
      hospitalName: json['hospital_name']?.toString() ?? '',
      department: json['department']?.toString() ?? '',
      doctorName: json['doctor_name']?.toString() ?? '',
      location: json['location']?.toString() ?? '',
      dDay: json['d_day']?.toString() ?? '',
      status: json['status']?.toString() ?? '',
    );
  }
}