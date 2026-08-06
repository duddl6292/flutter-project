import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/features/clinician/patients/clinician_patient_detail_model.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianTestResultRepositoryProvider =
    Provider<ClinicianTestResultRepository>(
      (ref) => ClinicianTestResultRepository(ref.watch(apiClientProvider)),
    );

class ClinicianTestResultRepository {
  const ClinicianTestResultRepository(this._dio);
  final Dio _dio;

  Future<List<ClinicianExamination>> fetchAll() {
    return runApiRequest(() async {
      final response = await _dio.get<Map<String, dynamic>>(
        '/api/v1/examinations/',
        queryParameters: {'page_size': 100},
      );
      final rows = response.data?['data'] as List<dynamic>? ?? const [];
      return rows
          .map(
            (row) => ClinicianExamination.fromJson(row as Map<String, dynamic>),
          )
          .toList();
    });
  }
}
