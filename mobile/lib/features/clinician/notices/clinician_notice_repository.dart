import 'package:brainon_mobile/features/clinician/notices/clinician_notice_model.dart';
import 'package:brainon_mobile/shared/mock/clinician_notice_mock.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianNoticeRepositoryProvider = Provider(
  (ref) => const ClinicianNoticeRepository(),
);

class ClinicianNoticeRepository {
  const ClinicianNoticeRepository();
  Future<List<ClinicianNotice>> fetchAll() async {
    await Future<void>.delayed(const Duration(milliseconds: 200));
    return clinicianNoticeMock.map(ClinicianNotice.fromJson).toList();
  }
}
