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
    final clinicians = <dynamic>[];
    var page = 1;
    while (true) {
      final response = await _dio.get<Map<String, dynamic>>(
        '/api/v1/clinicians/clinicians',
        queryParameters: {'hospital': hospitalId, 'page': page, 'page_size': 100},
      );
      final body = response.data ?? const {};
      clinicians.addAll(body['data'] as List<dynamic>? ?? const []);
      final meta = Map<String, dynamic>.from(body['meta'] as Map? ?? const {});
      final totalPages = int.tryParse(meta['total_pages']?.toString() ?? '') ?? 1;
      if (page >= totalPages) break;
      page++;
    }
    final departments = <String, Department>{};
    for (final raw in clinicians) {
      final clinician = Map<String, dynamic>.from(raw as Map);
      final department = Map<String, dynamic>.from(clinician['department'] as Map? ?? const {});
      final parsed = Department.fromJson(department, hospitalId: hospitalId);
      departments[parsed.departmentId] = parsed;
    }
    return departments.values.toList()..sort((a, b) => a.departmentName.compareTo(b.departmentName));
  });
}
