import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/features/clinician/consultations/clinician_consultation_model.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianConsultationRepositoryProvider = Provider(
  (ref) => ClinicianConsultationRepository(ref.watch(apiClientProvider)),
);

class ClinicianConsultationRepository {
  const ClinicianConsultationRepository(this._dio);
  final Dio _dio;
  Future<List<ClinicianConsultation>> fetchConsultations(String box) =>
      runApiRequest(() async {
        final response = await _dio.get<Map<String, dynamic>>(
          '/api/v1/consultations/',
          queryParameters: {'box': box, 'page_size': 100},
        );
        return _rows(
          response.data,
        ).map(ClinicianConsultation.fromJson).toList();
      });
  Future<ClinicianConsultation> fetchDetail(String id) =>
      _command('GET', '/api/v1/consultations/$id/');
  Future<List<ConsultationContext>> fetchContexts() => runApiRequest(() async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/consultations/contexts/',
    );
    return _rows(response.data).map(ConsultationContext.fromJson).toList();
  });
  Future<List<ConsultationClinician>> fetchClinicians() => runApiRequest(
    () async {
      final response = await _dio.get<Map<String, dynamic>>(
        '/api/v1/clinicians/clinicians',
        queryParameters: {'page_size': 100},
      );
      return _rows(response.data).map(ConsultationClinician.fromJson).toList();
    },
  );
  Future<ClinicianConsultation> create(ConsultationCreateInput input) =>
      _command('POST', '/api/v1/consultations/', data: input.toJson());
  Future<ClinicianConsultation> accept(String id) =>
      _command('POST', '/api/v1/consultations/$id/accept/', data: const {});
  Future<ClinicianConsultation> complete(String id, String response) =>
      _command(
        'POST',
        '/api/v1/consultations/$id/complete/',
        data: {'response': response},
      );
  Future<ClinicianConsultation> cancel(String id, String reason) => _command(
    'POST',
    '/api/v1/consultations/$id/cancel/',
    data: {'reason': reason},
  );
  Future<void> sendMessage(String id, String content) =>
      runApiRequest(() async {
        await _dio.post<void>(
          '/api/v1/consultations/$id/messages/',
          data: {'content': content},
        );
      });
  Future<ClinicianConsultation> _command(
    String method,
    String path, {
    Object? data,
  }) => runApiRequest(() async {
    final response = await _dio.request<Map<String, dynamic>>(
      path,
      data: data,
      options: Options(method: method),
    );
    return ClinicianConsultation.fromJson(
      response.data?['data'] as Map<String, dynamic>? ?? const {},
    );
  });
  List<Map<String, dynamic>> _rows(Map<String, dynamic>? body) =>
      (body?['data'] as List<dynamic>? ?? const [])
          .cast<Map<String, dynamic>>();
}
