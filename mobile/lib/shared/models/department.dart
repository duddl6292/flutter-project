class Department {
  final String departmentId;
  final String departmentName;
  final String hospitalId;

  const Department({
    required this.departmentId,
    required this.departmentName,
    required this.hospitalId,
  });

  factory Department.fromJson(
    Map<String, dynamic> json,
  ) {
    return Department(
      departmentId:
          json['department_id']?.toString() ?? '',
      departmentName:
          json['department_name']?.toString() ?? '',
      hospitalId:
          json['hospital_id']?.toString() ?? '',
    );
  }
}