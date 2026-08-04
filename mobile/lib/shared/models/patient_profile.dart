class PatientProfile {
  const PatientProfile({
    required this.id,
    required this.username,
    required this.role,
    this.name,
    this.email,
    this.phone,
    this.patientNumber,
  });

  final int id;
  final String username;
  final String role;

  final String? name;
  final String? email;
  final String? phone;
  final String? patientNumber;

  /// 화면에서 표시할 사용자 이름
  ///
  /// 백엔드에서 name이 내려오지 않으면 username을 대신 표시합니다.
  String get displayName {
    final trimmedName = name?.trim();

    if (trimmedName != null && trimmedName.isNotEmpty) {
      return trimmedName;
    }

    return username;
  }

  /// 화면에서 표시할 역할
  String get displayRole {
    switch (role.toUpperCase()) {
      case 'PATIENT':
        return '환자';
      case 'CLINICIAN':
        return '의료진';
      case 'ADMIN':
        return '관리자';
      default:
        return role;
    }
  }

  factory PatientProfile.fromJson(Map<String, dynamic> json) {
    return PatientProfile(
      id: _parseInt(json['id']),
      username: _parseString(json['username']),
      role: _parseString(json['role']),
      name: _parseNullableString(json['name'] ?? json['full_name']),
      email: _parseNullableString(json['email']),
      phone: _parseNullableString(json['phone'] ?? json['phone_number']),
      patientNumber: _parseNullableString(
        json['patient_number'] ?? json['patient_no'],
      ),
    );
  }

  static int _parseInt(dynamic value) {
    if (value is int) {
      return value;
    }

    return int.tryParse(value?.toString() ?? '') ?? 0;
  }

  static String _parseString(dynamic value) {
    return value?.toString() ?? '';
  }

  static String? _parseNullableString(dynamic value) {
    final parsed = value?.toString().trim();

    if (parsed == null || parsed.isEmpty) {
      return null;
    }

    return parsed;
  }
}
