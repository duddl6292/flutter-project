import 'package:brainon_mobile/features/notifications/notification_model.dart';
import 'package:brainon_mobile/features/notifications/notification_provider.dart';
import 'package:brainon_mobile/features/notifications/notification_repository.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class NotificationSettingsScreen extends ConsumerStatefulWidget {
  const NotificationSettingsScreen({super.key});

  @override
  ConsumerState<NotificationSettingsScreen> createState() =>
      _NotificationSettingsScreenState();
}

class _NotificationSettingsScreenState
    extends ConsumerState<NotificationSettingsScreen> {
  NotificationSettings? _draft;
  bool _saving = false;

  @override
  Widget build(BuildContext context) {
    final asyncSettings = ref.watch(notificationSettingsProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('푸시 알림 설정')),
      body: asyncSettings.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, _) => Center(
          child: FilledButton(
            onPressed: () => ref.invalidate(notificationSettingsProvider),
            child: const Text('다시 불러오기'),
          ),
        ),
        data: (settings) {
          _draft ??= settings;
          final draft = _draft!;
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              const Text(
                '알림 카테고리',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 8),
              ...draft.preferences.map(_preferenceTile),
              const SizedBox(height: 18),
              SwitchListTile(
                title: const Text('방해 금지 시간'),
                subtitle: Text(
                  draft.quietHoursEnabled
                      ? '${draft.quietHoursStart ?? '22:00'} ~ ${draft.quietHoursEnd ?? '07:00'}'
                      : '사용하지 않음',
                ),
                value: draft.quietHoursEnabled,
                onChanged: (value) => setState(() {
                  _draft = NotificationSettings(
                    preferences: draft.preferences,
                    quietHoursEnabled: value,
                    quietHoursStart: value
                        ? (draft.quietHoursStart ?? '22:00')
                        : null,
                    quietHoursEnd: value
                        ? (draft.quietHoursEnd ?? '07:00')
                        : null,
                  );
                }),
              ),
              if (draft.quietHoursEnabled)
                ListTile(
                  title: const Text('시간 변경'),
                  trailing: const Icon(Icons.schedule),
                  onTap: _selectQuietHours,
                ),
              const SizedBox(height: 24),
              FilledButton.icon(
                onPressed: _saving ? null : _save,
                icon: _saving
                    ? const SizedBox.square(
                        dimension: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.save),
                label: const Text('설정 저장'),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _preferenceTile(NotificationPreference preference) {
    return Card(
      child: Column(
        children: [
          ListTile(
            leading: Icon(_icon(preference.type)),
            title: Text(_label(preference.type)),
          ),
          SwitchListTile(
            title: const Text('푸시 알림'),
            value: preference.pushEnabled,
            onChanged: (value) =>
                _updatePreference(preference.copyWith(pushEnabled: value)),
          ),
          SwitchListTile(
            title: const Text('이메일 알림'),
            value: preference.emailEnabled,
            onChanged: (value) =>
                _updatePreference(preference.copyWith(emailEnabled: value)),
          ),
        ],
      ),
    );
  }

  void _updatePreference(NotificationPreference next) {
    final draft = _draft!;
    setState(() {
      _draft = NotificationSettings(
        preferences: draft.preferences
            .map((item) => item.type == next.type ? next : item)
            .toList(),
        quietHoursEnabled: draft.quietHoursEnabled,
        quietHoursStart: draft.quietHoursStart,
        quietHoursEnd: draft.quietHoursEnd,
      );
    });
  }

  Future<void> _selectQuietHours() async {
    final draft = _draft!;
    final start = await showTimePicker(
      context: context,
      initialTime: _parseTime(draft.quietHoursStart ?? '22:00'),
    );
    if (start == null || !mounted) return;
    final end = await showTimePicker(
      context: context,
      initialTime: _parseTime(draft.quietHoursEnd ?? '07:00'),
    );
    if (end == null) return;
    setState(() {
      _draft = NotificationSettings(
        preferences: draft.preferences,
        quietHoursEnabled: true,
        quietHoursStart: _formatTime(start),
        quietHoursEnd: _formatTime(end),
      );
    });
  }

  Future<void> _save() async {
    setState(() => _saving = true);
    try {
      final draft = _draft!;
      _draft = await ref
          .read(notificationRepositoryProvider)
          .updateSettings(
            preferences: draft.preferences,
            quietHoursEnabled: draft.quietHoursEnabled,
            quietHoursStart: draft.quietHoursStart,
            quietHoursEnd: draft.quietHoursEnd,
          );
      ref.invalidate(notificationSettingsProvider);
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(const SnackBar(content: Text('알림 설정을 저장했습니다.')));
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  TimeOfDay _parseTime(String value) {
    final parts = value.split(':');
    return TimeOfDay(hour: int.parse(parts[0]), minute: int.parse(parts[1]));
  }

  String _formatTime(TimeOfDay value) =>
      '${value.hour.toString().padLeft(2, '0')}:${value.minute.toString().padLeft(2, '0')}';
  String _label(String type) => switch (type) {
    'APPOINTMENT' => '진료 예약',
    'MEDICATION' => '복약',
    'TEST_RESULT' => '검사 결과',
    'CONSULTATION' => '협진',
    'EMERGENCY' => '응급 안내',
    'SYSTEM' => '시스템',
    _ => '기타',
  };
  IconData _icon(String type) => switch (type) {
    'APPOINTMENT' => Icons.calendar_month,
    'MEDICATION' => Icons.medication,
    'TEST_RESULT' => Icons.description,
    'CONSULTATION' => Icons.groups_2,
    'EMERGENCY' => Icons.emergency,
    _ => Icons.notifications,
  };
}
