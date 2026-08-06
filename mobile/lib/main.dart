import 'package:brainon_mobile/app/app.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'firebase_options.dart';

const bool uiPreviewMode = false; //ui만 확인할때

const notificationChannel = AndroidNotificationChannel(
  'brainon_high_v1',
  'BrainOn 알림',
  description: 'BrainOn의 주요 알림입니다.',
  importance: Importance.max,
);

final localNotifications = FlutterLocalNotificationsPlugin();

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // UI 확인 모드면 Firebase 설정을 건너뛰고 바로 앱 실행
  if (uiPreviewMode) {
    runApp(const ProviderScope(child: BrainOnApp()));
    return;
  }

  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);

  // 로컬 알림 초기화
  const initializationSettings = InitializationSettings(
    android: AndroidInitializationSettings('@mipmap/ic_launcher'),
  );

  await localNotifications.initialize(settings: initializationSettings);

  // 중요도가 높은 Android 알림 채널 생성
  await localNotifications
      .resolvePlatformSpecificImplementation<
        AndroidFlutterLocalNotificationsPlugin
      >()
      ?.createNotificationChannel(notificationChannel);

  // Android 13 이상 알림 권한 요청
  final permission = await FirebaseMessaging.instance.requestPermission(
    alert: true,
    badge: true,
    sound: true,
  );

  debugPrint('FCM permission: ${permission.authorizationStatus}');

  final token = await FirebaseMessaging.instance.getToken();
  debugPrint('FCM token: $token');

  // 앱이 화면에 열려 있을 때 시스템 알림 직접 표시
  FirebaseMessaging.onMessage.listen((message) async {
    final notification = message.notification;

    debugPrint('Foreground FCM: ${message.messageId}');
    debugPrint('Title: ${notification?.title}');
    debugPrint('Body: ${notification?.body}');

    if (notification == null) {
      return;
    }

    await localNotifications.show(
      id: message.messageId?.hashCode ?? DateTime.now().millisecondsSinceEpoch,
      title: notification.title ?? 'BrainOn',
      body: notification.body ?? '',
      notificationDetails: const NotificationDetails(
        android: AndroidNotificationDetails(
          'brainon_high_v1',
          'BrainOn 알림',
          channelDescription: 'BrainOn의 주요 알림입니다.',
          importance: Importance.max,
          priority: Priority.high,
          playSound: true,
        ),
      ),
    );
  });

  // 백그라운드 상태에서 알림을 눌러 앱을 연 경우
  FirebaseMessaging.onMessageOpenedApp.listen((message) {
    debugPrint('Notification opened: ${message.data}');
  });

  // 종료된 상태에서 알림을 눌러 앱을 연 경우
  final initialMessage = await FirebaseMessaging.instance.getInitialMessage();

  if (initialMessage != null) {
    debugPrint(
      'Notification opened from terminated state: '
      '${initialMessage.data}',
    );
  }

  runApp(const ProviderScope(child: BrainOnApp()));
}
