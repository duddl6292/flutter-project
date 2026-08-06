import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/features/notifications/notification_model.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final notificationRepositoryProvider = Provider<NotificationRepository>((ref) {
  return NotificationRepository(ref.watch(apiClientProvider));
});

class NotificationRepository {
  const NotificationRepository(this._dio);

  final Dio _dio;

  Future<({List<AppNotification> items, int unreadCount})> list({
    bool unreadOnly = false,
  }) async {
    return runApiRequest(() async {
      final response = await _dio.get<Map<String, dynamic>>(
        '/api/v1/notifications/',
        queryParameters: {'unread_only': unreadOnly},
      );
      final root = response.data ?? const {};
      final data = root['data'] as List? ?? const [];
      final meta = Map<String, dynamic>.from(root['meta'] as Map? ?? const {});
      return (
        items: data
            .map(
              (item) => AppNotification.fromJson(
                Map<String, dynamic>.from(item as Map),
              ),
            )
            .toList(),
        unreadCount: meta['unread_count'] as int? ?? 0,
      );
    });
  }

  Future<void> markRead(String id) => runApiRequest(() async {
    await _dio.patch<void>('/api/v1/notifications/$id/read/');
  });

  Future<void> markAllRead() => runApiRequest(() async {
    await _dio.post<void>('/api/v1/notifications/read-all/');
  });

  Future<NotificationSettings> getSettings() => runApiRequest(() async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/notifications/settings/',
    );
    return NotificationSettings.fromJson(
      Map<String, dynamic>.from(response.data?['data'] as Map),
    );
  });

  Future<NotificationSettings> updateSettings({
    required List<NotificationPreference> preferences,
    required bool quietHoursEnabled,
    String? quietHoursStart,
    String? quietHoursEnd,
  }) => runApiRequest(() async {
    final response = await _dio.patch<Map<String, dynamic>>(
      '/api/v1/notifications/settings/',
      data: {
        'global_setting': {
          'quiet_hours_enabled': quietHoursEnabled,
          'quiet_hours_start': quietHoursStart,
          'quiet_hours_end': quietHoursEnd,
        },
        'preferences': preferences.map((item) => item.toJson()).toList(),
      },
    );
    return NotificationSettings.fromJson(
      Map<String, dynamic>.from(response.data?['data'] as Map),
    );
  });

  Future<void> registerDevice({
    required String token,
    required String identifier,
    required String clientType,
  }) => runApiRequest(() async {
    await _dio.post<void>(
      '/api/v1/notifications/devices/register/',
      data: {
        'platform': 'ANDROID',
        'client_type': clientType,
        'device_identifier': identifier,
        'fcm_token': token,
        'device_name': 'BrainOn Android',
        'app_version': '1.0.0',
      },
    );
  });
}
