import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/shared/models/department.dart';
import 'package:brainon_mobile/shared/models/doctor.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final doctorRepositoryProvider = Provider(
  (ref) => DoctorRepository(ref.watch(apiClientProvider)),
);

class DoctorRepository {
  const DoctorRepository(this._dio);
  final Dio _dio;
  Future<List<Doctor>> getDoctorsByDepartment(Department department) => runApiRequest(() async {
    final response = await _dio.get<Map<String, dynamic>>('/api/v1/clinicians/clinicians', queryParameters: {'hospital': department.hospitalId, 'department': department.departmentCode, 'page_size': 100});
    final rows = response.data?['data'] as List<dynamic>? ?? const [];
    return rows.map((row) => Doctor.fromJson(row as Map<String, dynamic>)).toList();
  });
}
