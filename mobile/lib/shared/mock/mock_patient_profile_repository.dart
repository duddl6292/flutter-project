import 'package:brainon_mobile/features/patient/repositories/patient_profile_repository.dart';
import 'package:brainon_mobile/shared/models/patient_profile.dart';

class MockPatientProfileRepository implements PatientProfileRepository {
  const MockPatientProfileRepository();

  @override
  Future<PatientProfile> getMyProfile() async {
    // 실제 API 통신처럼 잠깐 로딩 상태를 보여주기 위한 지연입니다.
    await Future<void>.delayed(const Duration(milliseconds: 400));

    return const PatientProfile(
      id: '1',
      username: 'patient01',
      role: 'PATIENT',
      name: '김지원',
      email: 'patient01@brainon.test',
      phone: '010-1234-5678',
      patientNumber: 'P-2026-0001',
    );
  }
}
