import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/features/patient/repositories/api_patient_profile_repository.dart';
import 'package:brainon_mobile/features/patient/repositories/patient_profile_repository.dart';
import 'package:brainon_mobile/shared/mock/mock_patient_profile_repository.dart';
import 'package:brainon_mobile/shared/models/patient_profile.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final patientProfileRepositoryProvider = Provider<PatientProfileRepository>((
  ref,
) {
  if (kDebugMode) {
    return const MockPatientProfileRepository();
  }

  return ApiPatientProfileRepository(ref.watch(apiClientProvider));
});

final patientProfileProvider = FutureProvider.autoDispose<PatientProfile>((
  ref,
) async {
  final repository = ref.watch(patientProfileRepositoryProvider);

  return repository.getMyProfile();
});
