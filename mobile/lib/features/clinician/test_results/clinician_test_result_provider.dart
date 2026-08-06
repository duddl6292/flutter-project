import 'package:brainon_mobile/features/clinician/patients/clinician_patient_detail_model.dart';
import 'package:brainon_mobile/features/clinician/test_results/clinician_test_result_repository.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianTestResultsProvider = FutureProvider<List<ClinicianExamination>>(
  (ref) => ref.watch(clinicianTestResultRepositoryProvider).fetchAll(),
);
