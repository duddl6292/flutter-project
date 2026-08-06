import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/shared/models/appointment.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final appointmentRepositoryProvider = Provider(
  (ref) => AppointmentRepository(ref.watch(apiClientProvider)),
);

class AppointmentRepository {
  const AppointmentRepository(this._dio);
  final Dio _dio;

  Future<List<Appointment>> getAppointments() => runApiRequest(() async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/patients/me/appointments/',
      queryParameters: {'page_size': 100},
    );
    final rows = response.data?['data'] as List<dynamic>? ?? const [];
    return rows
        .map((row) => Appointment.fromJson(row as Map<String, dynamic>))
        .toList();
  });
}
