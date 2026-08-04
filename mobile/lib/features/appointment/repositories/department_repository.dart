import 'package:brainon_mobile/shared/mock/department_mock.dart';
import 'package:brainon_mobile/shared/models/department.dart';

class DepartmentRepository {
  Future<List<Department>> getDepartmentsByHospital(String hospitalId) async {
    await Future<void>.delayed(const Duration(milliseconds: 400));

    return departmentMock
        .where((json) => json['hospital_id']?.toString() == hospitalId)
        .map((json) => Department.fromJson(json))
        .toList();
  }
}
