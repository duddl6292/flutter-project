import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/features/clinician/ai_analysis/clinician_ai_analysis_model.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:typed_data';

final clinicianAiAnalysisRepositoryProvider = Provider(
  (ref) => ClinicianAiAnalysisRepository(ref.watch(apiClientProvider)),
);

class ClinicianAiAnalysisRepository {
  const ClinicianAiAnalysisRepository(this._dio);
  final Dio _dio;

  Future<List<ClinicianAiAnalysis>> fetchAll() => runApiRequest(() async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/ct-analysis/cases/',
      queryParameters: {'limit': 50},
    );
    return (response.data?['data'] as List? ?? const [])
        .map(
          (item) => ClinicianAiAnalysis.fromJson(
            Map<String, dynamic>.from(item as Map),
          ),
        )
        .toList();
  });

  Future<ClinicianAiAnalysis> fetchDetail(String id) => runApiRequest(() async {
    final response = await _dio.get<Map<String, dynamic>>('/api/v1/ct-analysis/cases/$id/');
    return ClinicianAiAnalysis.fromJson(Map<String, dynamic>.from(response.data?['data'] as Map? ?? const {}));
  });

  Future<Uint8List?> fetchPreview(String id) async {
    try {
      final response = await _dio.get<List<int>>(
        '/api/v1/ct-analysis/cases/$id/preview/',
        options: Options(responseType: ResponseType.bytes),
      );
      return response.data == null ? null : Uint8List.fromList(response.data!);
    } on DioException {
      return null;
    }
  }

  Future<Uint8List> fetchVolume(String id, String asset) =>
      runApiRequest(() async {
        final response = await _dio.get<List<int>>(
          '/api/v1/ct-analysis/cases/$id/$asset/',
          options: Options(responseType: ResponseType.bytes),
        );
        return Uint8List.fromList(response.data ?? const []);
      });
}
