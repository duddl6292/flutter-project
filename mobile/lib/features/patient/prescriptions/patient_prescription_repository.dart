import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/features/patient/prescriptions/patient_prescription_model.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final patientPrescriptionRepositoryProvider =
    Provider<PatientPrescriptionRepository>(
      (ref) => PatientPrescriptionRepository(ref.watch(apiClientProvider)),
    );

class PatientPrescriptionRepository {
  const PatientPrescriptionRepository(this._dio);

  final Dio _dio;

  Future<List<PatientPrescription>> fetchAll() {
    return runApiRequest(() async {
      final rows = <dynamic>[];
      var page = 1;
      while (true) {
        final response = await _dio.get<Map<String, dynamic>>(
          '/api/v1/patients/me/prescriptions/',
          queryParameters: {'page': page, 'page_size': 100},
        );
        final body = response.data ?? const {};
        rows.addAll(body['data'] as List<dynamic>? ?? const []);
        final meta = Map<String, dynamic>.from(
          body['meta'] as Map? ?? const {},
        );
        final totalPages =
            int.tryParse(meta['total_pages']?.toString() ?? '') ?? 1;
        if (page >= totalPages) break;
        page++;
      }
      return rows
          .map(
            (row) =>
                PatientPrescription.fromJson(row as Map<String, dynamic>),
          )
          .toList();
    });
  }
}
