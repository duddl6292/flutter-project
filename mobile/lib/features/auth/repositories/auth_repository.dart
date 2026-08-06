import 'package:brainon_mobile/shared/models/patient_signup_request.dart';

class AuthRepository {
  Future<void> signupPatient(PatientSignupRequest request) async {
    // 화면 동작 확인용 임시 처리
    await Future<void>.delayed(const Duration(milliseconds: 700));

    // TODO: Django API 확정 후 실제 POST 요청 연결
  }
}
