class ClinicianPatient {
  const ClinicianPatient({
    required this.id,
    required this.name,
    required this.registrationNumber,
    required this.phone,
    required this.sex,
    required this.birthDate,
    required this.status,
  });

  final String id;
  final String name;
  final String registrationNumber;
  final String phone;
  final String sex;
  final DateTime? birthDate;
  final String status;

  int? get age {
    final birth = birthDate;
    if (birth == null) return null;
    final today = DateTime.now();
    var value = today.year - birth.year;
    if (today.month < birth.month ||
        (today.month == birth.month && today.day < birth.day)) {
      value--;
    }
    return value;
  }

  factory ClinicianPatient.fromJson(Map<String, dynamic> json) {
    return ClinicianPatient(
      id: json['patient_id']?.toString() ?? '',
      name: json['name']?.toString() ?? '',
      registrationNumber: json['medical_record_number']?.toString() ?? '',
      phone: json['phone']?.toString() ?? '',
      sex: json['sex']?.toString() ?? '',
      birthDate: DateTime.tryParse(json['birth_date']?.toString() ?? ''),
      status: json['status']?.toString() ?? '',
    );
  }
}
