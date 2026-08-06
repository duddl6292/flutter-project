import 'dart:convert';

import 'package:brainon_mobile/core/auth/auth_provider.dart';
import 'package:brainon_mobile/features/auth/user_role.dart';
import 'package:brainon_mobile/features/notifications/notification_provider.dart';
import 'package:brainon_mobile/features/notifications/notification_repository.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

const _channel = AndroidNotificationChannel(
  'brainon_high_v2',
  'BrainOn 주요 알림',
  description: '예약, 복약, 검사 결과, 협진 및 응급 알림',
  importance: Importance.max,
);

final _localNotifications = FlutterLocalNotificationsPlugin();
void Function(String path)? notificationPathHandler;

@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {}

Future<void> initializeNotifications() async {
  const settings = InitializationSettings(
    android: AndroidInitializationSettings('@mipmap/ic_launcher'),
  );
  await _localNotifications.initialize(
    settings: settings,
    onDidReceiveNotificationResponse: (response) {
      final payload = response.payload;
      if (payload != null && payload.isNotEmpty) {
        notificationPathHandler?.call(payload);
      }
    },
  );
  await _localNotifications
      .resolvePlatformSpecificImplementation<
        AndroidFlutterLocalNotificationsPlugin
      >()
      ?.createNotificationChannel(_channel);
  await FirebaseMessaging.instance.requestPermission(
    alert: true,
    badge: true,
    sound: true,
  );
  FirebaseMessaging.onMessage.listen((message) async {
    final notification = message.notification;
    final type = message.data['type'] as String? ?? 'OTHER';
    await _localNotifications.show(
      id: message.messageId?.hashCode ?? DateTime.now().millisecondsSinceEpoch,
      title: notification?.title ?? message.data['title'] ?? 'BrainOn',
      body: notification?.body ?? message.data['body'] ?? '',
      notificationDetails: NotificationDetails(
        android: AndroidNotificationDetails(
          _channel.id,
          _channel.name,
          channelDescription: _channel.description,
          importance: type == 'EMERGENCY' ? Importance.max : Importance.high,
          priority: type == 'EMERGENCY' ? Priority.max : Priority.high,
          category: type == 'MEDICATION'
              ? AndroidNotificationCategory.reminder
              : AndroidNotificationCategory.message,
        ),
      ),
      payload: message.data['path'] as String?,
    );
  });
  FirebaseMessaging.onMessageOpenedApp.listen((message) {
    final path = message.data['path'] as String?;
    if (path != null) notificationPathHandler?.call(path);
  });
  final initial = await FirebaseMessaging.instance.getInitialMessage();
  final initialPath = initial?.data['path'] as String?;
  if (initialPath != null) {
    Future<void>.delayed(
      const Duration(milliseconds: 500),
      () => notificationPathHandler?.call(initialPath),
    );
  }
}

final fcmRegistrationProvider = FutureProvider<void>((ref) async {
  final user = ref.watch(authProvider).user;
  if (user == null) return;
  const storage = FlutterSecureStorage();
  var identifier = await storage.read(key: 'brainon_device_identifier');
  if (identifier == null) {
    identifier = base64Url.encode(
      utf8.encode('${user.id}:${DateTime.now().microsecondsSinceEpoch}'),
    );
    await storage.write(key: 'brainon_device_identifier', value: identifier);
  }
  final token = await FirebaseMessaging.instance.getToken();
  if (token == null) return;
  await ref
      .read(notificationRepositoryProvider)
      .registerDevice(
        token: token,
        identifier: identifier,
        clientType: user.role == UserRole.clinician
            ? 'CLINICIAN_APP'
            : 'PATIENT_APP',
      );
  final subscription = FirebaseMessaging.instance.onTokenRefresh.listen((
    nextToken,
  ) {
    ref
        .read(notificationRepositoryProvider)
        .registerDevice(
          token: nextToken,
          identifier: identifier!,
          clientType: user.role == UserRole.clinician
              ? 'CLINICIAN_APP'
              : 'PATIENT_APP',
        );
  });
  ref.onDispose(subscription.cancel);
  ref.invalidate(unreadNotificationCountProvider);
});
