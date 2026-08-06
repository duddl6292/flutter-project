import 'package:brainon_mobile/features/clinician/patients/clinician_patient_model.dart';
import 'package:brainon_mobile/features/clinician/patients/clinician_patient_repository.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianPatientsProvider = FutureProvider<List<ClinicianPatient>>((ref) {
  return ref.watch(clinicianPatientRepositoryProvider).fetchRecentPatients();
});
