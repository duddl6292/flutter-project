import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/features/clinician/prescriptions/clinician_prescription_model.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianPrescriptionRepositoryProvider = Provider(
  (ref) => ClinicianPrescriptionRepository(ref.watch(apiClientProvider)),
);

class ClinicianPrescriptionRepository {
  const ClinicianPrescriptionRepository(this._dio);
  final Dio _dio;

  Future<List<ClinicianPrescription>> fetchAll() => runApiRequest(() async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/prescriptions/',
      queryParameters: {'page_size': 100},
    );
    final rows = response.data?['data'] as List<dynamic>? ?? const [];
    return rows
        .map(
          (row) => ClinicianPrescription.fromJson(row as Map<String, dynamic>),
        )
        .toList();
  });

  Future<ClinicianPrescription> fetchDetail(String id) =>
      runApiRequest(() async {
        final response = await _dio.get<Map<String, dynamic>>(
          '/api/v1/prescriptions/$id/',
        );
        return ClinicianPrescription.fromJson(
          response.data?['data'] as Map<String, dynamic>? ?? const {},
        );
      });

  Future<List<PrescriptionContext>> fetchContexts() => runApiRequest(() async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/prescriptions/contexts/',
    );
    final rows = response.data?['data'] as List<dynamic>? ?? const [];
    return rows
        .map((row) => PrescriptionContext.fromJson(row as Map<String, dynamic>))
        .toList();
  });

  Future<ClinicianPrescription> create(PrescriptionCreateInput input) =>
      runApiRequest(() async {
        final response = await _dio.post<Map<String, dynamic>>(
          '/api/v1/prescriptions/',
          data: input.toJson(),
        );
        return ClinicianPrescription.fromJson(
          response.data?['data'] as Map<String, dynamic>? ?? const {},
        );
      });
}
