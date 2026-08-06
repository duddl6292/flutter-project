import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/core/auth/auth_provider.dart';
import 'package:brainon_mobile/core/auth/auth_state.dart';
import 'package:brainon_mobile/features/patient/repositories/api_patient_profile_repository.dart';
import 'package:brainon_mobile/features/patient/repositories/patient_profile_repository.dart';
import 'package:brainon_mobile/shared/models/patient_profile.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final patientProfileRepositoryProvider = Provider<PatientProfileRepository>((
  ref,
) {
  return ApiPatientProfileRepository(ref.watch(apiClientProvider));
});

final patientProfileProvider = FutureProvider.autoDispose<PatientProfile>((
  ref,
) async {
  final authState = ref.watch(authProvider);
  final authUser = authState.user;

  if (authState.status != AuthStatus.authenticated || authUser == null) {
    throw StateError('로그인한 환자 정보를 확인할 수 없습니다.');
  }

  final repository = ref.watch(patientProfileRepositoryProvider);
  final profile = await repository.getMyProfile();

  return profile.copyWith(
    userId: profile.userId ?? authUser.id,
    username: profile.username.isEmpty ? authUser.username : profile.username,
    role: profile.role ?? authUser.role.serverValue,
    email: profile.email ?? (authUser.email.isEmpty ? null : authUser.email),
  );
});
