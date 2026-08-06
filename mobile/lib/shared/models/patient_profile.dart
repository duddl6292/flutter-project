class PatientProfile {
  const PatientProfile({
    required this.id,
    required this.username,
    this.userId,
    this.role,
    this.name,
    this.email,
    this.phone,
    this.patientNumber,
    this.birthDate,
    this.sex,
    this.emergencyContact,
    this.address,
    this.status,
  });

  /// 환자 프로필 UUID (`patient_id`).
  final String id;

  /// 환자 프로필에 연결된 로그인 계정 UUID (`user_id`).
  final String? userId;
  final String username;
  final String? role;

  final String? name;
  final String? email;
  final String? phone;
  final String? patientNumber;
  final DateTime? birthDate;
  final String? sex;
  final String? emergencyContact;
  final String? address;
  final String? status;

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
    final normalizedRole = role?.trim().toUpperCase();

    switch (normalizedRole) {
      case 'PATIENT':
        return '환자';
      case 'CLINICIAN':
        return '의료진';
      case 'ADMIN':
        return '관리자';
      default:
        return role?.trim() ?? '';
    }
  }

  factory PatientProfile.fromJson(Map<String, dynamic> json) {
    return PatientProfile(
      id: _parseString(json['patient_id'] ?? json['id']),
      userId: _parseNullableString(json['user_id']),
      username: _parseString(json['username']),
      role: _parseNullableString(json['role']),
      name: _parseNullableString(json['name'] ?? json['full_name']),
      email: _parseNullableString(json['email']),
      phone: _parseNullableString(json['phone'] ?? json['phone_number']),
      patientNumber: _parseNullableString(
        json['medical_record_number'] ??
            json['patient_number'] ??
            json['patient_no'],
      ),
      birthDate: _parseNullableDate(json['birth_date']),
      sex: _parseNullableString(json['sex']),
      emergencyContact: _parseNullableString(json['emergency_contact']),
      address: _parseNullableString(json['address']),
      status: _parseNullableString(json['status']),
    );
  }

  PatientProfile copyWith({
    String? userId,
    String? username,
    String? role,
    String? email,
  }) {
    return PatientProfile(
      id: id,
      userId: userId ?? this.userId,
      username: username ?? this.username,
      role: role ?? this.role,
      name: name,
      email: email ?? this.email,
      phone: phone,
      patientNumber: patientNumber,
      birthDate: birthDate,
      sex: sex,
      emergencyContact: emergencyContact,
      address: address,
      status: status,
    );
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

  static DateTime? _parseNullableDate(dynamic value) {
    final parsed = _parseNullableString(value);

    return parsed == null ? null : DateTime.tryParse(parsed);
  }
}
