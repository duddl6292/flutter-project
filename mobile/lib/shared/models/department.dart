class Department {
  final String departmentId;
  final String departmentName;
  final String hospitalId;
  final String departmentCode;

  const Department({
    required this.departmentId,
    required this.departmentName,
    required this.hospitalId,
    this.departmentCode = '',
  });

  factory Department.fromJson(Map<String, dynamic> json, {String hospitalId = ''}) {
    return Department(
      departmentId: json['department_id']?.toString() ?? '',
      departmentName: json['department_name']?.toString() ?? json['name']?.toString() ?? '',
      hospitalId: json['hospital_id']?.toString() ?? hospitalId,
      departmentCode: json['code']?.toString() ?? '',
    );
  }
}
