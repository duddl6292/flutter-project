import 'package:brainon_mobile/features/patient/prescriptions/patient_prescription_model.dart';
import 'package:brainon_mobile/features/patient/prescriptions/patient_prescription_repository.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final patientPrescriptionsProvider =
    FutureProvider<List<PatientPrescription>>(
      (ref) => ref.watch(patientPrescriptionRepositoryProvider).fetchAll(),
    );
