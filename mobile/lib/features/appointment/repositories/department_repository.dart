import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/shared/models/department.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final departmentRepositoryProvider = Provider(
  (ref) => DepartmentRepository(ref.watch(apiClientProvider)),
);

class DepartmentRepository {
  const DepartmentRepository(this._dio);
  final Dio _dio;
  Future<List<Department>> getDepartmentsByHospital(String hospitalId) => runApiRequest(() async {
    final response = await _dio.get<Map<String, dynamic>>('/api/v1/clinicians/departments', queryParameters: {'page_size': 100});
    final rows = response.data?['data'] as List<dynamic>? ?? const [];
    return rows.map((row) => Department.fromJson(row as Map<String, dynamic>, hospitalId: hospitalId)).toList();
  });
}
