class AppointmentCreateRequest {
  final String hospitalId;
  final String departmentId;
  final String doctorId;
  final DateTime scheduledAt;

  const AppointmentCreateRequest({
    required this.hospitalId,
    required this.departmentId,
    required this.doctorId,
    required this.scheduledAt,
  });

  Map<String, dynamic> toJson() {
    return {
      'hospital_id': hospitalId,
      'department_id': departmentId,
      'doctor_id': doctorId,
      'scheduled_at': scheduledAt.toIso8601String(),
    };
  }
}
