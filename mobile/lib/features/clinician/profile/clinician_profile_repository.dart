import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/features/clinician/profile/clinician_notification_settings_model.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianProfileRepositoryProvider = Provider(
  (ref) => ClinicianProfileRepository(ref.watch(apiClientProvider)),
);

class ClinicianProfileRepository {
  const ClinicianProfileRepository(this._dio);

  final Dio _dio;

  Future<ClinicianNotificationSettings> fetchNotificationSettings() {
    return runApiRequest(() async {
      final response = await _dio.get<Map<String, dynamic>>(
        '/api/v1/notifications/settings/',
      );
      return ClinicianNotificationSettings.fromJson(
        response.data?['data'] as Map<String, dynamic>? ?? const {},
      );
    });
  }

  Future<ClinicianNotificationSettings> updateNotificationSettings(
    ClinicianNotificationSettings settings,
  ) {
    return runApiRequest(() async {
      final response = await _dio.patch<Map<String, dynamic>>(
        '/api/v1/notifications/settings/',
        data: settings.toJson(),
      );
      return ClinicianNotificationSettings.fromJson(
        response.data?['data'] as Map<String, dynamic>? ?? const {},
      );
    });
  }
}
