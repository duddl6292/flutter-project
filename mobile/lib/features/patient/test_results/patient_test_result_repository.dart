import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/features/patient/test_results/patient_test_result_model.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final patientTestResultRepositoryProvider =
    Provider<PatientTestResultRepository>(
      (ref) => PatientTestResultRepository(ref.watch(apiClientProvider)),
    );

class PatientTestResultRepository {
  const PatientTestResultRepository(this._dio);

  final Dio _dio;

  Future<List<PatientTestResult>> fetchAll() {
    return runApiRequest(() async {
      final response = await _dio.get<Map<String, dynamic>>(
        '/api/v1/patients/me/test-results/',
        queryParameters: {'page_size': 100},
      );
      final rows = response.data?['data'] as List<dynamic>? ?? const [];
      return rows
          .map(
            (row) => PatientTestResult.fromJson(
              row as Map<String, dynamic>,
            ),
          )
          .toList();
    });
  }

  Future<PatientTestResult> fetchById(String testResultId) async {
    final results = await fetchAll();
    return results.firstWhere(
      (result) => result.id == testResultId,
      orElse: () => throw StateError('공개된 검사 결과를 찾을 수 없습니다.'),
    );
  }
}
