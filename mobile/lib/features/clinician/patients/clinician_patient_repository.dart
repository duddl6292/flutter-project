import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/features/clinician/patients/clinician_patient_model.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianPatientRepositoryProvider = Provider<ClinicianPatientRepository>(
  (ref) => ClinicianPatientRepository(ref.watch(apiClientProvider)),
);

class ClinicianPatientRepository {
  const ClinicianPatientRepository(this._dio);

  final Dio _dio;

  Future<List<ClinicianPatient>> fetchRecentPatients() {
    return runApiRequest(() async {
      final response = await _dio.get<Map<String, dynamic>>(
        '/api/v1/patients/',
        queryParameters: {'page_size': 100},
      );
      final rows = response.data?['data'] as List<dynamic>? ?? const [];
      return rows
          .map((row) => ClinicianPatient.fromJson(row as Map<String, dynamic>))
          .toList();
    });
  }
}
