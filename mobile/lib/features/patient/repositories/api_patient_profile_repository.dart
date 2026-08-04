import 'package:brainon_mobile/features/patient/repositories/patient_profile_repository.dart';
import 'package:brainon_mobile/shared/models/patient_profile.dart';
import 'package:dio/dio.dart';

class ApiPatientProfileRepository implements PatientProfileRepository {
  ApiPatientProfileRepository(this._dio);

  // 공통 API 클라이언트를 주입받아 인증 및 토큰 갱신 흐름을 재사용합니다.
  // ignore: unused_field
  final Dio _dio;

  @override
  Future<PatientProfile> getMyProfile() async {
    // TODO: 백엔드의 환자 프로필 조회 엔드포인트와 응답 JSON 필드가
    // 확정되면 공통 Dio 인스턴스인 _dio로 요청하고 PatientProfile로 변환합니다.
    throw UnsupportedError(
      '환자 프로필 조회 API가 아직 확정되지 않았습니다. '
      '엔드포인트와 응답 명세를 확인한 뒤 연동해야 합니다.',
    );
  }
}
