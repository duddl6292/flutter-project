import 'package:brainon_mobile/shared/mock/medication_mock.dart';
import 'package:brainon_mobile/shared/models/medication.dart';

class MedicationRepository {
  Future<List<Medication>> getMedications() async {
    await Future<void>.delayed(
      const Duration(milliseconds: 500),
    );

    return medicationMock
        .map(
          (json) => Medication.fromJson(json),
        )
        .toList();
  }
}