import 'package:brainon_mobile/features/patient/medical_history/patient_medical_history_model.dart';
import 'package:brainon_mobile/features/patient/medical_history/patient_medical_history_repository.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final patientMedicalHistoriesProvider =
    FutureProvider<List<PatientMedicalHistory>>(
      (ref) => ref.watch(patientMedicalHistoryRepositoryProvider).fetchAll(),
    );

final patientMedicalHistoryDetailProvider =
    FutureProvider.family<PatientMedicalHistory, String>((ref, encounterId) {
      return ref
          .watch(patientMedicalHistoryRepositoryProvider)
          .fetchById(encounterId);
    });
