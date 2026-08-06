import 'package:brainon_mobile/features/patient/test_results/patient_test_result_model.dart';
import 'package:brainon_mobile/features/patient/test_results/patient_test_result_repository.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final patientTestResultsProvider = FutureProvider<List<PatientTestResult>>(
  (ref) => ref.watch(patientTestResultRepositoryProvider).fetchAll(),
);

final patientTestResultDetailProvider =
    FutureProvider.family<PatientTestResult, String>((ref, testResultId) {
      return ref
          .watch(patientTestResultRepositoryProvider)
          .fetchById(testResultId);
    });
