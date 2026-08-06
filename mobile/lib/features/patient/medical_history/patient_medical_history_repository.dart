import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/features/patient/medical_history/patient_medical_history_model.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final patientMedicalHistoryRepositoryProvider =
    Provider<PatientMedicalHistoryRepository>(
      (ref) => PatientMedicalHistoryRepository(ref.watch(apiClientProvider)),
    );

class PatientMedicalHistoryRepository {
  const PatientMedicalHistoryRepository(this._dio);

  final Dio _dio;

  Future<List<PatientMedicalHistory>> fetchAll() {
    return runApiRequest(() async {
      final response = await _dio.get<Map<String, dynamic>>(
        '/api/v1/patients/me/medical-history/',
        queryParameters: {'page_size': 100},
      );
      final rows = response.data?['data'] as List<dynamic>? ?? const [];
      return rows
          .map(
            (row) =>
                PatientMedicalHistory.fromJson(row as Map<String, dynamic>),
          )
          .toList();
    });
  }

  Future<PatientMedicalHistory> fetchById(String encounterId) async {
    final histories = await fetchAll();
    return histories.firstWhere(
      (history) => history.encounterId == encounterId,
      orElse: () => throw StateError('진료 내역을 찾을 수 없습니다.'),
    );
  }
}
