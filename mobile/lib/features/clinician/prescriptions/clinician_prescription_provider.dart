import 'package:brainon_mobile/features/clinician/prescriptions/clinician_prescription_model.dart';
import 'package:brainon_mobile/features/clinician/prescriptions/clinician_prescription_repository.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianPrescriptionsProvider =
    FutureProvider<List<ClinicianPrescription>>(
      (ref) => ref.watch(clinicianPrescriptionRepositoryProvider).fetchAll(),
    );

final clinicianPrescriptionDetailProvider = FutureProvider.autoDispose
    .family<ClinicianPrescription, String>(
      (ref, id) =>
          ref.watch(clinicianPrescriptionRepositoryProvider).fetchDetail(id),
    );

final prescriptionContextsProvider =
    FutureProvider.autoDispose<List<PrescriptionContext>>(
      (ref) =>
          ref.watch(clinicianPrescriptionRepositoryProvider).fetchContexts(),
    );
