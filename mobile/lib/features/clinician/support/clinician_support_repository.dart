import 'package:brainon_mobile/features/clinician/support/clinician_support_model.dart';
import 'package:brainon_mobile/shared/mock/clinician_support_mock.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianSupportRepositoryProvider = Provider(
  (ref) => const ClinicianSupportRepository(),
);

class ClinicianSupportRepository {
  const ClinicianSupportRepository();
  Future<List<ClinicianSupportFaq>> fetchFaqs() async {
    return clinicianSupportMock.map(ClinicianSupportFaq.fromJson).toList();
  }
}
