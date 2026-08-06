import 'package:brainon_mobile/features/auth/user_role.dart';

enum AuthStatus { restoring, unauthenticated, authenticating, authenticated }

class AuthHospital {
  const AuthHospital({required this.id, required this.name});

  final String id;
  final String name;

  factory AuthHospital.fromJson(Map<String, dynamic> json) {
    return AuthHospital(
      id: json['hospital_id'] as String,
      name: json['hospital_name'] as String,
    );
  }
}

class AuthDepartment {
  const AuthDepartment({required this.code, required this.name});

  final String code;
  final String name;

  factory AuthDepartment.fromJson(Map<String, dynamic> json) {
    return AuthDepartment(
      code: json['code'] as String,
      name: json['name'] as String,
    );
  }
}

class AuthClinician {
  const AuthClinician({
    required this.id,
    required this.name,
    required this.licenseNumber,
    required this.approvalStatus,
    required this.hospitalId,
    required this.hospitalName,
    required this.departmentId,
    required this.departmentCode,
    required this.departmentName,
  });

  final String id;
  final String name;
  final String licenseNumber;
  final String approvalStatus;
  final String hospitalId;
  final String hospitalName;
  final String departmentId;
  final String departmentCode;
  final String departmentName;

  factory AuthClinician.fromJson(Map<String, dynamic> json) {
    return AuthClinician(
      id: json['id'] as String,
      name: json['name'] as String,
      licenseNumber: json['license_number'] as String,
      approvalStatus: json['approval_status'] as String,
      hospitalId: json['hospital_id'] as String,
      hospitalName: json['hospital_name'] as String,
      departmentId: json['department_id'] as String,
      departmentCode: json['department_code'] as String,
      departmentName: json['department_name'] as String,
    );
  }
}

class AuthUser {
  const AuthUser({
    required this.id,
    required this.username,
    required this.role,
    this.email = '',
    this.clinician,
  });

  final String id;
  final String username;
  final UserRole role;
  final String email;
  final AuthClinician? clinician;

  factory AuthUser.fromJson(
    Map<String, dynamic> json, {
    Map<String, dynamic>? clinician,
  }) {
    return AuthUser(
      id: json['id'] as String,
      username: json['username'] as String,
      role: UserRole.fromApiValue(json['role'] as String),
      email: json['email'] as String? ?? '',
      clinician: clinician == null ? null : AuthClinician.fromJson(clinician),
    );
  }
}

class AuthState {
  const AuthState({this.status = AuthStatus.unauthenticated, this.user});

  final AuthStatus status;
  final AuthUser? user;
}
