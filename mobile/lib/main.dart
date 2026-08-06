import 'package:brainon_mobile/app/app.dart';
import 'package:brainon_mobile/core/notifications/fcm_service.dart';
import 'package:brainon_mobile/firebase_options.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
  FirebaseMessaging.onBackgroundMessage(firebaseMessagingBackgroundHandler);
  await initializeNotifications();
  runApp(const ProviderScope(child: BrainOnApp()));
}
