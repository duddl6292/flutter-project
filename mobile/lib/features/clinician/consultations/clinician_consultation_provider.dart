import 'package:brainon_mobile/features/clinician/consultations/clinician_consultation_model.dart';
import 'package:brainon_mobile/features/clinician/consultations/clinician_consultation_repository.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianConsultationsProvider =
    FutureProvider.family<List<ClinicianConsultation>, String>(
      (ref, box) => ref
          .watch(clinicianConsultationRepositoryProvider)
          .fetchConsultations(box),
    );
final clinicianConsultationDetailProvider = FutureProvider.autoDispose
    .family<ClinicianConsultation, String>(
      (ref, id) =>
          ref.watch(clinicianConsultationRepositoryProvider).fetchDetail(id),
    );
final consultationContextsProvider =
    FutureProvider.autoDispose<List<ConsultationContext>>(
      (ref) =>
          ref.watch(clinicianConsultationRepositoryProvider).fetchContexts(),
    );
final consultationCliniciansProvider =
    FutureProvider.autoDispose<List<ConsultationClinician>>(
      (ref) =>
          ref.watch(clinicianConsultationRepositoryProvider).fetchClinicians(),
    );
