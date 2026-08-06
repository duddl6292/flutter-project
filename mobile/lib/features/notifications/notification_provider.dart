import 'package:brainon_mobile/features/notifications/notification_model.dart';
import 'package:brainon_mobile/features/notifications/notification_repository.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final notificationsProvider = FutureProvider.autoDispose
    .family<({List<AppNotification> items, int unreadCount}), bool>((
      ref,
      unreadOnly,
    ) {
      return ref
          .watch(notificationRepositoryProvider)
          .list(unreadOnly: unreadOnly);
    });

final unreadNotificationCountProvider = FutureProvider<int>((ref) async {
  final result = await ref.watch(notificationRepositoryProvider).list();
  return result.unreadCount;
});

final notificationSettingsProvider =
    FutureProvider.autoDispose<NotificationSettings>((ref) {
      return ref.watch(notificationRepositoryProvider).getSettings();
    });
