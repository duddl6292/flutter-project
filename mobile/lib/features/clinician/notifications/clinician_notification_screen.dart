import 'package:brainon_mobile/features/clinician/notifications/clinician_notification_provider.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_detail_scaffold.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ClinicianNotificationScreen extends ConsumerStatefulWidget {
  const ClinicianNotificationScreen({super.key});
  @override
  ConsumerState<ClinicianNotificationScreen> createState() =>
      _NotificationState();
}

class _NotificationState extends ConsumerState<ClinicianNotificationScreen> {
  bool unreadOnly = true;
  @override
  Widget build(BuildContext context) {
    final data = ref.watch(clinicianNotificationsProvider);
    return ClinicianDetailScaffold(
      title: '알림센터',
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: SegmentedButton<bool>(
              segments: const [
                ButtonSegment(value: true, label: Text('읽지 않음')),
                ButtonSegment(value: false, label: Text('전체')),
              ],
              selected: {unreadOnly},
              onSelectionChanged: (value) =>
                  setState(() => unreadOnly = value.first),
            ),
          ),
          Expanded(
            child: data.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (_, _) => Center(
                child: FilledButton(
                  onPressed: () =>
                      ref.invalidate(clinicianNotificationsProvider),
                  child: const Text('다시 시도'),
                ),
              ),
              data: (items) {
                final list = unreadOnly
                    ? items.where((item) => !item.isRead).toList()
                    : items;
                if (list.isEmpty) return const Center(child: Text('알림이 없습니다.'));
                return ListView(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  children: list
                      .map(
                        (item) => Card(
                          elevation: 0,
                          color: item.isRead
                              ? Colors.white
                              : const Color(0xFFEAF2FA),
                          child: ListTile(
                            leading: Icon(
                              item.type.name == 'consultation'
                                  ? Icons.groups_2_outlined
                                  : Icons.notifications_outlined,
                            ),
                            title: Text(
                              item.title,
                              style: const TextStyle(
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                            subtitle: Text(item.message),
                          ),
                        ),
                      )
                      .toList(),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
