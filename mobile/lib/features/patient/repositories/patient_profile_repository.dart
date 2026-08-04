import 'package:brainon_mobile/shared/models/patient_profile.dart';

abstract interface class PatientProfileRepository {
  /// 현재 로그인한 환자의 프로필을 조회합니다.
  ///
  /// 구현체는 데이터 출처와 관계없이 [PatientProfile]만 반환하며,
  /// 조회 실패 시 화면에서 처리할 수 있도록 예외를 전달해야 합니다.
  Future<PatientProfile> getMyProfile();
}
