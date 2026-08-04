
class PatientSignupRequest {
  final String username;
  final String password;
  final String email;
  final String firstName;
  final String lastName;
  final String medicalRecordNumber;
  final String patientName;
  final String birthDate;
  final String sex;
  final String phone;
  final String? emergencyContact;
  final String? address;

  const PatientSignupRequest({
    required this.username,
    required this.password,
    required this.email,
    required this.firstName,
    required this.lastName,
    required this.medicalRecordNumber,
    required this.patientName,
    required this.birthDate,
    required this.sex,
    required this.phone,
    this.emergencyContact,
    this.address,
  });

  Map<String, dynamic> toJson() {
    return {
      'username': username,
      'password': password,
      'email': email,
      'first_name': firstName,
      'last_name': lastName,
      'role': 'PATIENT',
      'medical_record_number': medicalRecordNumber,
      'patient_name': patientName,
      'birth_date': birthDate,
      'sex': sex,
      'phone': phone,
      'emergency_contact': _nullableText(emergencyContact),
      'address': _nullableText(address),
    };
  }

  static String? _nullableText(String? value) {
    final text = value?.trim() ?? '';

    return text.isEmpty ? null : text;
  }
}