import 'package:brainon_mobile/features/notifications/notification_model.dart';
import 'package:brainon_mobile/features/notifications/notification_provider.dart';
import 'package:brainon_mobile/features/notifications/notification_repository.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class NotificationScreen extends ConsumerStatefulWidget {
  const NotificationScreen({super.key});

  @override
  ConsumerState<NotificationScreen> createState() => _NotificationScreenState();
}

class _NotificationScreenState extends ConsumerState<NotificationScreen> {
  bool _unreadOnly = false;

  @override
  Widget build(BuildContext context) {
    final result = ref.watch(notificationsProvider(_unreadOnly));
    return Scaffold(
      appBar: AppBar(
        title: const Text('알림'),
        actions: [
          TextButton(
            onPressed: () async {
              await ref.read(notificationRepositoryProvider).markAllRead();
              _refresh();
            },
            child: const Text('모두 읽음'),
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: SegmentedButton<bool>(
              segments: const [
                ButtonSegment(value: false, label: Text('전체')),
                ButtonSegment(value: true, label: Text('안 읽음')),
              ],
              selected: {_unreadOnly},
              onSelectionChanged: (value) {
                setState(() => _unreadOnly = value.first);
              },
            ),
          ),
          Expanded(
            child: result.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => Center(
                child: FilledButton.icon(
                  onPressed: _refresh,
                  icon: const Icon(Icons.refresh),
                  label: const Text('알림 다시 불러오기'),
                ),
              ),
              data: (data) {
                if (data.items.isEmpty) {
                  return const Center(child: Text('표시할 알림이 없습니다.'));
                }
                return RefreshIndicator(
                  onRefresh: () async => _refresh(),
                  child: ListView.separated(
                    padding: const EdgeInsets.fromLTRB(16, 4, 16, 24),
                    itemCount: data.items.length,
                    separatorBuilder: (_, _) => const SizedBox(height: 8),
                    itemBuilder: (context, index) {
                      final item = data.items[index];
                      return Card(
                        color: item.isRead
                            ? Colors.white
                            : const Color(0xFFEAF2FA),
                        child: ListTile(
                          leading: CircleAvatar(
                            backgroundColor: _color(item.type).withAlpha(28),
                            child: Icon(
                              _icon(item.type),
                              color: _color(item.type),
                            ),
                          ),
                          title: Text(
                            item.title,
                            style: TextStyle(
                              fontWeight: item.isRead
                                  ? FontWeight.w600
                                  : FontWeight.w800,
                            ),
                          ),
                          subtitle: Padding(
                            padding: const EdgeInsets.only(top: 4),
                            child: Text(item.body),
                          ),
                          trailing: item.isRead
                              ? null
                              : const Icon(
                                  Icons.circle,
                                  size: 9,
                                  color: Color(0xFF2563EB),
                                ),
                          onTap: () => _open(item),
                        ),
                      );
                    },
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  void _refresh() {
    ref.invalidate(notificationsProvider);
    ref.invalidate(unreadNotificationCountProvider);
  }

  Future<void> _open(AppNotification item) async {
    if (!item.isRead) {
      await ref.read(notificationRepositoryProvider).markRead(item.id);
      _refresh();
    }
    if (!mounted) return;
    final path = item.data['path'] as String?;
    if (path != null && path.startsWith('/')) context.push(path);
  }

  IconData _icon(String type) => switch (type) {
    'APPOINTMENT' => Icons.calendar_month,
    'MEDICATION' => Icons.medication,
    'TEST_RESULT' => Icons.description,
    'CONSULTATION' => Icons.groups_2,
    'EMERGENCY' => Icons.emergency,
    'SYSTEM' => Icons.settings,
    _ => Icons.notifications,
  };

  Color _color(String type) => switch (type) {
    'EMERGENCY' => const Color(0xFFDC2626),
    'MEDICATION' => const Color(0xFF059669),
    'TEST_RESULT' => const Color(0xFF7C3AED),
    _ => const Color(0xFF2563EB),
  };
}
