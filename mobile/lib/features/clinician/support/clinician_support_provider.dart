import 'package:brainon_mobile/features/clinician/support/clinician_support_model.dart';
import 'package:brainon_mobile/features/clinician/support/clinician_support_repository.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianSupportProvider = FutureProvider<List<ClinicianSupportFaq>>(
  (ref) => ref.watch(clinicianSupportRepositoryProvider).fetchFaqs(),
);
