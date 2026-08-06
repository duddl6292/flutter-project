import 'package:brainon_mobile/features/clinician/clinical_records/clinician_record_model.dart';
import 'package:brainon_mobile/shared/mock/clinician_record_mock.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianRecordRepositoryProvider = Provider(
  (ref) => const ClinicianRecordRepository(),
);

class ClinicianRecordRepository {
  const ClinicianRecordRepository(); // TODO(API): GET /api/v1/clinicians/clinical-records/
  Future<List<ClinicianRecord>> fetchAll() async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    return clinicianRecordMock.map(ClinicianRecord.fromJson).toList();
  }

  Future<void> save(ClinicianRecordInput input) async {
    await Future<void>.delayed(const Duration(milliseconds: 350));
    input.toJson();
    // TODO(API): PUT /api/v1/encounters/{encounter_id}/clinical-record/
  }
}
