import 'package:brainon_mobile/shared/mock/doctor_mock.dart';
import 'package:brainon_mobile/shared/models/doctor.dart';

class DoctorRepository {
  Future<List<Doctor>> getDoctorsByDepartment(String departmentId) async {
    await Future<void>.delayed(const Duration(milliseconds: 300));

    return doctorMock
        .where((json) => json['department_id']?.toString() == departmentId)
        .map((json) => Doctor.fromJson(json))
        .toList();
  }
}
