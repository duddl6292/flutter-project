enum UserRole {
  patient,
  clinician;

  String get apiValue {
    switch (this) {
      case UserRole.patient:
        return 'patient';
      case UserRole.clinician:
        return 'clinician';
    }
  }

  String get serverValue => name.toUpperCase();

  static UserRole fromApiValue(String value) {
    return switch (value.toUpperCase()) {
      'PATIENT' => UserRole.patient,
      'CLINICIAN' => UserRole.clinician,
      _ => throw FormatException('Unsupported user role: $value'),
    };
  }

  String get displayName {
    switch (this) {
      case UserRole.patient:
        return '환자';
      case UserRole.clinician:
        return '의료진';
    }
  }
}
