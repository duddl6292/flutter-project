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

  String get displayName {
    switch (this) {
      case UserRole.patient:
        return '환자';
      case UserRole.clinician:
        return '의료진';
    }
  }
}
