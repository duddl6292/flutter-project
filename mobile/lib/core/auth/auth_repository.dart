import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/core/auth/auth_state.dart';
import 'package:brainon_mobile/core/storage/token_storage.dart';
import 'package:brainon_mobile/features/auth/user_role.dart';
import 'package:brainon_mobile/shared/mock/auth_login_options_mock.dart';
import 'package:brainon_mobile/shared/models/patient_signup_request.dart';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

class AuthRepository {
  AuthRepository(this._dio, this._tokenStorage);

  final Dio _dio;
  final TokenStorage _tokenStorage;

  Future<List<AuthHospital>> getHospitals() async {
    try {
      final hospitals = await runApiRequest(() async {
        final response = await _dio.get<Map<String, dynamic>>(
          '/api/v1/hospitals/',
          queryParameters: {'page_size': 100},
        );
        final data = response.data!['data'] as List<dynamic>;
        return data
            .map((item) => AuthHospital.fromJson(item as Map<String, dynamic>))
            .toList();
      });
      if (hospitals.isNotEmpty || !kDebugMode) {
        return hospitals;
      }
    } on Object {
      if (!kDebugMode) {
        rethrow;
      }
    }
    return authHospitalMockData.map(AuthHospital.fromJson).toList();
  }

  Future<List<AuthDepartment>> getDepartments() async {
    try {
      final departments = await runApiRequest(() async {
        final response = await _dio.get<Map<String, dynamic>>(
          '/api/v1/clinicians/departments',
          queryParameters: {'page_size': 100},
        );
        final data = response.data!['data'] as List<dynamic>;
        return data
            .map(
              (item) => AuthDepartment.fromJson(item as Map<String, dynamic>),
            )
            .toList();
      });
      if (departments.isNotEmpty || !kDebugMode) {
        return departments;
      }
    } on Object {
      if (!kDebugMode) {
        rethrow;
      }
    }
    return authDepartmentMockData.map(AuthDepartment.fromJson).toList();
  }

  Future<void> signupPatient(PatientSignupRequest request) {
    return runApiRequest(() async {
      await _dio.post<Map<String, dynamic>>(
        '/api/v1/auth/patient/signup/',
        data: request.toJson(),
      );
    });
  }

  Future<AuthUser> login({
    required UserRole role,
    required String password,
    String? username,
    String? hospitalId,
    String? departmentCode,
    String? licenseNumber,
  }) {
    return runApiRequest(() async {
      final path = switch (role) {
        UserRole.patient => '/api/v1/auth/patient/login/',
        UserRole.clinician => '/api/v1/auth/clinician/login/',
      };
      final requestData = switch (role) {
        UserRole.patient => {'username': username, 'password': password},
        UserRole.clinician => {
          'hospital_id': hospitalId,
          'department_code': departmentCode,
          'license_number': licenseNumber,
          'password': password,
        },
      };
      final response = await _dio.post<Map<String, dynamic>>(
        path,
        data: requestData,
      );
      final data = response.data!['data'] as Map<String, dynamic>;
      await _tokenStorage.writeTokens(
        accessToken: data['access'] as String,
        refreshToken: data['refresh'] as String,
      );
      return AuthUser.fromJson(
        data['user'] as Map<String, dynamic>,
        clinician: data['clinician'] as Map<String, dynamic>?,
      );
    });
  }

  Future<AuthUser> me() {
    return runApiRequest(() async {
      final response = await _dio.get<Map<String, dynamic>>('/api/v1/auth/me/');
      final data = response.data!['data'] as Map<String, dynamic>;
      return AuthUser.fromJson(
        data['user'] as Map<String, dynamic>,
        clinician: data['clinician'] as Map<String, dynamic>?,
      );
    });
  }

  Future<AuthUser> updateEmail(String email) {
    return runApiRequest(() async {
      final response = await _dio.patch<Map<String, dynamic>>(
        '/api/v1/auth/me/',
        data: {'email': email},
      );
      final data = response.data!['data'] as Map<String, dynamic>;
      return AuthUser.fromJson(
        data['user'] as Map<String, dynamic>,
        clinician: data['clinician'] as Map<String, dynamic>?,
      );
    });
  }

  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
    required String newPasswordConfirm,
  }) {
    return runApiRequest(() async {
      await _dio.post<Map<String, dynamic>>(
        '/api/v1/auth/password/change/',
        data: {
          'current_password': currentPassword,
          'new_password': newPassword,
          'new_password_confirm': newPasswordConfirm,
        },
      );
    });
  }

  Future<bool> hasStoredTokens() async {
    final access = await _tokenStorage.readAccessToken();
    final refresh = await _tokenStorage.readRefreshToken();
    return access?.isNotEmpty == true || refresh?.isNotEmpty == true;
  }

  Future<void> logout() async {
    await _tokenStorage.clear();
  }
}
