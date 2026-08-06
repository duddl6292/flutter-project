import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/features/patient/repositories/patient_profile_repository.dart';
import 'package:brainon_mobile/shared/models/patient_profile.dart';
import 'package:dio/dio.dart';

class ApiPatientProfileRepository implements PatientProfileRepository {
  ApiPatientProfileRepository(this._dio);

  final Dio _dio;

  @override
  Future<PatientProfile> getMyProfile() {
    return runApiRequest(() async {
      final response = await _dio.get<Map<String, dynamic>>(
        '/api/v1/patients/me/',
      );
      final responseData = response.data;
      final profileData = responseData?['data'];

      if (profileData is! Map<String, dynamic>) {
        throw const FormatException('환자 프로필 응답 형식이 올바르지 않습니다.');
      }

      return PatientProfile.fromJson(profileData);
    });
  }
}
