import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/features/clinician/appointments/clinician_schedule_model.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianScheduleRepositoryProvider =
    Provider<ClinicianScheduleRepository>(
      (ref) => ClinicianScheduleRepository(ref.watch(apiClientProvider)),
    );

class ClinicianScheduleRepository {
  const ClinicianScheduleRepository(this._dio);
  final Dio _dio;
  Future<List<ClinicianSchedule>> fetchSchedules() => runApiRequest(() async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/appointments/',
    );
    final rows = response.data?['data'] as List<dynamic>? ?? const [];
    return rows
        .map((row) => ClinicianSchedule.fromJson(row as Map<String, dynamic>))
        .where((item) => item.patientId.isNotEmpty)
        .toList();
  });
}
