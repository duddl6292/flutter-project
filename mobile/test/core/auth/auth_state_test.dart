import 'package:brainon_mobile/core/auth/auth_state.dart';
import 'package:brainon_mobile/features/auth/user_role.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('initial auth state is unauthenticated', () {
    const state = AuthState();

    expect(state.status, AuthStatus.unauthenticated);
    expect(state.user, isNull);
  });

  test('parses UUID user id and clinician role from the backend response', () {
    final user = AuthUser.fromJson(
      {
        'id': '57ca748d-4af7-45f0-81e8-48366349bd32',
        'username': 'doctor',
        'email': 'doctor@example.com',
        'role': 'CLINICIAN',
      },
      clinician: {
        'id': 'a1e88630-08af-4380-aa44-df17a5aa6606',
        'name': 'Doctor Kim',
        'license_number': '123456',
        'approval_status': 'APPROVED',
        'hospital_id': 'c762363f-d79c-469b-aebb-fcce9c461f01',
        'hospital_name': 'BrainOn Hospital',
        'department_id': 'b7b3a548-dfb8-4ad3-a5e3-bd329f6177c0',
        'department_code': 'D',
        'department_name': 'Neurology',
      },
    );

    expect(user.id, '57ca748d-4af7-45f0-81e8-48366349bd32');
    expect(user.role, UserRole.clinician);
    expect(user.clinician?.departmentCode, 'D');
  });
}
