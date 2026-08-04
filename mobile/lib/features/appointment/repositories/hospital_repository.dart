import 'package:brainon_mobile/shared/mock/hospital_mock.dart';
import 'package:brainon_mobile/shared/models/hospital.dart';

class HospitalRepository {
  Future<List<Hospital>> getHospitals() async {
    await Future<void>.delayed(
      const Duration(milliseconds: 400),
    );

    return hospitalMockList
        .map(
          (json) => Hospital.fromJson(json),
        )
        .toList();
  }
}