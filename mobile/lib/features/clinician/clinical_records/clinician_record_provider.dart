import 'package:brainon_mobile/features/clinician/clinical_records/clinician_record_model.dart';
import 'package:brainon_mobile/features/clinician/clinical_records/clinician_record_repository.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianRecordsProvider = FutureProvider<List<ClinicianRecord>>(
  (ref) => ref.watch(clinicianRecordRepositoryProvider).fetchAll(),
);
