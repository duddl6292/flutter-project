class Doctor {
  final String doctorId;
  final String doctorName;
  final String departmentId;
  final String departmentName;

  const Doctor({
    required this.doctorId,
    required this.doctorName,
    required this.departmentId,
    required this.departmentName,
  });

  factory Doctor.fromJson(Map<String, dynamic> json) {
    return Doctor(
      doctorId: json['doctor_id']?.toString() ?? json['clinician_id']?.toString() ?? '',
      doctorName: json['doctor_name']?.toString() ?? json['name']?.toString() ?? '',
      departmentId: json['department_id']?.toString() ?? (json['department'] as Map<String, dynamic>?)?['department_id']?.toString() ?? '',
      departmentName: json['department_name']?.toString() ?? (json['department'] as Map<String, dynamic>?)?['name']?.toString() ?? '',
    );
  }
}
