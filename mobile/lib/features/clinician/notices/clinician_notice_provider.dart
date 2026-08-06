import 'package:brainon_mobile/features/clinician/notices/clinician_notice_model.dart';
import 'package:brainon_mobile/features/clinician/notices/clinician_notice_repository.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianNoticesProvider = FutureProvider<List<ClinicianNotice>>(
  (ref) => ref.watch(clinicianNoticeRepositoryProvider).fetchAll(),
);
